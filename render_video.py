import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
from stable_baselines3.common.atari_wrappers import AtariWrapper
import imageio
import time

# Create the environment with the same wrappers as training,
# but with render_mode set to "rgb_array" to capture frames.
def make_env():
    env = gym.make("PongNoFrameskip-v4", render_mode="rgb_array")
    env = AtariWrapper(env)
    return env

env = DummyVecEnv([make_env])
env = VecFrameStack(env, n_stack=4)

# Load the trained model
model = PPO.load("ppo_pong_final")

# Reset the environment (gymnasium returns an observation and an info dict)
obs = env.reset()

frames = []  # List to store frames for the video
done = False

while not done:
    # Capture the current frame from the underlying environment.
    # Note: env.envs[0] accesses the single instance wrapped inside DummyVecEnv.
    frame = env.envs[0].render()
    frames.append(frame)
    
    # Predict the next action using the loaded model
    action, _ = model.predict(obs, deterministic=True)
    
    # Take a step in the environment
    obs, reward, done, info = env.step(action)


env.close()

# Save the recorded frames as an MP4 video file using imageio
video_path = "ppo_pong_play.mp4"
fps = 30  # Frames per second for the output video
imageio.mimwrite(video_path, frames, fps=fps)
print("Video saved to", video_path)