import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_workload_data(time_steps=2000):
    np.random.seed(42)

    t = np.arange(time_steps)

    # Daily traffic pattern (sin wave)
    daily_pattern = 50 + 30 * np.sin(2 * np.pi * t / 200)

    # Random noise
    noise = np.random.normal(0, 5, time_steps)

    # Sudden traffic spikes
    spikes = np.zeros(time_steps)
    spike_indices = np.random.choice(time_steps, size=20, replace=False)
    spikes[spike_indices] = np.random.uniform(20, 50, size=20)

    workload = daily_pattern + noise + spikes
    workload = np.maximum(workload, 0)

    return workload


if __name__ == "__main__":
    workload = generate_workload_data()

    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame({"workload": workload})
    df.to_csv("data/workload.csv", index=False)

    print("✅ Workload data generated and saved!")

    plt.figure(figsize=(10,5))
    plt.plot(workload)
    plt.title("Simulated Cloud Workload")
    plt.xlabel("Time")
    plt.ylabel("Load")
    plt.show()