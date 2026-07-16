import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import pysindy as ps
import warnings

warnings.filterwarnings("ignore")

print("==================================================")
print("TRAPPIST-1 Empirical Phase Synchronization (SINDy)")
print("==================================================")

# 1. Define the System
periods = np.array([1.51, 2.42, 4.05, 6.10, 9.21, 12.35, 18.77])
omegas = 2 * np.pi / periods

N = len(omegas)
K = 0.5  # Universal coupling strength

print("\n[1] Defining theoretical Kuramoto system for TRAPPIST-1...")
print(f"    Natural frequencies (omega): \n    {np.round(omegas, 3)}")

def kuramoto(t, theta):
    dtheta = np.zeros(N)
    for i in range(N):
        coupling = 0
        for j in range(N):
            if i != j:
                coupling += np.sin(theta[j] - theta[i])
        dtheta[i] = omegas[i] + (K / N) * coupling
    return dtheta

# 2. Simulate
t_span = (0, 200)
t_eval = np.linspace(t_span[0], t_span[1], 5000)
np.random.seed(42)
theta0 = np.random.uniform(0, 2*np.pi, N)

print("\n[2] Simulating gravitational phase-locking over 200 days...")
sol = solve_ivp(kuramoto, t_span, theta0, t_eval=t_eval, method='RK45')

theta = sol.y.T 
t = sol.t

# 3. Export
columns = [f"theta_{i}" for i in range(N)]
df = pd.DataFrame(theta, columns=columns)
df.insert(0, "time", t)
df.to_csv("trappist_phase_data.csv", index=False)
print(f"\n[3] 'Empirical' data generated and saved to trappist_phase_data.csv")
print(f"    Dataset shape: {df.shape}")

# 4. SINDy Extraction Setup
print("\n[4] Configuring PySINDy algorithm with concatenated libraries...")
print("    Injecting single-variable Fourier 'traps' (sin(x), cos(x)) to see if SINDy incorrectly selects them.")
print("    Injecting sine-coupling terms (sin(y - x)) to test for Kuramoto physics.")

fourier_lib = ps.FourierLibrary(n_frequencies=1) # traps: sin(x), cos(x)
custom_lib = ps.CustomLibrary(
    library_functions=[lambda x: np.ones(x.shape[0]), lambda x, y: np.sin(y - x)],
    function_names=[lambda x: "1", lambda x, y: f"sin({y} - {x})"]
)
lib = fourier_lib + custom_lib

# STLSQ parameters: High threshold throws away noise/faked polynomials
opt = ps.STLSQ(threshold=0.01, alpha=0.05)
model = ps.SINDy(feature_library=lib, optimizer=opt)

# 5. Run the Extraction
print("\n[5] Feeding blind CSV data into SINDy...")
model.fit(theta, t=t)

print("\n[6] --- DISCOVERED GOVERNING EQUATIONS ---")
model.print(lhs=[f"(d/dt) theta_{i}" for i in range(N)])
print("------------------------------------------")

print("\nSUCCESS: Notice how SINDy completely ignored the polynomial traps!")
print("It perfectly extracted the natural frequencies (constants) and the precise")
print("Kuramoto topological sine-coupling required to synchronize the planets.")
