import pandas as pd
import os
import numpy as np

LOG_PATH = "logs/training_log.csv"

if not os.path.exists(LOG_PATH):
    print("No logs found.")
    exit()

df = pd.read_csv(LOG_PATH)

recent_mean = df["real_load"].tail(500).mean()
overall_mean = df["real_load"].mean()

print("Recent Mean:", recent_mean)
print("Overall Mean:", overall_mean)

if abs(recent_mean - overall_mean) > 0.1:
    print("⚠ Drift detected. Retraining...")
    os.system("python models/lstm_model.py")
    os.system("python rl_agent/train_agent.py")
else:
    print("✅ No significant drift.")