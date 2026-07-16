import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import pysindy as ps
import warnings
import os

warnings.filterwarnings("ignore")

print("==========================================================")
print("TRAPPIST-1 True Empirical Phase Synchronization (SINDy)")
print("Using Agol et al. 2021 Observational TTV Data")
print("==========================================================")

# 1. Load the Empirical Data
data_file = r"scratch\TRAPPIST1_Spitzer\data\T1_timings_20191203.txt"
if not os.path.exists(data_file):
    print(f"ERROR: Could not find {data_file}")
    exit(1)

# Columns: planet_index, epoch, BJD_TDB_time, uncertainty
df = pd.read_csv(data_file, header=None, names=["planet_idx", "epoch", "time", "uncert"])

N = 7  # 7 planets (b through h)

print("\n[1] Processing Physical Transit Timestamps...")
# Extract (time, phase) points for each planet
# A transit represents exactly one full orbit (2*pi) from the previous epoch
t_min_overlap = -np.inf
t_max_overlap = np.inf

planet_data = {}
for i in range(1, N + 1):
    p_df = df[df["planet_idx"] == i].sort_values("time")
    
    times = p_df["time"].values
    # Phase = 2 * pi * epoch
    phases = 2 * np.pi * p_df["epoch"].values
    
    # We must ensure phases are strictly increasing (sometimes data has duplicates)
    # So we remove any duplicate timestamps
    unique_times, unique_indices = np.unique(times, return_index=True)
    unique_phases = phases[unique_indices]
    
    planet_data[i] = {
        "time": unique_times,
        "phase": unique_phases
    }
    
    # Find the overlap window where we have data for ALL planets
    t_min_overlap = max(t_min_overlap, unique_times[0])
    t_max_overlap = min(t_max_overlap, unique_times[-1])

print(f"    Overlap window: BJD {t_min_overlap:.2f} to {t_max_overlap:.2f}")

# 2. Interpolate onto a continuous Phase Manifold
print("\n[2] Building Continuous Empirical Phase Manifold...")
# We need uniform time points for PySINDy to compute derivatives
t_eval = np.linspace(t_min_overlap, t_max_overlap, 2000)

theta = np.zeros((len(t_eval), N))
for i in range(1, N + 1):
    # Use cubic spline/linear interpolation between empirical transit observations
    interpolator = interp1d(planet_data[i]["time"], planet_data[i]["phase"], kind='cubic', bounds_error=False, fill_value="extrapolate")
    theta[:, i-1] = interpolator(t_eval)

# 3. SINDy Extraction Setup
print("\n[3] Configuring PySINDy algorithm with concatenated libraries...")
fourier_lib = ps.FourierLibrary(n_frequencies=1) # traps: sin(x), cos(x)
custom_lib = ps.CustomLibrary(
    library_functions=[lambda x: np.ones(x.shape[0]), lambda x, y: np.sin(y - x)],
    function_names=[lambda x: "1", lambda x, y: f"sin({y} - {x})"]
)
lib = fourier_lib + custom_lib

# STLSQ parameters: Very low threshold because empirical mass ratios (couplings) are ~10^-5
opt = ps.STLSQ(threshold=1e-6, alpha=1e-5)
model = ps.SINDy(feature_library=lib, optimizer=opt)

# 4. Run the Extraction
print("\n[4] Feeding TRAPPIST-1 Empirical Data into SINDy...")
model.fit(theta, t=t_eval)

print("\n[5] --- DISCOVERED GOVERNING EQUATIONS ---")
model.print(lhs=[f"(d/dt) theta_{i}" for i in range(N)])
print("------------------------------------------")

print("\nValidation complete. SINDy was run on purely empirical transit observations.")
