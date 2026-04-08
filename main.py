from qiskit_alice_bob_provider import AliceBobProvider
from qiskit import QuantumCircuit, execute

# Connect to the Alice & Bob cloud
provider = AliceBobProvider('YOUR_API_KEY')
backend = provider.get_backend('emulated_cat_qasm_simulator')

# Create a simple circuit
# In Cat Qubits, we often focus on the 'kappa' (coupling) and 'n-bar' (photon count)
qc = QuantumCircuit(1, 1)

# Prepare a state that would normally decohere
qc.x(0) 
qc.measure(0, 0)

# Run on Alice & Bob's specialized Cat Qubit simulator
job = execute(qc, backend, shots=1000)
counts = job.result().get_counts()

print(f"Results showing bit-flip suppression: {counts}")