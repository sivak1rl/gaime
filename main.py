from simling import Simling
from objects import FoodSource, Bed
import pygame # Ensure pygame is imported if not already fully

# Initialize Pygame
pygame.init()
pygame.font.init() # Explicitly initialize font module

# Define screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set window title
pygame.display.set_caption("Simling Prototype")

# Pygame clock
clock = pygame.time.Clock()

# UI Font
ui_font = pygame.font.Font(None, 28) # System default font, size 28

# Selected Simling Tracker
selected_simling = None

# Create Simlings
simlings = [
    Simling(x=100, y=100),
    Simling(x=150, y=200),
]

# Create food sources and beds
food_sources = [
    FoodSource(x=50, y=50),
    FoodSource(x=700, y=500),
]
beds = [
    Bed(x=400, y=50),
    Bed(x=100, y=500),
]

# World objects dictionary
world_objects = {
    "food_sources": food_sources,
    "beds": beds,
}

# Main game loop
running = True
while running:
    # Time Delta Calculation
    time_delta_seconds = clock.tick(60) / 1000.0  # Aim for 60 FPS, convert ms to s

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                selected_simling = None # Deselect by default
                for simling_obj in simlings: 
                    simling_rect = pygame.Rect(simling_obj.x, simling_obj.y, simling_obj.size, simling_obj.size)
                    if simling_rect.collidepoint(event.pos):
                        selected_simling = simling_obj
                        print(f"Selected Simling at ({selected_simling.x}, {selected_simling.y})")
                        break # Stop after selecting one
            elif event.button == 3:  # Right mouse button
                if selected_simling is not None:
                    selected_simling.set_player_commanded_target(event.pos)
                    print(f"Commanding selected Simling to {event.pos}")

    # Update Phase
    for simling in simlings:
        simling.update(time_delta_seconds, world_objects)

    # Draw Phase
    # Fill the screen with white
    screen.fill((255, 255, 255))

    # Draw objects
    for food in food_sources:
        food.draw(screen)
    for bed in beds:
        bed.draw(screen)

    # Draw Simlings
    for simling in simlings:
        simling.draw(screen) # Original draw
        if simling == selected_simling:
            pygame.draw.rect(screen, (255, 0, 0), (simling.x - 2, simling.y - 2, simling.size + 4, simling.size + 4), 2) # Draw red border

    # UI Rendering for Selected Simling
    if selected_simling is not None:
        # Define starting Y position for the first line of text
        ui_start_y = 10
        ui_line_height = 25 # Pixels between lines of text
        ui_margin_x = 10

        # Helper function to render and blit text (optional, can be inline)
        def draw_text(text, x, y, color=(0,0,0)): # Black text by default
            text_surface = ui_font.render(text, True, color)
            screen.blit(text_surface, (x, y))

        # Display selected Simling's needs
        draw_text(f"Selected Simling:", ui_margin_x, ui_start_y)
        draw_text(f" - Hunger: {selected_simling.hunger:.1f}", ui_margin_x, ui_start_y + ui_line_height)
        draw_text(f" - Sleep: {selected_simling.sleep:.1f}", ui_margin_x, ui_start_y + 2 * ui_line_height)
        draw_text(f" - Social: {selected_simling.social:.1f}", ui_margin_x, ui_start_y + 3 * ui_line_height)
        draw_text(f" - Fun: {selected_simling.fun:.1f}", ui_margin_x, ui_start_y + 4 * ui_line_height)
        draw_text(f" - Action: {selected_simling.current_action}", ui_margin_x, ui_start_y + 5 * ui_line_height)

    # Update the display
    pygame.display.flip()

# Uninitialize Pygame
pygame.quit()
