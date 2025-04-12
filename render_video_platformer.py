import gymnasium as gym
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
from stable_baselines3.common.atari_wrappers import AtariWrapper
from gymnasium.wrappers import FrameStack, TransformObservation
from stable_baselines3.common.monitor import Monitor
import imageio
import numpy as np

from PlatformerEnv import PlatformerEnv


# Function to create the environment with the same wrappers as during training
def make_env():
    env = PlatformerEnv(screen_w=800, screen_h=600, max_frames=1000)
    env = AtariWrapper(env, clip_reward=False)
    env = Monitor(env)  
    #env = FrameStack(env, num_stack=4)  
    env = FrameStack(env, num_stack=4)
    # Convert the LazyFrames into a concrete np.ndarray
    env = TransformObservation(env, lambda obs: np.squeeze(np.array(obs), axis=-1))
    env.observation_space = gym.spaces.Box(low=0, high=255, shape=(4, 84, 84), dtype=np.uint8)
    return env

experiment = 2

env = PlatformerEnv(screen_w=800, screen_h=600, max_frames=1000)
root_env = env
env = AtariWrapper(env, clip_reward=False)
env = Monitor(env)  
#env = FrameStack(env, num_stack=4)  
env = FrameStack(env, num_stack=4)
# Convert the LazyFrames into a concrete np.ndarray
env = TransformObservation(env, lambda obs: np.squeeze(np.array(obs), axis=-1))
env.observation_space = gym.spaces.Box(low=0, high=255, shape=(4, 84, 84), dtype=np.uint8)
# Load the trained model
##model = PPO.load("ppo_pong_final")
#model = PPO.load(f"ppo_platformer_checkpoint_{3}")
#model = PPO("CnnPolicy", env)
model = DQN.load(f"snapshots/dqn_platformer_checkpoint_475000_steps", buffer_size =0)

# Reset the environment (gymnasium returns an observation and an info dict)
obs, _ = env.reset()

frames = []  # List to store frames for the video
done = False

cnt = 0
while not done:
    # Capture the current frame from the underlying environment.
    frame = root_env.render()
    frames.append(frame)
    
    # Predict the next action using the loaded model
    action, _ = model.predict(obs, deterministic=True)
    
    # Take a step in the environment
    obs, reward, done, _, info = env.step(action)
    if (cnt % 100 == 0):
        print("frame: ", cnt)
    cnt += 1


env.close()

# Save the recorded frames as an MP4 video file using imageio
video_path = f"dqn_platformer_play_{experiment}.mp4"
fps = 30  # Frames per second for the output video
imageio.mimwrite(video_path, frames, fps=fps)
print("Video saved to", video_path)