import time
from memory_reader import MemoryReader
import pygame
import sys
import math

GAME_NAME = "Ultimate_Racing_2D_2.exe"
POINTER_OFFSET = 0x021ACA90
OFFSETS = [0x838, 0x68, 0x10, 0x48, 0x10, 0x8F0, 0x0]
MAX_SPEED_KMH = 360
MAX_SPEED_GAME = 7.8

memory_reader_x = MemoryReader(GAME_NAME, POINTER_OFFSET)
memory_reader_x.attach()
memory_reader_x.resolve_pointer(OFFSETS)
# memory_reader_x.pointer += 0x50 # TODO: Better way to find the float value

# memory_reader_y = MemoryReader(GAME_NAME, POINTER_OFFSET)
# memory_reader_y.attach()
# memory_reader_y.resolve_pointer(OFFSETS)
# memory_reader_y.pointer += 0x54 # TODO: Better way to find the float value

while True:
    v = memory_reader_x.read_float()
    time.sleep(0.1)
    # Initialize pygame
    pygame.init()

    # Set up display
    width, height = 400, 400
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Speed Meter")

    # Set up font
    font = pygame.font.SysFont(None, 48)

    # Function to draw gauge
    def draw_gauge(speed):
        window.fill((0, 0, 0))  # Clear the screen with a black background
        
        # Center and radius for the gauge
        center = (width // 2, height // 2)
        radius = 150
        
        # Draw the gauge circle
        pygame.draw.circle(window, (255, 255, 255), center, radius, 5)
        
        # Map speed to the angle of the needle (speed 0 -> -90 degrees, max speed -> 90 degrees)
        angle = -90 + (speed / MAX_SPEED_GAME) * 180  # Convert speed to angle
        
        # Convert angle to radians
        angle_rad = math.radians(angle)
        
        # Calculate the needle's end position
        needle_length = radius - 20
        end_x = center[0] + needle_length * math.cos(angle_rad)
        end_y = center[1] + needle_length * math.sin(angle_rad)
        
        # Draw the needle
        pygame.draw.line(window, (255, 0, 0), center, (end_x, end_y), 3)
        
        # Draw the speed as text
        speed_kmh = (speed / MAX_SPEED_GAME) * MAX_SPEED_KMH
        speed_text = font.render(f"{int(speed_kmh)} km/h", True, (255, 255, 255))
        text_rect = speed_text.get_rect(center=(center[0], center[1] + radius + 30))
        window.blit(speed_text, text_rect)
        
        # Update the display
        pygame.display.flip()

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        v = abs(memory_reader_x.read_double())
        # print(v)
        
        draw_gauge(v)
        
        time.sleep(0.1)