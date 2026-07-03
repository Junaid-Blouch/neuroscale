import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stable_baselines3 import PPO
from environment.cloud_env import CloudEnv


print("🚀 NeuroScale Final Evaluation Started")

# =========================
# LOAD ENVIRONMENT
# =========================
env = CloudEnv()

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH, "models", "ppo_cloud_agent.zip")

model = PPO.load(MODEL_PATH)

# =========================
# 1️⃣ PPO EVALUATION
# =========================
obs, _ = env.reset()

ppo_total_reward = 0
ppo_overload_count = 0

done = False

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, _, _ = env.step(action)

    ppo_total_reward += reward

    current_load = obs[0]
    capacity = env.active_servers * env.server_capacity

    if current_load > capacity:
        ppo_overload_count += 1

# =========================
# 2️⃣ THRESHOLD EVALUATION
# =========================
env_threshold = CloudEnv()
obs, _ = env_threshold.reset()

threshold_total_reward = 0
threshold_overload_count = 0

done = False

while not done:

    current_load = obs[0]
    capacity = env_threshold.active_servers * env_threshold.server_capacity

    # Threshold logic
    if current_load > capacity * 0.8:
        action = 2
    elif current_load < capacity * 0.3:
        action = 0
    else:
        action = 1

    obs, reward, done, _, _ = env_threshold.step(action)

    threshold_total_reward += reward

    if current_load > capacity:
        threshold_overload_count += 1

# =========================
# PRINT RESULTS
# =========================
print("\n📊 FINAL COMPARISON RESULTS\n")

print("✅ PPO RESULTS:")
print("Total Reward:", round(ppo_total_reward, 2))
print("Overload Count:", ppo_overload_count)

print("\n✅ Threshold RESULTS:")
print("Total Reward:", round(threshold_total_reward, 2))
print("Overload Count:", threshold_overload_count)

print("\n✅ Evaluation Finished")