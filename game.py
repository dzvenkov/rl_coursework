import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WASD Triangle Controller")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Triangle:
    def __init__(self, x, y, size=40, speed=5):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.angle = 0  # Radians

    def input(self, directions: list[int]):
        for direction in directions:
            if direction == 1:   # Up
                self.y -= self.speed
            elif direction == 2: # Down
                self.y += self.speed
            elif direction == 3: # Left
                self.x -= self.speed
            elif direction == 4: # Right
                self.x += self.speed

    def look_at(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        self.angle = math.atan2(dy, dx)

    def draw(self, surface):
        # Define triangle points relative to center (facing right by default)
        base_points = [
            (self.size, 0),                    # Tip
            (-self.size, -self.size * 0.75),   # Back left
            (-self.size, self.size * 0.75)     # Back right
        ]

        # Rotate and translate points
        rotated_points = []
        for px, py in base_points:
            rotated_x = px * math.cos(self.angle) - py * math.sin(self.angle)
            rotated_y = px * math.sin(self.angle) + py * math.cos(self.angle)
            rotated_points.append((self.x + rotated_x, self.y + rotated_y))

        pygame.draw.polygon(surface, WHITE, rotated_points)

# Create triangle instance
triangle = Triangle(WIDTH // 2, HEIGHT // 2)

# Game loop
clock = pygame.time.Clock()
while True:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            triangle.look_at(mx, my)

    # Gather all pressed directions
