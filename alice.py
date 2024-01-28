import numpy as np
import random
import socket
import pickle
from math import gcd

# def alice_compute_X1(A, H, m):
#     singular = True
#     while singular:
#         t = random.randint(0, m - 1)
#         B = random.choice(H)
#         X1 = np.linalg.matrix_power(A, t % m).dot(B)
#         X1 = X1 % 10000
#         X1_det = int(np.round(np.linalg.det(X1)))
#         if X1_det != 0 and gcd(X1_det, 256) == 1:  # Check if determinant is non-zero
#             singular = False
#     return t, B, X1


def alice_compute_X1(A, H, m):
    t = random.randint(0, m - 1)
    B = random.choice(H)
    X1 = np.linalg.matrix_power(A, t % m).dot(B)
    return t, B, X1

def hill_cipher_encrypt(message, key):

    keys = np.array([[5, 6, 7], [2, 3, 4], [3, 1, 2]])

    while len(message) % 3 != 0:
        message += ' '  # Padding with spaces
    ascii_values = [ord(char) for char in message]
    blocks = [np.array(ascii_values[i:i + 3]).reshape(3,1) for i in range(0, len(ascii_values), 3)]
    encrypted_matrix = np.array([np.dot(keys, block) % 256 for block in blocks])
    
    # Flatten the encrypted_matrix to a single list
    flattened_encrypted_matrix = [num for block in encrypted_matrix for num in block.flatten()]
    # Convert flattened matrix to text
    encrypted_message = ''.join(chr(int(num)) for num in flattened_encrypted_matrix)
    print("Encrpted message: ", encrypted_message)
    return encrypted_matrix

A = np.array([[2, 1, 0], [1, 2, 1], [0, 1, 2]])
m = 100
H = [np.array([[2, 1, 0], [0, 2, 1], [1, 0, 2]]),
     np.array([[3, 1, 2], [1, 3, 1], [2, 1, 3]])]

HOST = '127.0.0.1'
PORT = 65432
exchange_successful = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    
    while not exchange_successful:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            try:
                t, B, X1 = alice_compute_X1(A, H, m)
                # print("Sending X1 to Bob...")
                conn.sendall(pickle.dumps(X1))

                # print("Waiting for X2 from Bob...")
                X2_from_bob = pickle.loads(conn.recv(1024))
                KA = np.linalg.matrix_power(A, t % m).dot(X2_from_bob).dot(B)
                # KA = KA % 10000
                conn.sendall(pickle.dumps(KA))

                result = conn.recv(1024).decode('utf-8')
                if result == 'success':
                    exchange_successful = True
                    print("Shared Secret Key Exchange was successful!")
                    print("Shared Secret: \n", KA)

                    # Encrypt a message using the Hill cipher
                    message_to_encrypt = "Harshit"
                    encrypted_matrix = hill_cipher_encrypt(message_to_encrypt, KA)
                    print("Encrypted Matrix: \n", encrypted_matrix)
                    conn.sendall(pickle.dumps(encrypted_matrix))

            except Exception as e:
                print(f"Error: {e}")
