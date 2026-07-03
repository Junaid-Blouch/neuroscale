import os
import math
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from torch.utils.data import DataLoader, TensorDataset
from scipy import stats


# =========================
# PATHS
# =========================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_PATH, "data", "real_workload.csv")
MODEL_PATH = os.path.join(BASE_PATH, "models", "trained_lstm.pth")
SCALER_PATH = os.path.join(BASE_PATH, "models", "workload_scaler.save")

print("🚀 NeuroScale Optimized Training (8GB RAM Safe)")

# =========================
# LOAD DATA
# =========================
df_raw = pd.read_csv(DATA_PATH, header=None)
df = pd.DataFrame()
df["workload"] = df_raw.iloc[:, 5]

print("Original size:", len(df))

# =========================
# CLEANING
# =========================
df.dropna(inplace=True)
df["workload"] = pd.to_numeric(df["workload"], errors="coerce")
df.dropna(inplace=True)
df = df[(df["workload"] >= 0) & (df["workload"] <= 1)]

# =========================
# OUTLIER REMOVAL
# =========================
z_scores = np.abs(stats.zscore(df["workload"]))
df = df[z_scores < 3]

print("After outlier removal:", len(df))

# =========================
# LIMIT DATA FOR RAM
# =========================
MAX_ROWS = 80000
df = df.iloc[:MAX_ROWS]
print("After limiting rows:", len(df))

# =========================
# SMOOTHING
# =========================
df["workload"] = df["workload"].rolling(window=5).mean()
df.dropna(inplace=True)

# =========================
# FEATURE ENGINEERING
# =========================
df["rolling_mean"] = df["workload"].rolling(window=20).mean()
df["rolling_std"] = df["workload"].rolling(window=20).std()
df.dropna(inplace=True)

features = df[["workload", "rolling_mean", "rolling_std"]].values

print("Final dataset size:", len(features))

# =========================
# SCALING
# =========================
scaler = MinMaxScaler()
features_scaled = scaler.fit_transform(features)
joblib.dump(scaler, SCALER_PATH)

# =========================
# SEQUENCE CREATION
# =========================
def create_sequences(data, seq_length=30):
    X, y = [], []
    for i in range(len(data)-seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length][0])
    return np.array(X), np.array(y)

SEQ_LENGTH = 30
X, y = create_sequences(features_scaled, SEQ_LENGTH)

train_size = int(len(X) * 0.8)

X_train = torch.tensor(X[:train_size], dtype=torch.float32)
y_train = torch.tensor(y[:train_size], dtype=torch.float32)

X_test = torch.tensor(X[train_size:], dtype=torch.float32)
y_test = torch.tensor(y[train_size:], dtype=torch.float32)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# =========================
# LSTM MODEL
# =========================
class LSTMModel(nn.Module):
    def __init__(self):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size=3, hidden_size=64, num_layers=1, batch_first=True)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(64, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.dropout(out[:, -1, :])
        return self.fc(out)

model = LSTMModel()

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

train_dataset = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

# =========================
# TRAINING
# =========================
EPOCHS = 25

print("🧠 Training Started...")

for epoch in range(EPOCHS):
    total_loss = 0

    for batch_X, batch_y in train_loader:
        outputs = model(batch_X)
        loss = criterion(outputs.squeeze(), batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss/len(train_loader):.6f}")

print("✅ Training Completed")

torch.save(model.state_dict(), MODEL_PATH)

# =========================
# EVALUATION
# =========================
model.eval()
with torch.no_grad():
    predictions = model(X_test)

predictions_full = np.zeros((len(predictions), 3))
predictions_full[:,0] = predictions.numpy().flatten()

actual_full = np.zeros((len(y_test), 3))
actual_full[:,0] = y_test.numpy()

predictions = scaler.inverse_transform(predictions_full)[:,0]
actual = scaler.inverse_transform(actual_full)[:,0]

mae = mean_absolute_error(actual, predictions)
rmse = math.sqrt(mean_squared_error(actual, predictions))

print("\n📊 Evaluation Results")
print(f"MAE  : {mae:.6f}")
print(f"RMSE : {rmse:.6f}")

plt.figure(figsize=(10,5))
plt.plot(actual[:300], label="Actual")
plt.plot(predictions[:300], label="Predicted")
plt.legend()
plt.title("NeuroScale Optimized Prediction")
plt.show()

print("✅ NeuroScale Training Finished Successfully")