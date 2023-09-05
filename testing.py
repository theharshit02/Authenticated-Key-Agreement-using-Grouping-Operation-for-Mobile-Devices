import numpy as np
import random

# Function to calculate the shared secret
def calculate_shared_secret(A, t, X2, B, s, X1, C, m):
    # Alice computes K_A
    KA = np.linalg.matrix_power(A, t % m).dot(X2).dot(B)
    # Bob computes K_B
    KB = np.linalg.matrix_power(A, s % m).dot(X1).dot(C)
    # Take modulo m to prevent integer overflow
    # KA %= m
    # KB %= m
    # Verify if both shared secrets are equal
    if np.array_equal(KA, KB) and not np.all(KA == 0):
        return KA, True
    else:
        return KA, False

# Initialize variables
A = np.array([[2, 1, 0], [1, 2, 1], [0, 1, 2]])  # Public constant A in G (3x3 matrix)
m = 100  # Large positive integer, public domain

# Elements in H, public domain (3x3 matrices)
H = [
    np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    np.array([[2, 1, 0], [0, 2, 1], [1, 0, 2]]),
    np.array([[3, 1, 2], [1, 3, 1], [2, 1, 3]])
]

while True:
    # Alice selects a secret integer t in Fm
    t = random.randint(0, m - 1)

    # Ensure that B does not commute with A
    while True:
        B = random.choice(H)
        if not np.array_equal(np.linalg.matrix_power(A, t % m).dot(B), B.dot(np.linalg.matrix_power(A, t % m))):
            break

    # Bob selects a secret integer s in Fm
    s = random.randint(0, m - 1)

    # Ensure that C does not commute with A
    while True:
        C = random.choice(H)
        if not np.array_equal(np.linalg.matrix_power(A, s % m).dot(C), C.dot(np.linalg.matrix_power(A, s % m))):
            break

    # Alice computes X1 and sends it to Bob
    X1 = np.linalg.matrix_power(A, t % m).dot(B)

    # Bob computes X2 and sends it to Alice
    X2 = np.linalg.matrix_power(A, s % m).dot(C)

    # Calculate the shared secret
    shared_secret, is_match = calculate_shared_secret(A, t, X2, B, s, X1, C, m)



    # Verify if the shared secret key is not a zero matrix
    if is_match:
        print("The shared secret keys match!")
        print(f"KA:{shared_secret}")
        print(f"KB:{shared_secret}")
        break

# Display the results
print(f"Public constant A:\n{A}")
print(f"Public domain m: {m}")
print(f"Public domain H: {H}")
print(f"Alice's secret integer t: {t}")
print(f"Bob's secret integer s: {s}")
print(f"Alice's secret element B:\n{B}")
print(f"Bob's secret element C:\n{C}")
print(f"Alice's computed X1:\n{X1}")
print(f"Bob's computed X2:\n{X2}")