import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
from stable_baselines3.common.atari_wrappers import AtariWrapper
import time
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

# Reset the environment; gymnasium's reset returns an observation and info dictionary
obs = env.reset()

# Run one episode, visualizing the gameplay
done = False
while not done:
    # Render the environment (a window should open)
    env.render()
    
    # Predict the next action using the loaded model
    action, _states = model.predict(obs)
    
    # Take a step in the environment; gymnasium returns terminated and truncated flags
    obs, reward, done, info = env.step(action)

    # Sleep for a short while so that the gameplay is viewable
    time.sleep(0.005)

env.close()