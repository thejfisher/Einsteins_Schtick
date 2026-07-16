import numpy as np
import pandas as pd
import pysindy as ps
from scipy.integrate import odeint

# ---------------------------------------------------------
# 1. Simulate Metronome Data (Kuramoto Weak Coupling)
# ---------------------------------------------------------
def metronome_dynamics(theta, t, omega, K):
    N = len(theta)
    dtheta_dt = np.zeros(N)
    for i in range(N):
        coupling = 0
        for j in range(N):
            if i != j:
                coupling += np.sin(theta[j] - theta[i])
        dtheta_dt[i] = omega[i] + (K / N) * coupling
    return dtheta_dt

np.random.seed(42)
n_metronomes = 5
t = np.linspace(0, 50, 5000)

# Natural frequencies (slightly different)
omega = np.random.uniform(1.0, 1.5, n_metronomes)
# Coupling strength
K = 0.5 

# Initial phases
theta0 = np.random.uniform(0, 2 * np.pi, n_metronomes)

print("Simulating Coupled Metronomes (Kuramoto Mechanics)...")
theta_data = odeint(metronome_dynamics, theta0, t, args=(omega, K))

# Save to CSV
csv_filename = "metronome_phase_data.csv"
columns = [f"theta_{i}" for i in range(n_metronomes)]
df = pd.DataFrame(theta_data, columns=columns)
df['time'] = t
df.to_csv(csv_filename, index=False)
print(f"Data saved to {csv_filename}")

# ---------------------------------------------------------
# 2. PySINDy Extraction (Blind Equation Discovery)
# ---------------------------------------------------------
print("Running SINDy to extract topological coupling...")

# Build a Fourier library to capture sine/cosine couplings
fourier_library = ps.FourierLibrary(n_frequencies=1)
custom_lib = ps.CustomLibrary(
    library_functions=[lambda x: np.ones(x.shape[0]), lambda x, y: np.sin(y - x)],
    function_names=[lambda x: "1", lambda x, y: f"sin({y} - {x})"]
)
custom_library = fourier_library + custom_lib

# We tell SINDy to look for equations that explain the velocity of the phases
optimizer = ps.STLSQ(threshold=0.01, alpha=0.05)

model = ps.SINDy(
    optimizer=optimizer,
    feature_library=custom_library
)

# Fit SINDy to the phase data (dt is derived from the time array)
model.fit(theta_data, t=t)

print("\n--- SINDy Discovered Equations for the Metronomes ---")
model.print(lhs=[f"(d/dt) theta_{i}" for i in range(n_metronomes)])
print("-----------------------------------------------------")
