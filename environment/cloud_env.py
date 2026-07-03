import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import os
import torch
import torch.nn as nn
import joblib


class LSTMModel(nn.Module):
    def __init__(self):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(3, 64, 1, batch_first=True)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(64, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.dropout(out[:, -1, :])
        return self.fc(out)


class CloudEnv(gym.Env):

    def __init__(self):
        super(CloudEnv, self).__init__()

        BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DATA_PATH = os.path.join(BASE_PATH, "data", "real_workload.csv")
        MODEL_PATH = os.path.join(BASE_PATH, "models", "trained_lstm.pth")
        SCALER_PATH = os.path.join(BASE_PATH, "models", "workload_scaler.save")

        df_raw = pd.read_csv(DATA_PATH, header=None)
        workload = df_raw.iloc[:,5].values[:50000]
        workload = (workload - workload.min()) / (workload.max() - workload.min())
        self.workload = workload

        self.scaler = joblib.load(SCALER_PATH)

        self.lstm_model = LSTMModel()
        self.lstm_model.load_state_dict(torch.load(MODEL_PATH))
        self.lstm_model.eval()

        self.max_servers = 20
        self.min_servers = 1
        self.server_capacity = 1.0 / self.max_servers

        # ✅ Adaptive reward weights
        self.cost_weight = 0.04
        self.overload_weight = 70
        self.target_overload_rate = 0.01

        self.total_steps = 0
        self.overload_count = 0

        self.action_space = spaces.Discrete(3)

        self.observation_space = spaces.Box(
            low=np.array([0,0,-1,self.min_servers], dtype=np.float32),
            high=np.array([1,1,1,self.max_servers], dtype=np.float32),
            dtype=np.float32
        )

        self.episode_length = 2000
        self.reset()

    def reset(self, seed=None, options=None):
        self.current_step = 60
        self.active_servers = 5
        self.total_steps = 0
        self.overload_count = 0
        return self._get_state(), {}

    def _predict_with_lstm(self):
        window = self.workload[self.current_step-60:self.current_step]

        df_temp = pd.DataFrame()
        df_temp["workload"] = window
        df_temp["workload"] = df_temp["workload"].rolling(5).mean()
        df_temp.dropna(inplace=True)
        df_temp["rolling_mean"] = df_temp["workload"].rolling(20).mean()
        df_temp["rolling_std"] = df_temp["workload"].rolling(20).std()
        df_temp.dropna(inplace=True)

        features = df_temp[["workload","rolling_mean","rolling_std"]].values
        scaled = self.scaler.transform(features)

        tensor = torch.tensor(scaled.reshape(1,len(features),3), dtype=torch.float32)

        with torch.no_grad():
            pred_scaled = self.lstm_model(tensor)

        prediction = self.scaler.inverse_transform(
            np.concatenate([pred_scaled.numpy(), np.zeros((1,2))], axis=1)
        )[0][0]

        return float(prediction)

    def _get_state(self):
        current_load = float(self.workload[self.current_step])
        predicted_load = self._predict_with_lstm()

        prev_load = float(self.workload[self.current_step-1])
        load_delta = current_load - prev_load

        return np.array(
            [current_load, predicted_load, load_delta, self.active_servers],
            dtype=np.float32
        )

    def step(self, action):

        # Apply scaling action
        if action == 0:
            self.active_servers = max(self.min_servers, self.active_servers - 1)
        elif action == 2:
            self.active_servers = min(self.max_servers, self.active_servers + 1)

        current_load = float(self.workload[self.current_step])
        capacity = self.active_servers * self.server_capacity

        overload = max(current_load - capacity, 0)

        # ✅ Track overload
        self.total_steps += 1
        if overload > 0:
            self.overload_count += 1

        # ✅ Enterprise Balanced Reward
        utilization = min(current_load / capacity, 1)

        overload_penalty = overload * self.overload_weight
        cost_penalty = self.active_servers * self.cost_weight

        stability_bonus = 0.5 if overload == 0 else 0

        reward = (
            utilization
            + stability_bonus
            - cost_penalty
            - overload_penalty
        )

        # ✅ Adaptive tuning every 500 steps
        if self.total_steps % 500 == 0:

            overload_rate = self.overload_count / self.total_steps

            if overload_rate > self.target_overload_rate:
                self.overload_weight *= 1.15
                self.cost_weight *= 0.95
            else:
                self.overload_weight *= 0.97
                self.cost_weight *= 1.02

            # Clamp safe ranges
            self.overload_weight = min(max(self.overload_weight, 20), 200)
            self.cost_weight = min(max(self.cost_weight, 0.01), 0.1)

        self.current_step += 1
        done = self.current_step >= self.episode_length

        return self._get_state(), reward, done, False, {}