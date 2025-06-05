import sys
import gymnasium as gym
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.atari_wrappers import AtariWrapper
from stable_baselines3.common.monitor import Monitor
from gymnasium.wrappers import FrameStack, TransformObservation
import numpy as np

from PlatformerEnv import PlatformerEnv, Step4Wrapper, Step5Wrapper
from RollingAverageRewardCallback import RollingAverageRewardCallback
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.utils import get_linear_fn


def make_env():
    env = PlatformerEnv(screen_w=800, screen_h=600, max_frames=1000)
    # env = Step4Wrapper(env)
    env = AtariWrapper(env, clip_reward=False)
    # env = Monitor(env)  
    # env = FrameStack(env, num_stack=4)  
    env = FrameStack(env, num_stack=4)
    # Convert the LazyFrames into a concrete np.ndarray
    env = TransformObservation(env, lambda obs: np.squeeze(np.array(obs), axis=-1))
    env.observation_space = gym.spaces.Box(low=0, high=255, shape=(4, 84, 84), dtype=np.uint8)
    env = DummyVecEnv([lambda: env])
    # env = Step4Wrapper(env)
    return env

if __name__ == '__main__':
    env = make_env()


    # Checkpoint every 25k steps
    checkpoint_callback = CheckpointCallback(
        save_freq=25_000,
        save_path="./snapshots/",
        name_prefix="dqn_platformer_checkpoint"
    )

    # Custom reward logging
    rolling_avg_callback = RollingAverageRewardCallback(rolling_window=100)
    callback = CallbackList([checkpoint_callback, rolling_avg_callback])

    # If an argument is provided, load an existing model; otherwise, create a new model
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
        print(f"Loading model from: {model_path}")
        model = DQN.load(model_path, env=env)
        '''
        model.exploration_final_eps = 0.075
        model.exploration_fraction = 0.1
        model.exploration_initial_eps = 0.25
        model._exploration_schedule = get_linear_fn(
            model.exploration_initial_eps,
            model.exploration_final_eps,
            model.exploration_fraction)
            '''
        
    else:
        model = DQN("CnnPolicy", env, verbose=1, tensorboard_log="./tensorboard_logs/",
                    exploration_final_eps=0.075, exploration_fraction=0.4, buffer_size=100000)

    model.learn(total_timesteps=3_000_000, callback=callback, tb_log_name="DQN_Platformer", reset_num_timesteps = False)

    model.save("dqn_platformer_final")
