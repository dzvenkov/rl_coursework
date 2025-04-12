import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.atari_wrappers import AtariWrapper
from PlatformerEnv import PlatformerEnv
from RollingAverageRewardCallback import RollingAverageRewardCallback


# Setup environment

def make_env():
    env = PlatformerEnv(screen_w=800, screen_h=600, max_frames=1000)
    env = AtariWrapper(env, clip_reward=False)
    return env


if __name__ == '__main__':

    #env = DummyVecEnv([lambda: env])
    env = SubprocVecEnv([make_env for _ in range(4)])
    env = VecFrameStack(env, n_stack=4)

    # Create the checkpoint callback (save every 25k steps)
    checkpoint_callback = CheckpointCallback(
        save_freq=25_000,
        save_path="./snapshots/",
        name_prefix="ppo_platformer_checkpoint"
    )

    # Create our custom rolling average reward callback
    rolling_avg_callback = RollingAverageRewardCallback(rolling_window=100)

    # Combine callbacks into a CallbackList so both can be used during training
    callback = CallbackList([checkpoint_callback, rolling_avg_callback])

    # Create and train PPO model with TensorBoard logging
    model = PPO("CnnPolicy", env, verbose=1, tensorboard_log="./tensorboard_logs/")
    model.learn(total_timesteps=1_000_000, callback=callback, tb_log_name="PPO_Platformer")

    # Save final model
    model.save("ppo_platformer_final")