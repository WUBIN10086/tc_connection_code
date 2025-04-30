import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from math import sqrt
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score

# ========= Load Data =========
Pd = pd.read_csv("all_rsss.csv", header=None).iloc[:, 0].values
Sh = pd.read_csv("all_thr.csv", header=None).iloc[:, 0].values

assert len(Pd) == len(Sh), "Pd and Sh must have the same length"

X = Pd.reshape(-1, 1)
y = Sh

# ========= SVR Model =========
svr_model = SVR(kernel='rbf', C=100, epsilon=0.5)
svr_model.fit(X, y)
y_pred_svr = svr_model.predict(X)

# ========= Evaluation =========
print("\n--- SVR Results ---")
print(f"RMSE: {sqrt(mean_squared_error(y, y_pred_svr)):.4f}")
print(f"R2:   {r2_score(y, y_pred_svr):.4f}")

# ========= Visualization =========
x_range = np.linspace(min(Pd), max(Pd), 200).reshape(-1, 1)
svr_curve = svr_model.predict(x_range)

plt.figure(figsize=(8, 5))
plt.scatter(Pd, Sh, label="Measured Sh", color='black', s=40)
plt.plot(x_range, svr_curve, label="SVR Fit", color='blue')
plt.xlabel("RSS (Pd)")
plt.ylabel("Throughput (Sh)")
plt.title("SVR Regression Fit")
plt.legend()
plt.grid(True)
plt.tight_layout()
os.makedirs("output", exist_ok=True)
plt.savefig("output/svr_fit.png")
plt.show()

# ========= Save Predictions =========
pd.DataFrame({
    "RSS": Pd,
    "Measured_Sh": Sh,
    "SVR_Predicted_Sh": y_pred_svr
}).to_csv("output/svr_predictions.csv", index=False)

print("\n=== All SVR results saved in 'output/' folder ===")
