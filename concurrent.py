import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd

# Data
m_values = np.array([1, 2, 3, 4, 5, 6, 7])
data = np.array([
    [394, 394, 391, 384.9, 383.66, 361.59, 347.26],
    [398, 395, 393, 387,   377.85, 357,    345.42],
    [395, 393, 390, 388.29,379.3,  355.07, 336.5 ]
])
tp_mean = data.mean(axis=0)

# Model
def rational(m, a0, a1, a2, b1):
    return (a0 + a1 * m + a2 * m**2) / (1 + b1 * m)

# Fit
popt_rat, _ = curve_fit(rational, m_values, tp_mean, p0=(1, 1, 0, 0.1))
tp_pred = rational(m_values, *popt_rat)
percent_errors = np.abs((tp_pred - tp_mean) / tp_mean) * 100

# Output parameters
print("Fitted parameters:")
print(f"a0 = {popt_rat[0]:.4f}")
print(f"a1 = {popt_rat[1]:.4f}")
print(f"a2 = {popt_rat[2]:.4f}")
print(f"b1 = {popt_rat[3]:.4f}\n")

# Output predictions and errors
print(f"{'Hosts':>5} | {'Measured':>9} | {'Predicted':>9} | {'Error (%)':>10}")
print("-" * 40)
for m, tm, tp, err in zip(m_values, tp_mean, tp_pred, percent_errors):
    print(f"{m:5d} | {tm:9.2f} | {tp:9.2f} | {err:10.2f}")

# Save to CSV
df = pd.DataFrame({
    'Hosts': m_values,
    'Measured': tp_mean,
    'Predicted': tp_pred,
    'Error (%)': percent_errors
})
df.to_csv('rational_fit_results.csv', index=False)
print("\nSaved results to 'rational_fit_results.csv'.")

# Plot
plt.figure(figsize=(10,6))
plt.scatter(m_values, tp_mean, label='Measured mean', color='#333333', s=80)
plt.plot(np.linspace(1, 7, 200), rational(np.linspace(1, 7, 200), *popt_rat),
         label='Rational fit', color='#1f77b4', linewidth=2.5)

plt.xlabel('Number of Hosts', fontsize=16)
plt.ylabel('Throughput', fontsize=16)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.legend(fontsize=18, loc='upper right')
plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()
