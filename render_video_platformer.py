import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
from stable_baselines3.common.atari_wrappers import AtariWrapper
import imageio
from PlatformerEnv import PlatformerEnv


# Function to create the environment with the same wrappers as during training
env = PlatformerEnv(screen_w=800, screen_h=600)
env = AtariWrapper(env)
env = DummyVecEnv([lambda: env])
env = VecFrameStack(env, n_stack=4)

# Load the trained model
##model = PPO.load("ppo_pong_final")
model = PPO.load("snapshots/ppo_platformer_checkpoint_25000_steps")
#model = PPO("CnnPolicy", env)


# Reset the environment (gymnasium returns an observation and an info dict)
obs = env.reset()

frames = []  # List to store frames for the video
done = False

cnt = 0
while not done:
    # Capture the current frame from the underlying environment.
    # Note: env.envs[0] accesses the single instance wrapped inside DummyVecEnv.
    frame = env.envs[0].render()
    frames.append(frame)
    
    # Predict the next action using the loaded model
    action, _ = model.predict(obs, deterministic=True)
    
    # Take a step in the environment
    obs, reward, done, info = env.step(action)
    if (cnt % 100 == 0):
        print("cnt: ", cnt)
    cnt += 1


env.close()

# Save the recorded frames as an MP4 video file using imageio
video_path = "ppo_platformer_play.mp4"
fps = 30  # Frames per second for the output video
imageio.mimwrite(video_path, frames, fps=fps)
print("Video saved to", video_path)