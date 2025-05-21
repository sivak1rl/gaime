import unittest
from simling import Simling
from objects import FoodSource, Bed
import pygame # Simling __init__ tries to load an image, which needs pygame.display.set_mode()
import os

class TestSimlingNeeds(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Pygame display needs to be initialized for image loading to work,
        # even if we don't actually use the display in these tests.
        # This is because Simling() tries to load an image.
        # Set a dummy video mode.
        if os.environ.get('SDL_VIDEODRIVER') == 'dummy':
            pygame.display.init()
            pygame.display.set_mode((1, 1)) # Dummy screen
        else:
            # In a real environment, you might not need this if display is available
            # or if images are mocked out. For this sandbox, we ensure it runs.
            try:
                pygame.display.init()
                pygame.display.set_mode((1, 1))
            except pygame.error:
                # Fallback if display init fails (e.g. no X server)
                os.environ['SDL_VIDEODRIVER'] = 'dummy'
                pygame.display.init()
                pygame.display.set_mode((1, 1))


    def setUp(self):
        """This method is run before each test."""
        self.simling = Simling(x=0, y=0)
        # Reset needs to known values for reliable testing
        self.simling.hunger = 50.0
        self.simling.sleep = 50.0
        self.simling.social = 50.0
        self.simling.fun = 50.0

    def test_need_decay(self):
        """Test that needs decay correctly over time."""
        self.simling.update(time_delta_seconds=1.0, world_objects={})
        self.assertAlmostEqual(self.simling.hunger, 50.0 + Simling.HUNGER_RATE * 1.0)
        self.assertAlmostEqual(self.simling.sleep, 50.0 + Simling.SLEEP_RATE * 1.0)
        self.assertAlmostEqual(self.simling.social, 50.0 + Simling.SOCIAL_RATE * 1.0)
        self.assertAlmostEqual(self.simling.fun, 50.0 + Simling.FUN_RATE * 1.0)

    def test_need_clamping_upper(self):
        """Test that needs are clamped at their upper limit (100.0)."""
        self.simling.hunger = 99.9
        self.simling.sleep = 99.8
        self.simling.social = 99.7
        self.simling.fun = 99.6
        
        self.simling.update(time_delta_seconds=10.0, world_objects={}) # Long delta
        
        self.assertAlmostEqual(self.simling.hunger, 100.0)
        self.assertAlmostEqual(self.simling.sleep, 100.0)
        self.assertAlmostEqual(self.simling.social, 100.0)
        self.assertAlmostEqual(self.simling.fun, 100.0)

    def test_food_satisfaction(self):
        """Test interaction with FoodSource and hunger satisfaction."""
        food = FoodSource(x=10, y=10)
        
        # Test normal reduction
        self.simling.hunger = 80.0
        food.use(self.simling)
        self.assertAlmostEqual(self.simling.hunger, 30.0)
        
        # Test clamping at 0
        self.simling.hunger = 20.0
        food.use(self.simling)
        self.assertAlmostEqual(self.simling.hunger, 0.0)

        # Test when hunger is already 0
        self.simling.hunger = 0.0
        food.use(self.simling)
        self.assertAlmostEqual(self.simling.hunger, 0.0)

        # Test when reduction would go far below 0
        self.simling.hunger = 40.0 # Food reduces by 50
        food.use(self.simling)
        self.assertAlmostEqual(self.simling.hunger, 0.0)

    def test_sleep_satisfaction(self):
        """Test interaction with Bed and sleep satisfaction."""
        bed = Bed(x=10, y=10)
        
        # Test normal reduction
        self.simling.sleep = 90.0
        bed.use(self.simling)
        self.assertAlmostEqual(self.simling.sleep, 20.0)
        
        # Test clamping at 0
        self.simling.sleep = 30.0
        bed.use(self.simling)
        self.assertAlmostEqual(self.simling.sleep, 0.0)

        # Test when sleep is already 0
        self.simling.sleep = 0.0
        bed.use(self.simling)
        self.assertAlmostEqual(self.simling.sleep, 0.0)

        # Test when reduction would go far below 0
        self.simling.sleep = 60.0 # Bed reduces by 70
        bed.use(self.simling)
        self.assertAlmostEqual(self.simling.sleep, 0.0)


class TestSimlingAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This assumes the setUpClass from TestSimlingNeeds has already run
        # and initialized Pygame display if necessary.
        # If running this test class in isolation and objects load images,
        # a similar Pygame initialization might be needed here.
        # For now, we rely on TestSimlingNeeds's setup or that image loading
        # in Simling/Object is robust to no display (e.g., uses fallback).
        # The existing setUpClass in TestSimlingNeeds should handle this globally.
        pass

    def setUp(self):
        """This method is run before each test."""
        self.simling = Simling(x=0, y=0)
        self.food1 = FoodSource(x=100, y=100) # Closest food
        self.food2 = FoodSource(x=500, y=500) # Further food
        self.bed1 = Bed(x=50, y=50)     # Closest bed
        self.bed2 = Bed(x=400, y=400)   # Further bed
        self.world_objects = {
            "food_sources": [self.food1, self.food2],
            "beds": [self.bed1, self.bed2]
        }
        
        # Reset Simling's needs and state
        self.simling.hunger = 0.0
        self.simling.sleep = 0.0
        self.simling.social = 0.0 # Reset all needs for a clean state
        self.simling.fun = 0.0
        self.simling.current_action = "idle"
        self.simling.target_object = None
        self.simling.target_x = None
        self.simling.target_y = None

    def test_ai_seeks_food_when_hungry(self):
        """Test AI seeks food when hungry."""
        self.simling.hunger = 80  # Above threshold (default 70)
        self.simling.update(time_delta_seconds=0.1, world_objects=self.world_objects)
        
        self.assertEqual(self.simling.current_action, "seeking_food")
        self.assertEqual(self.simling.target_object, self.food1) # Closest food
        self.assertAlmostEqual(self.simling.target_x, self.food1.x + self.food1.size / 2 - self.simling.size / 2)
        self.assertAlmostEqual(self.simling.target_y, self.food1.y + self.food1.size / 2 - self.simling.size / 2)

    def test_ai_seeks_sleep_when_sleepy(self):
        """Test AI seeks sleep when sleepy."""
        self.simling.sleep = 80  # Above threshold (default 70)
        self.simling.update(time_delta_seconds=0.1, world_objects=self.world_objects)
        
        self.assertEqual(self.simling.current_action, "seeking_sleep")
        self.assertEqual(self.simling.target_object, self.bed1) # Closest bed
        self.assertAlmostEqual(self.simling.target_x, self.bed1.x + self.bed1.size[0] / 2 - self.simling.size / 2)
        self.assertAlmostEqual(self.simling.target_y, self.bed1.y + self.bed1.size[1] / 2 - self.simling.size / 2)

    def test_ai_eats_when_at_food(self):
        """Test AI eats when it arrives at a food source."""
        self.simling.hunger = 80.0
        initial_hunger = self.simling.hunger
        
        self.simling.current_action = "seeking_food"
        self.simling.target_object = self.food1
        # Simulate arrival by setting Simling's position to the target's position
        # and clearing target_x/y to trigger arrival logic in update.
        self.simling.x = self.food1.x + self.food1.size / 2 - self.simling.size / 2
        self.simling.y = self.food1.y + self.food1.size / 2 - self.simling.size / 2
        self.simling.target_x = None 
        self.simling.target_y = None
        
        self.simling.update(time_delta_seconds=0.1, world_objects=self.world_objects)
        
        self.assertLess(self.simling.hunger, initial_hunger)
        self.assertEqual(self.simling.hunger, 80.0 - 50.0) # FoodSource reduces by 50
        self.assertEqual(self.simling.current_action, "idle")
        self.assertIsNone(self.simling.target_object)

    def test_ai_sleeps_when_at_bed(self):
        """Test AI sleeps when it arrives at a bed."""
        self.simling.sleep = 80.0
        initial_sleep = self.simling.sleep
        
        self.simling.current_action = "seeking_sleep"
        self.simling.target_object = self.bed1
        self.simling.x = self.bed1.x + self.bed1.size[0] / 2 - self.simling.size / 2
        self.simling.y = self.bed1.y + self.bed1.size[1] / 2 - self.simling.size / 2
        self.simling.target_x = None
        self.simling.target_y = None
            
        self.simling.update(time_delta_seconds=0.1, world_objects=self.world_objects)
        
        self.assertLess(self.simling.sleep, initial_sleep)
        self.assertEqual(self.simling.sleep, 80.0 - 70.0) # Bed reduces by 70
        self.assertEqual(self.simling.current_action, "idle")
        self.assertIsNone(self.simling.target_object)

    def test_ai_prefers_food_over_sleep_if_both_high(self):
        """Test AI prioritizes food if both hunger and sleep are high."""
        self.simling.hunger = 80
        self.simling.sleep = 80
        self.simling.update(time_delta_seconds=0.1, world_objects=self.world_objects)
        
        # This assumes hunger is checked before sleep in Simling's update method
        self.assertEqual(self.simling.current_action, "seeking_food")
        self.assertEqual(self.simling.target_object, self.food1)


if __name__ == '__main__':
    unittest.main()
