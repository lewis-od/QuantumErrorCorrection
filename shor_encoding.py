from qutip import *
import random

# Logical state to encode
psi = (basis(2, 0) + basis(2, 1)).unit()
# Will encode 1 logical qubit as 9 physical qubits
physical = [basis(2, 0)]*8

# Full multipartite state of system
state = tensor([psi] + physical)

# First encode qubit 0 into qubits 0, 3, and 6 using phase-flip code
state = cnot(9, target=3, control=0) * cnot(9, target=6, control=0) * state
state = snot(9, 0) * snot(9, 3) * snot(9, 6) * state

# Encode qubit 0 using bit-flip code
state = cnot(9, target=1, control=0) * cnot(9, target=2, control=0) * state
# Encode qubit 3
state = cnot(9, target=4, control=3) * cnot(9, target=5, control=3) * state
# Encode qubit 6
state = cnot(9, target=7, control=6) * cnot(9, target=8, control=6) * state

# Cause random bit-flip and phase-flip error
error_op = [qeye(2)]*9
phase_qubit = random.randint(0, 8) # qubit to phase-flip
print("Phase-flippping qubit {}".format(phase_qubit))
error_op[phase_qubit] *= sigmaz()

flip_qubit = random.randint(0, 8) # qubit to bit-flip
print("Bit-flipping qubit {}".format(flip_qubit))
error_op[flip_qubit] *= sigmax()

state = tensor(error_op) * state

# Correct bit-flip errors - can correct one per block of 3
# Define block-level operations
I3 = tensor([qeye(2)]*3) # Identity on 3 qubits
# Syndrome measurement on each block of 3
A = tensor(sigmaz(), sigmaz(), qeye(2))
B = tensor(qeye(2), sigmaz(), sigmaz())

# Perform bit-flip error correction on each block of 3
for n in range(3): # n labels which block we're checking
    # Contruct syndrome measurement
    An = [I3] * 3
    An[n] = A
    Bn = [I3] * 3
    Bn[n] = B
    An, Bn = tensor(An), tensor(Bn)
    # Perform measurement
    a = 1 if An * state == state else -1
    b = 1 if Bn * state == state else -1
    # Determine correction
    correction = [qeye(2)]*9
    if a == 1 and b == 1:
        print("No bit-flip error on block {}".format(n))
    elif a == 1 and b == -1:
        correction[3*n+2] = sigmax()
        print("Error detected: bit-flip on qubit 2 of block {}".format(n))
    elif a == -1 and b == 1:
        correction[3*n] = sigmax()
        print("Error detected: bit-flip on qubit 0 of block {}".format(n))
    else: # a == b == -1
        correction[3*n+1] = sigmax()
        print("Error detected: bit-flip on qubit 1 of block {}".format(n))
    # Apply correction
    state = tensor(correction) * state

# Detect phase-flip error
sigmax3 = tensor([sigmax()] * 3) # Block level sigmax
measurements = [0, 0, 0]
for n in range(3):
    X = [I3, I3, I3]
    X[n] = sigmax3 # sigmax on block n
    X = tensor(X)
    measurements[n] = X * state

# Correct phase-flip error
sigmaz3 = tensor([sigmaz()] * 3) # Block level sigmaz
correction = [I3, I3, I3]
if measurements[0] == measurements[1]:
    if measurements[1] == measurements[2]:
        print("No phase-flip error")
    else:
        print("Error detected: phase-flip on block 2")
        correction[2] = sigmaz3
else:
    if measurements[0] == measurements[2]:
        print("Error detected: phase-flip on block 1")
        correction[1] = sigmaz3
    else:
        print("Error detected: phase-flip on block 0")
        correction[0] = sigmaz3
state = tensor(correction) * state

# Decode bit-flip code on each group of 3 qubits
state = cnot(9, target=2, control=0) * cnot(9, target=1, control=0) * state
state = cnot(9, target=5, control=3) * cnot(9, target=4, control=3) * state
state = cnot(9, target=8, control=6) * cnot(9, target=7, control=6) * state

# Decode phase-flip code on qubits 0,3,6
state = snot(9, 0) * snot(9, 3) * snot(9, 6) * state
state = cnot(9, target=6, control=0) * cnot(9, target=3, control=0) * state

if (state.ptrace(0) == ket2dm(psi)):
    print("Decoding successful")
else:
    print("Error decoding")
