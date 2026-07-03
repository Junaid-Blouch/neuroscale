import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from environment.cloud_env import CloudEnv

print("🚀 Performance-First PPO Training")

env = CloudEnv()
env = Monitor(env)

model = PPO(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=0.0003,
    n_steps=1024,
    batch_size=64,
    gamma=0.99,
)

TOTAL_TIMESTEPS = 150000

model.learn(total_timesteps=TOTAL_TIMESTEPS)

print("✅ PPO Training Completed")

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH, "models", "ppo_cloud_agent")

model.save(MODEL_PATH)

print("✅ Model Saved")