import pygame
import os

class FoodSource:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30
        self.color = (0, 255, 0)  # Green

        image_path = os.path.join("assets", "images", "food_source.png")
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        except pygame.error as e:
            print(f"Error loading food_source image: {e}")
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill(self.color)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def use(self, simling):
        simling.hunger -= 50
        if simling.hunger < 0:
            simling.hunger = 0.0

class Bed:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = (60, 30)  # Width, Height
        self.color = (139, 69, 19)  # Brown

        image_path = os.path.join("assets", "images", "bed.png")
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.original_image, self.size)
        except pygame.error as e:
            print(f"Error loading bed image: {e}")
            self.image = pygame.Surface(self.size)
            self.image.fill(self.color)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def use(self, simling):
        simling.sleep -= 70
        if simling.sleep < 0:
            simling.sleep = 0.0
