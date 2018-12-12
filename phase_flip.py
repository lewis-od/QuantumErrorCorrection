from qutip import *
import random

# Logical qubit to encode
psi = (basis(2, 0) + basis(2, 1)).unit()
# Physical qubits
qubit1, qubit2 = basis(2, 0), basis(2, 0)
# Full state of system
state = tensor(psi, qubit1, qubit2)

cnot01 = cnot(N=3, control=0, target=1)
cnot02 = cnot(N=3, control=0, target=2)

# Perform encoding
state = cnot02 * cnot01 * state # Encode logical -> physical
state = snot(3, 0) * snot(3, 1) * snot(3, 2) * state # Convert to +,- basis

# Syndrome measurements
A = tensor(sigmax(), sigmax(), qeye(2))
B = tensor(qeye(2), sigmax(), sigmax())

# Change phase of random qubit
phase_ops = [qeye(2), qeye(2), sigmaz()]
random.shuffle(phase_ops)
print("Changing phase of qubit {}".format(phase_ops.index(sigmaz())))
phase = tensor(phase_ops)
state = phase * state

# Perform syndrome measurement
a = 1 if (A * state) == state else -1
b = 1 if (B * state) == state else -1

# Perform error correction
correction = None
if a == 1 and b == 1:
  # No error
  correction = tensor([qeye(2)]*3)
  print("No error")
elif a == 1 and b == -1:
  correction = tensor(qeye(2), qeye(2), sigmaz())
  print("Error detected: qubit 2 flipped")
elif a == -1 and b == 1:
  correction = tensor(sigmaz(), qeye(2), qeye(2))
  print("Error detected: qubit 0 flipped")
else:
  correction = tensor(qeye(2), sigmaz(), qeye(2))
  print("Error detected: qubit 1 flipped")

state = correction * state

# Decode qubits
state = snot(3, 0) * snot(3, 1) * snot(3, 2) * state # Convert to 0,1 basis
state = cnot01 * cnot02 * state # Decode physical -> logical
logical = state.ptrace(0)

# Check qubit was decoded correctly
if logical == ket2dm(psi):
    print("Error successfully corrected")
else:
    print("Error correction failed")
