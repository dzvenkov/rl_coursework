import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv
from stable_baselines3.common.atari_wrappers import AtariWrapper

# Setup environment
env_id = "PongNoFrameskip-v4"
env = gym.make(env_id)
env = AtariWrapper(env)
env = DummyVecEnv([lambda: env])
env = VecFrameStack(env, n_stack=4)

# Checkpoint callback: saves model every 100,000 steps
checkpoint_callback = CheckpointCallback(
    save_freq=100_000,
    save_path="./snapshots/",
    name_prefix="ppo_pong_checkpoint"
)

# Create and train PPO model with TensorBoard logging
model = PPO("CnnPolicy", env, verbose=1, tensorboard_log="./tensorboard_logs/")
model.learn(total_timesteps=1_000_000, callback=checkpoint_callback, tb_log_name="PPO_Pong")

# Save final model
model.save("ppo_pong_final")
