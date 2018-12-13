from qutip import *
import random
import copy

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
# TODO: Make this so that bit-flip and phase-flip can be on different qubits
error_ops = [qeye(2)]*8 + [sigmaz()*sigmax()]
random.shuffle(error_ops)
error_qubit = error_ops.index(sigmaz()*sigmax())
print("Causing error on qubit {}".format(error_qubit))
error_op = tensor(error_ops)
state = error_op * state

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
        print("No error on block {}".format(n))
    elif a == 1 and b == -1:
        correction[3*n+2] = sigmax()
        print("Error detected: bit flip on qubit 2 of block {}".format(n))
    elif a == -1 and b == 1:
        correction[3*n] = sigmax()
        print("Error detected: bit flip on qubit 0 of block {}".format(n))
    else: # a == b == -1
        correction[3*n+1] = sigmax()
        print("Error detected: bit flip on qubit 1 of block {}".format(n))
    # Apply correction
    state = tensor(correction) * state

# TODO: Correct phase flip error

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
