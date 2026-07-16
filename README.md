# TRAPPIST-1 Algorithmic Symmetry

This repository contains the code and methodology used to demonstrate algorithmic symmetry across physical systems, specifically focusing on the orbital resonance of the TRAPPIST-1 exoplanet system.

We utilize the **SINDy (Sparse Identification of Nonlinear Dynamics)** algorithm to show that complex phase-synchronization mechanics—specifically the Kuramoto pairwise topological coupling limit $\sin(\theta_j - \theta_i)$—can be extracted directly from both synthetic calibration models and raw, physical astrophysics observations.

## Files Included

- **`trappist_calibration.py`**: A synthetic mathematical sanity check. Generates 7 bodies moving at the TRAPPIST-1 orbital frequencies and forces them to interact using Kuramoto mechanics. Proves that the SINDy pipeline is correctly tuned to reject polynomial traps and reconstruct the Kuramoto formula.
- **`trappist_empirical.py`**: The True Empirical Extraction script. Ingests raw Transit Timing Variations (TTVs) and applies a cubic spline interpolation to generate a continuous phase manifold, which is then fed into SINDy to detect the underlying mathematical topology.
- **`T1_timings_20191203.txt`**: The raw empirical dataset containing 447 physical, observed planetary transit timestamps of TRAPPIST-1 (in BJD), sourced from the exhaustive *Agol et al. (2021)* Spitzer/K2 observation campaign.
- **`manuscript.md`**: The draft manuscript detailing the methodology, results, and the philosophical argument for "Algorithmic Symmetry."

## Methodology Note

Because physical gravitational coupling is incredibly weak (planet-to-star mass ratios are $\sim 10^{-5}$), the resulting phase deviances are microscopic. To capture these dynamics in the empirical data, we lowered the SINDy STLSQ sparse regression threshold to $10^{-6}$. Additionally, the cubic spline interpolation introduces a mathematical smoothing assumption into the raw data, highlighting an algorithmic preference rather than claiming absolute physical universality.
