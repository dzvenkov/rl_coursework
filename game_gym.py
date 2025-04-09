import pygame
import random
import gymnasium as gym
import numpy as np

# Global constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# --- Game Classes (Player, Platform, MovingPlatform, Coin, Level, etc.) ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        width = 40
        height = 60
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = 0
        self.level = None

    def update(self):
        self.calc_grav()
        self.rect.x += self.change_x

        # Horizontal collisions
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        # Vertical movement
        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
            self.change_y = 0
            if isinstance(block, MovingPlatform):
                self.rect.x += block.change_x

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.35

        # Check if on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        # Move down a bit and check for platforms.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10

    def go_left(self):
        self.change_x = -6

    def go_right(self):
        self.change_x = 6

    def stop(self):
        self.change_x = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()


class MovingPlatform(Platform):
    change_x = 0
    change_y = 0
    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0
    player = None
    level = None

    def update(self):
        self.rect.x += self.change_x
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
            else:
                self.player.rect.left = self.rect.right

        self.rect.y += self.change_y
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1

        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
            self.change_x *= -1


class Coin(pygame.sprite.Sprite):
    """A collectible coin that increases the player's score."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 0), (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Level(object):
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.coin_list = pygame.sprite.Group()
        self.player = player
        self.background = None
        self.world_shift = 0
        self.level_limit = -1000

    def update(self):
        self.platform_list.update()
        self.enemy_list.update()
        self.coin_list.update()

    def draw(self, screen):
        screen.fill(BLUE)
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.coin_list.draw(screen)

    def shift_world(self, shift_x):
        self.world_shift += shift_x
        for platform in self.platform_list:
            platform.rect.x += shift_x
        for enemy in self.enemy_list:
            enemy.rect.x += shift_x
        for coin in self.coin_list:
            coin.rect.x += shift_x

    def spawn_coins_near_platforms(self):
        for platform in self.platform_list:
            if random.random() < 0.6:
                x = platform.rect.x + random.randint(10, platform.rect.width - 10)
                y = platform.rect.y - 25
                coin = Coin(x, y)
                self.coin_list.add(coin)


class Level_01(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.level_limit = -1500
        level = [[210, 70, 500, 500],
                 [210, 70, 800, 400],
                 [210, 70, 1000, 500],
                 [210, 70, 1120, 280],
                 [150, 70, 700, 150],
                ]
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        block = MovingPlatform(70, 40)
        block.rect.x = 1350
        block.rect.y = 280
        block.boundary_left = 1350
        block.boundary_right = 1600
        block.change_x = 1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        block = MovingPlatform(70, 40)
        block.rect.x = 600
        block.rect.y = 100
        block.boundary_top = 100
        block.boundary_bottom = 420
        block.change_y = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        block = MovingPlatform(70, 40)
        block.rect.x = 1000
        block.rect.y = 100
        block.boundary_top = 100
        block.boundary_bottom = 300
        block.change_y = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        self.spawn_coins_near_platforms()


# --- Gymnasium Environment Wrapper ---

class PlatformerEnv(gym.Env):
    """Custom Gymnasium environment for the platformer game with multi-key support."""
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        super().__init__()
        self.width = width
        self.height = height

        # Define a multi-key action space:
        # action[0]: left, action[1]: right, action[2]: jump.
        self.action_space = gym.spaces.MultiBinary(3)
        # The observation is an RGB image (height, width, 3)
        self.observation_space = gym.spaces.Box(low=0, high=255,
                                                shape=(self.height, self.width, 3), dtype=np.uint8)

        # Create a hidden surface to render the game state.
        self.render_surface = pygame.Surface((self.width, self.height))
        self.done = False
        self.score = 0
        self.clock = pygame.time.Clock()

        # Initialize game objects.
        self.player = Player()
        self.level_list = [Level_01(self.player)]  # Add more levels if desired.
        self.current_level_no = 0
        self.current_level = self.level_list[self.current_level_no]
        self.player.level = self.current_level
        self.player.rect.x = 340
        self.player.rect.y = self.height - self.player.rect.height
        self.active_sprite_list = pygame.sprite.Group()
        self.active_sprite_list.add(self.player)

        # Initialize font for score rendering.
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 28)

    def reset(self, *, seed=None, options=None):
        self.done = False
        self.score = 0
        self.current_level_no = 0
        self.current_level = self.level_list[self.current_level_no]
        self.player.level = self.current_level
        self.player.rect.x = 340
        self.player.rect.y = self.height - self.player.rect.height
        self.player.change_x = 0
        self.player.change_y = 0
        self.active_sprite_list.empty()
        self.active_sprite_list.add(self.player)
        return self.render("rgb_array"), {}

    def step(self, action):
        # Process multi-key actions.
        # action is expected to be a vector of length 3: [left, right, jump].
        self.player.stop()
        left, right, jump = action[0], action[1], action[2]

        # For horizontal movement, if both left and right are pressed, they cancel out.
        if left and not right:
            self.player.go_left()
        elif right and not left:
            self.player.go_right()
        # If both or neither are pressed, horizontal speed remains 0.
        if jump:
            self.player.jump()

        # Update game objects.
        self.active_sprite_list.update()
        self.current_level.update()

        # Handle coin collection.
        coins_collected = pygame.sprite.spritecollide(self.player, self.current_level.coin_list, True)
        for _ in coins_collected:
            self.score += 1
            platform = random.choice(self.current_level.platform_list.sprites())
            x = platform.rect.x + random.randint(10, max(10, platform.rect.width - 10))
            y = platform.rect.y - 25
            new_coin = Coin(x, y)
            self.current_level.coin_list.add(new_coin)

        # Scroll the level if necessary.
        if self.player.rect.right >= 500:
            diff = self.player.rect.right - 500
            self.player.rect.right = 500
            self.current_level.shift_world(-diff)
        if self.player.rect.left <= 120:
            diff = 120 - self.player.rect.left
            self.player.rect.left = 120
            self.current_level.shift_world(diff)

        current_position = self.player.rect.x + self.current_level.world_shift
        if current_position < self.current_level.level_limit:
            if self.current_level_no < len(self.level_list) - 1:
                self.player.rect.x = 120
                self.current_level_no += 1
                self.current_level = self.level_list[self.current_level_no]
                self.player.level = self.current_level
            else:
                self.done = True

        observation = self.render("rgb_array")
        reward = self.score  # You can adjust the reward scheme as needed.
        return observation, reward, self.done, False, {"score": self.score}

    def render(self, mode="rgb_array"):
        # Clear the render surface.
        self.render_surface.fill(BLUE)
        # Draw level and sprites.
        self.current_level.draw(self.render_surface)
        self.active_sprite_list.draw(self.render_surface)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.render_surface.blit(score_text, (20, 20))
        if mode == "rgb_array":
            arr = pygame.surfarray.array3d(self.render_surface)
            return np.transpose(arr, (1, 0, 2))
        elif mode == "human":
            return None

    def close(self):
        pygame.quit()


# --- Main Loop (for running and displaying the game) ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Platformer with Coins (Gym Env Multi-Key Support)")

    # Create an instance of the environment.
    env = PlatformerEnv(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    observation, _ = env.reset()

    clock = pygame.time.Clock()
    done = False
    kill = False

    while not done and not kill:
        # Process events.
        for event in pygame.event.get():
            # Handle window quit or Alt+F4.
            if event.type == pygame.QUIT:
                kill = True

        # Use the current key states to determine the action.
        keys = pygame.key.get_pressed()
        # Action vector: [left, right, jump].
        action = np.array([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP]], dtype=np.int8)

        observation, reward, done, _, info = env.step(action)

        # Convert observation (an RGB array) to a Pygame surface.
        observation_surface = pygame.surfarray.make_surface(np.transpose(observation, (1, 0, 2)))
        screen.blit(observation_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    env.close()
    pygame.quit()


if __name__ == "__main__":
    main()
