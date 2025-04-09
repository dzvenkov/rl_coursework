import pygame
from PlatformerEnv import PlatformerEnv
import numpy as np

# --- Main Loop (for running and displaying the game) ---

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Platformer with Coins (Multi-Key Gym Env)")

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
        # Action vector: [left, right, jump]
        action = np.array([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP]], dtype=np.int8)

        observation, reward, env_done, _, info = env.step(action)
        # If env_done is True, we break out.
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
