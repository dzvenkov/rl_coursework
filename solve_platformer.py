import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv
from stable_baselines3.common.atari_wrappers import AtariWrapper
from PlatformerEnv import PlatformerEnv


# Setup environment

env = PlatformerEnv(screen_w=800, screen_h=600)
env = AtariWrapper(env)
env = DummyVecEnv([lambda: env])
env = VecFrameStack(env, n_stack=4)

# Checkpoint callback: saves model every 100,000 steps
checkpoint_callback = CheckpointCallback(
    save_freq=100_000,
    save_path="./snapshots/",
    name_prefix="ppo_platformer_checkpoint"
)

# Create and train PPO model with TensorBoard logging
model = PPO("CnnPolicy", env, verbose=1, tensorboard_log="./tensorboard_logs/")
model.learn(total_timesteps=1_000_000, callback=checkpoint_callback, tb_log_name="PPO_Platfromer")

# Save final model
model.save("ppo_platformer_final")
