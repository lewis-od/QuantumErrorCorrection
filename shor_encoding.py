from qutip import *

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

# TODO: Cause random bit-flip and phase-flip errors
# TODO: Correct errors

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
