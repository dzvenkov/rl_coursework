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


# --- Game Classes (Player, Platform, MovingPlatform, Coin, Level, etc.) ---

class Player(pygame.sprite.Sprite):
    def __init__(self, screen_height):
        super().__init__()
        width = 40
        height = 60
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = 0
        self.level = None
        self.screen_height = screen_height

    def update(self):
        self.calc_grav()
        self.rect.x += self.change_x

        # Horizontal collision detection
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        # Vertical movement and collision detection
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

        # Make sure player doesn't fall below the screen
        if self.rect.y >= self.screen_height - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = self.screen_height - self.rect.height

    def jump(self):
        # Slightly adjust the player's position to detect if on platform.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2
        if len(platform_hit_list) > 0 or self.rect.bottom >= self.screen_height:
            self.change_y = -10

    def go_left(self):
        self.change_x = -6

    def go_right(self):
        self.change_x = 6


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
        self.level_limit_left = 300
        self.level_limit_right = 1800

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
        self.level_limit_left += shift_x
        self.level_limit_right += shift_x
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
        self.level_limit_left = 300
        self.level_limit_right = 1800
        level = [[210, 70, 500, 500],
                 [210, 70, 800, 400],
                 [210, 70, 1000, 500],
                 [210, 70, 1120, 280],
                 [150, 70, 700, 150],
                 # borders
                 [500, 1000, -300, 0],
                 [500, 1000, 1900, 0],
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
    """Custom Gymnasium environment for the platformer game with discrete action space,
       a dummy ALE interface, and a frame limit for episodes."""
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, screen_w, screen_h, max_frames=3600):
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.max_frames = max_frames  # Maximum frames per episode (default 60 sec * 60 fps)
        self.frame_count = 0

        # Define a discrete action space with 6 actions:
        # 0: NOOP, 1: LEFT, 2: RIGHT, 3: JUMP, 4: JUMP_LEFT, 5: JUMP_RIGHT
        self.action_space = gym.spaces.Discrete(6)
        # The observation is an RGB image (height, width, 3)
        self.observation_space = gym.spaces.Box(low=0, high=255,
                                                shape=(self.screen_h, self.screen_w, 3), dtype=np.uint8)

        # Create an offscreen surface to render the game state.
        self.render_surface = pygame.Surface((self.screen_w, self.screen_h))
        self.done = False
        self.score = 0
        self.clock = pygame.time.Clock()

        # Initialize game objects.
        self.player = Player(self.screen_h)
        self.level_list = [Level_01(self.player)]  # More levels can be added.
        self.current_level_no = 0
        self.current_level = self.level_list[self.current_level_no]
        self.player.level = self.current_level
        self.player.rect.x = 340
        self.player.rect.y = self.screen_h - self.player.rect.height
        self.active_sprite_list = pygame.sprite.Group()
        self.active_sprite_list.add(self.player)

        # Initialize font for score and timer rendering.
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 28)

    @property
    def ale(self):
        # Provide a dummy Arcade Learning Environment interface.
        class DummyALE:
            def lives(self):
                return 1
        return DummyALE()

    def get_action_meanings(self):
        return ["NOOP", "LEFT", "RIGHT", "JUMP", "JUMP_LEFT", "JUMP_RIGHT"]

    def reset(self, *, seed=None, options=None):
        self.done = False
        self.score = 0
        self.total_reward = 0
        self.total_cf = 0
        self.total_pf = 0
        self.total_bf = 0
        self.current_level_no = 0
        self.current_level = self.level_list[self.current_level_no]
        self.player.level = self.current_level
        self.player.rect.x = 340
        self.player.rect.y = self.screen_h - self.player.rect.height
        self.player.change_x = 0
        self.player.change_y = 0
        self.active_sprite_list.empty()
        self.active_sprite_list.add(self.player)
        self.frame_count = 0  # Reset frame counter
        return self.render("rgb_array"), {}

    def step(self, action):
        # Increment frame counter.
        self.frame_count += 1
        if self.frame_count >= self.max_frames:
            self.done = True

        # Reset horizontal movement.
        self.player.change_x = 0

        # Interpret the discrete action.
        if action == 0:  # NOOP
            pass
        elif action == 1:  # LEFT
            self.player.go_left()
        elif action == 2:  # RIGHT
            self.player.go_right()
        elif action == 3:  # JUMP
            self.player.jump()
        elif action == 4:  # JUMP_LEFT
            self.player.go_left()
            self.player.jump()
        elif action == 5:  # JUMP_RIGHT
            self.player.go_right()
            self.player.jump()

        # Update game objects.
        self.active_sprite_list.update()
        self.current_level.update()

        # Handle coin collection.
        coins_collected = pygame.sprite.spritecollide(self.player, self.current_level.coin_list, True)
        coins_reward = 0
        for coin in coins_collected:
            self.score += 1
            coins_reward += (600 - coin.rect.y) / 3  # Reward based on coin height.
            # Spawn a new coin at a random position on a platform.
            platform = random.choice(self.current_level.platform_list.sprites())
            x = platform.rect.x + random.randint(10, max(10, platform.rect.width - 10))
            y = platform.rect.y - 25
            new_coin = Coin(x, y)
            self.current_level.coin_list.add(new_coin)

        # --- Add coin proximity reward factor ---
        # Calculate the distance from the player to each coin still in the level.
        coins = self.current_level.coin_list.sprites()
        if coins:
            # Compute Euclidean distances from the player's center to each coin.
            distances = [
                np.sqrt((self.player.rect.centerx - coin.rect.centerx)**2 +
                        (self.player.rect.centery - coin.rect.centery)**2)
                for coin in coins
            ]
            # Use the closest coin distance.
            min_distance = min(distances)
            # Set a maximum distance threshold (adjust as needed).
            max_distance = 1000  
            # Linearly interpolate: if min_distance == 0, factor is 5; if min_distance >= max_distance, factor is 1.
            proximity_factor = - 5 * (min_distance / max_distance)
            #Clamp the factor 
            proximity_factor = max(-5, min(0, proximity_factor))
        else:
            proximity_factor = 0
        proximity_factor /= 10

        # Check for level-end conditions.
        if self.player.rect.right >= 500:
            diff = self.player.rect.right - 500
            self.player.rect.right = 500
            self.current_level.shift_world(-diff)
        if self.player.rect.left <= 120:
            diff = 120 - self.player.rect.left
            self.player.rect.left = 120
            self.current_level.shift_world(diff)

        #border factor
        border_factor = 0
        if self.player.rect.right >= self.current_level.level_limit_right:
            border_factor = -10
        if self.player.rect.left <= self.current_level.level_limit_left:
            border_factor = -10


        # Combine the rewards: reward from coins, plus bonus from proximity + border penalty
        reward = coins_reward + proximity_factor + border_factor

        self.total_reward += reward
        self.total_cf += coins_reward
        self.total_pf += proximity_factor
        self.total_bf += border_factor

        #print(f"p : {proximity_factor}, b: {border_factor}, c: {coins_reward}, s: {self.score}, r: {reward}")
        observation = self.render("rgb_array")
        info = {}
        if self.done:
            info = {"episode": {"r": self.total_reward, "l": self.frame_count, "score": self.score, "cf": self.total_cf, "pf": self.total_pf, "bf": self.total_bf}}
        return observation, reward, self.done, False, info


    def render(self, mode="rgb_array"):
        # Clear the offscreen surface.
        self.render_surface.fill(BLUE)
        # Draw the level and active sprites.
        self.current_level.draw(self.render_surface)
        self.active_sprite_list.draw(self.render_surface)
        # Render score text.
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.render_surface.blit(score_text, (20, 20))
        # Compute time left in seconds (assuming 60 FPS).
        time_left = max(0, (self.max_frames - self.frame_count) // 60)
        timer_text = self.font.render(f"Time Left: {time_left} sec", True, WHITE)
        # Blit the timer next to the score (for example, just below it).
        self.render_surface.blit(timer_text, (20, 60))
        if mode == "rgb_array":
            arr = pygame.surfarray.array3d(self.render_surface)
            return np.transpose(arr, (1, 0, 2))
        elif mode == "human":
            return None

    def close(self):
        pygame.quit()
