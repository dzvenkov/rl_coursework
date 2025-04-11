import pygame
from PlatformerEnv import PlatformerEnv
import numpy as np

# --- Main Loop (for running and displaying the game) ---

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Platformer with Coins (Discrete Gym Env)")

    # Create an instance of the environment.
    env = PlatformerEnv(screen_w=SCREEN_WIDTH, screen_h=SCREEN_HEIGHT)
    observation, _ = env.reset()

    clock = pygame.time.Clock()
    done = False

    while not done:
        # Process events.
        for event in pygame.event.get():
            # Check for the QUIT event.
            if event.type == pygame.QUIT:
                done = True
        
        # If a QUIT event is detected, break immediately.
        if done:
            break

        # Obtain the current key state.
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        jump = keys[pygame.K_UP]

        # Determine the discrete action based on key presses.
        # The available actions are:
        # 0: NOOP, 1: LEFT, 2: RIGHT, 3: JUMP, 4: JUMP_LEFT, 5: JUMP_RIGHT
        if jump:
            if left:
                action = 4  # JUMP_LEFT
            elif right:
                action = 5  # JUMP_RIGHT
            else:
                action = 3  # JUMP
        else:
            if left and not right:
                action = 1  # LEFT
            elif right and not left:
                action = 2  # RIGHT
            else:
                action = 0  # NOOP

        observation, reward, env_done, _, info = env.step(action)
        if env_done:
            done = True

        # Convert the observation (an RGB array) to a Pygame surface.
        observation_surface = pygame.surfarray.make_surface(np.transpose(observation, (1, 0, 2)))
        screen.blit(observation_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    env.close()

if __name__ == "__main__":
    main()
