import random
from qiskit import QuantumCircuit, transpile
from qiskit_alice_bob_provider import AliceBobLocalProvider

# -----------------------------
# 1) Backend
# -----------------------------

# *** This is the Alice and Bob SIMULATOR, we did not 
# get the api keys yet
provider = AliceBobLocalProvider()
backend = provider.get_backend("EMU:1Q:LESCANNE_2020")

# -----------------------------
# 2) BB84 settings
# -----------------------------
N = 64                  # number of qubits sent
SHOTS = 1               # one shot per transmitted qubit
AVG_NB_PHOTONS = 4      # valid on this backend

# Alice's random raw bits and bases
# basis: 0 = Z basis, 1 = X basis
alice_bits = [random.randint(0, 1) for _ in range(N)]
alice_bases = [random.randint(0, 1) for _ in range(N)]

# Bob's random measurement bases
bob_bases = [random.randint(0, 1) for _ in range(N)]

# -----------------------------
# 3) Build one circuit per signal
# -----------------------------
circuits = []

for i in range(N):
    qc = QuantumCircuit(1, 1)

    bit = alice_bits[i]
    basis = alice_bases[i]

    # Alice prepares one of: |0>, |1>, |+>, |->
    if basis == 0:  # Z basis
        qc.initialize("1" if bit else "0", 0)
    else:           # X basis
        qc.initialize("-" if bit else "+", 0)

    # the delay here can be used for noise
    # qc.delay(1, unit="us")

    # Bob measures in a random basis
    if bob_bases[i] == 0:
        qc.measure(0, 0)
    else:
        qc.measure_x(0, 0)

    circuits.append(transpile(qc, backend))

# -----------------------------
# 4) Run the batch
# -----------------------------
job = backend.run(
    circuits,
    shots=SHOTS,
    average_nb_photons=AVG_NB_PHOTONS,
)

result = job.result()

# Collect Bob's outcomes
bob_results = []
for qc in circuits:
    counts = result.get_counts(qc)
    measured_bit = int(next(iter(counts)))   # "0" or "1"
    bob_results.append(measured_bit)

# -----------------------------
# 5) Sifting: keep only matching bases
# -----------------------------
matching = [i for i in range(N) if alice_bases[i] == bob_bases[i]]

alice_sifted = [alice_bits[i] for i in matching]
bob_sifted = [bob_results[i] for i in matching]

# -----------------------------
# 6) QBER estimation
#    Reveal a random subset publicly
# -----------------------------
if len(alice_sifted) < 2:
    print("Too few sifted bits. Increase N.")
    raise SystemExit

sample_size = max(1, len(alice_sifted) // 2)
sample_idx = set(random.sample(range(len(alice_sifted)), sample_size))

revealed_alice = [alice_sifted[i] for i in sample_idx]
revealed_bob = [bob_sifted[i] for i in sample_idx]

errors = sum(a != b for a, b in zip(revealed_alice, revealed_bob))
qber = errors / sample_size

# Final unrevealed key
final_positions = [i for i in range(len(alice_sifted)) if i not in sample_idx]
alice_key = [alice_sifted[i] for i in final_positions]
bob_key = [bob_sifted[i] for i in final_positions]

# -----------------------------
# 7) Report
# -----------------------------
print("Total transmissions:", N)
print("Sifted key length:", len(alice_sifted))
print("Sample size for QBER:", sample_size)
print("Estimated QBER:", qber)
print("Alice key:", alice_key)
print("Bob key:  ", bob_key)
print("Keys match:", alice_key == bob_key)