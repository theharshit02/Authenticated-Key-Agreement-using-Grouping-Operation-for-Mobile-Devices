import numpy as np
import random
import socket
import pickle
from math import gcd

# Function to compute the modular inverse of a matrix
def mod_inv_matrix(A):
    # Fixed modulus for modular inverse calculation
    fixed_modulus = 256

    def modular_inverse(n, modulus):
        g, x, y = extended_gcd(n, modulus)
        if g != 1:
            return None
        return x % modulus

    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        else:
            gcd, x, y = extended_gcd(b % a, a)
            return gcd, y - (b // a) * x, x

    det = int(np.round(np.linalg.det(A)))
    det_inv = modular_inverse(det, fixed_modulus)
    if det_inv is None:
        raise ValueError("The modular inverse of the determinant does not exist.")

    cofactors = np.zeros_like(A)
    for r in range(A.shape[0]):
        for c in range(A.shape[1]):
            minor = A[np.array(list(range(r)) + list(range(r+1, A.shape[0])))[:, np.newaxis],
                      np.array(list(range(c)) + list(range(c+1, A.shape[1])))]
            cofactors[r, c] = (-1) ** (r + c) * int(np.round(np.linalg.det(minor)))

    adjugate = cofactors.T
    A_inv = (det_inv * adjugate) % fixed_modulus
    return A_inv

def matrix_to_text(matrix):
    text = ''
    for row in matrix:
        for num in row:
            text += chr(int(num) % 256)
    return text

# def bob_compute_X2(A, H, m):
#     singular = True
#     while singular:
#         s = random.randint(0, m - 1)
#         C = random.choice(H)
#         X2 = np.linalg.matrix_power(A, s % m).dot(C)
#         X2 = X2 % 10000
#         X2_det = int(np.round(np.linalg.det(X2)))
#         if X2_det != 0 and gcd(X2_det, 256) == 1:
#             singular = False
#     return s, C, X2

def bob_compute_X2(A, H, m):
    s = random.randint(0, m - 1)
    C = random.choice(H)
    X2 = np.linalg.matrix_power(A, s % m).dot(C)
    return s, C, X2

def keys_match_and_non_zero(KA, KB):
    return np.array_equal(KA, KB) and not np.all(KA == 0)

def decrypt_blocks(encrypted_blocks, KB):
    decrypted_text = ''
    KB_inv = mod_inv_matrix(KB)
    for block in encrypted_blocks:
        decrypted_block = np.dot(KB_inv, block) % 256
        decrypted_text += matrix_to_text(decrypted_block)
    return decrypted_text

# Define the matrix A, modulus m for Bob's code, and set of matrices H
A = np.array([[2, 1, 0], [1, 2, 1], [0, 1, 2]])
m = 100  # Modulus for Bob's part of the code
H = [np.array([[2, 1, 0], [0, 2, 1], [1, 0, 2]]),
     np.array([[3, 1, 2], [1, 3, 1], [2, 1, 3]])]

HOST = '127.0.0.1'
PORT = 65432
success = False

while not success:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            
            # print("Receiving X1 from Alice...")
            X1_from_alice = pickle.loads(s.recv(1024))
            
            s_value, C, X2 = bob_compute_X2(A, H, m)
            # print("Sending X2 to Alice...")
            s.sendall(pickle.dumps(X2))
            
            KB = np.linalg.matrix_power(A, s_value % m).dot(X1_from_alice).dot(C)
            # KB = KB % 10000
            KA_from_alice = pickle.loads(s.recv(1024))

            if keys_match_and_non_zero(KA_from_alice, KB):
                s.sendall(b'success')
                success = True

                print("Shared Secret Key Exchange was successful!")
                print("Shared Secret: \n", KB)


                # Receive the encrypted blocks
                encrypted_blocks = pickle.loads(s.recv(1024))
                print("Received Encrypted Matrix: \n", encrypted_blocks)

                # Decrypt the encrypted blocks
                keyzzz = np.array([[5, 6, 7], [2, 3, 4], [3, 1, 2]])
                decrypted_text = decrypt_blocks(encrypted_blocks, keyzzz)
                print("Decrypted text: \n", decrypted_text)

            else:
                print("Key Exchange failed. Trying again...")
                s.sendall(b'failure')
        except Exception as e:
            print(f"Error: {e}")
