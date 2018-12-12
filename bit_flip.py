from qutip import *
import random

# Logical qubit to encode
psi = (basis(2, 0) + basis(2, 1)).unit()
# Physical qubits
qubit1, qubit2 = basis(2, 0), basis(2, 0)

state = tensor(psi, qubit1, qubit2)

cnot01 = cnot(N=3, control=0, target=1)
cnot02 = cnot(N=3, control=0, target=2)

# Perform encoding
state = cnot02 * cnot01 * state

# Syndrome measurements
A = tensor(sigmaz(), sigmaz(), qeye(2))
B = tensor(qeye(2), sigmaz(), sigmaz())

# Flip a random qubit
flip_ops = [qeye(2), qeye(2), sigmax()]
random.shuffle(flip_ops)
print("Flipping qubit {}".format(flip_ops.index(sigmax())))
flip = tensor(flip_ops)
state = flip * state

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
  correction = tensor(qeye(2), qeye(2), sigmax())
  print("Error detected: qubit 2 flipped")
elif a == -1 and b == 1:
  correction = tensor(sigmax(), qeye(2), qeye(2))
  print("Error detected: qubit 0 flipped")
else:
  correction = tensor(qeye(2), sigmax(), qeye(2))
  print("Error detected: qubit 1 flipped")

state = correction * state

# Decode physical -> logical
state = cnot01 * cnot02 * state
logical = state.ptrace(0)

# Check qubit was decoded correctly
if logical == ket2dm(psi):
    print("Error successfully corrected")
else:
    print("Error correction failed")
