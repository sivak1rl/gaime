import pygame
import math
import os # Added import os
from objects import FoodSource, Bed

class Simling:
    HUNGER_RATE = 0.5  # Units per second
    SLEEP_RATE = 0.3   # Units per second
    SOCIAL_RATE = 0.2  # Units per second
    FUN_RATE = 0.4     # Units per second (boredom increases)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hunger = 50.0
        self.sleep = 50.0
        self.social = 50.0
        self.fun = 50.0
        self.color = (0, 128, 255)  # A shade of blue
        self.size = 20
        self.speed = 50.0
        self.target_x = None
        self.target_y = None
        self.current_action = "idle"
        self.target_object = None

        image_path = os.path.join("assets", "images", "simling.png")
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        except pygame.error as e:
            print(f"Error loading simling image: {e}")
            # Fallback: create a placeholder surface if image loading fails
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill(self.color)

    def set_player_commanded_target(self, position):
        self.target_x = position[0]
        self.target_y = position[1]
        self.current_action = "player_commanded" # New action state
        self.target_object = None # Clear any autonomous target

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def move_towards_target(self, time_delta_seconds):
        if self.target_x is not None and self.target_y is not None:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < 1.0:  # Close enough, snap to target
                self.x = self.target_x
                self.y = self.target_y
                self.target_x = None
                self.target_y = None
                return  # Arrived

            normalized_dx = dx / distance
            normalized_dy = dy / distance
            move_amount = self.speed * time_delta_seconds
            self.x += normalized_dx * move_amount
            self.y += normalized_dy * move_amount

            # Re-check distance after move, if overshot or very close, snap
            new_dx = self.target_x - self.x
            new_dy = self.target_y - self.y
            if new_dx * dx < 0 or new_dy * dy < 0 or math.sqrt(new_dx*new_dx + new_dy*new_dy) < 1.0: # Overshot or very close
                self.x = self.target_x
                self.y = self.target_y
                self.target_x = None
                self.target_y = None

    def update(self, time_delta_seconds, world_objects):
        # Needs decay
        self.hunger += Simling.HUNGER_RATE * time_delta_seconds
        self.sleep += Simling.SLEEP_RATE * time_delta_seconds
        self.social += Simling.SOCIAL_RATE * time_delta_seconds
        self.fun += Simling.FUN_RATE * time_delta_seconds

        # Clamp values between 0 and 100
        self.hunger = max(0.0, min(100.0, self.hunger))
        self.sleep = max(0.0, min(100.0, self.sleep))
        self.social = max(0.0, min(100.0, self.social))
        self.fun = max(0.0, min(100.0, self.fun))

        self.move_towards_target(time_delta_seconds)

        # AI Logic
        if self.current_action == "idle":
            if self.hunger > 70 and world_objects.get("food_sources"): # Check for food if idle and hungry
                closest_food = self.find_closest_object(world_objects["food_sources"])
                if closest_food:
                    self.current_action = "seeking_food"
                    self.target_object = closest_food
                    self.target_x = closest_food.x + closest_food.size / 2 - self.size / 2
                    self.target_y = closest_food.y + closest_food.size / 2 - self.size / 2
            elif self.sleep > 70 and world_objects.get("beds"): # Check for bed if idle and sleepy
                closest_bed = self.find_closest_object(world_objects["beds"])
                if closest_bed:
                    self.current_action = "seeking_sleep"
                    self.target_object = closest_bed
                    self.target_x = closest_bed.x + closest_bed.size[0] / 2 - self.size / 2
                    self.target_y = closest_bed.y + closest_bed.size[1] / 2 - self.size / 2
        # Check for arrival at player-commanded destination
        elif self.current_action == "player_commanded" and self.target_x is None and self.target_y is None:
            self.current_action = "idle"
        elif self.current_action == "seeking_food":
            if self.target_x is None and self.target_object is not None and isinstance(self.target_object, FoodSource):
                self.target_object.use(self)
                self.current_action = "idle"
                self.target_object = None
        elif self.current_action == "seeking_sleep":
            if self.target_x is None and self.target_object is not None and isinstance(self.target_object, Bed):
                self.target_object.use(self)
                self.current_action = "idle"
                self.target_object = None

    def find_closest_object(self, objects_list):
        if not objects_list:
            return None
        closest_obj = None
        min_dist_sq = float('inf')

        for obj in objects_list:
            if isinstance(obj, Bed):
                obj_center_x = obj.x + obj.size[0] / 2
                obj_center_y = obj.y + obj.size[1] / 2
            else:  # Assuming FoodSource or similar with obj.size as a scalar
                obj_center_x = obj.x + obj.size / 2
                obj_center_y = obj.y + obj.size / 2
            
            dx = obj_center_x - (self.x + self.size / 2)
            dy = obj_center_y - (self.y + self.size / 2)
            dist_sq = dx*dx + dy*dy

            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_obj = obj
        return closest_obj
