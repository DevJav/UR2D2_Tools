import pygame
import ctypes
import requests
import os
import win32gui
import win32con
import win32api

def main():
    # Initialize Pygame
    pygame.init()
    WIDTH, HEIGHT = 500, 120
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)  # Frameless window
    pygame.display.set_caption("Game Overlay")
    font_large = pygame.font.Font(pygame.font.match_font('arial'), 36)
    font_small = pygame.font.Font(pygame.font.match_font('arial'), 24)
    clock = pygame.time.Clock()

    # Colors
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BLACK = (0, 0, 0)
    TRANSPARENT_BLACK = (0, 0, 0, 128)

    # Fetch data from the timing script
    def fetch_data():
        try:
            response = requests.get("http://127.0.0.1:5000/get_data")
            return response.json()
        except requests.ConnectionError:
            return None

    # Make the Pygame window always on top and transparent
    hwnd = pygame.display.get_wm_info()["window"]

    # Set the window to be always on top and transparent
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x80000 | 0x20)  # WS_EX_LAYERED | WS_EX_TRANSPARENT
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 200, 0x2)  # Set full opacity (255)

    # get display size
    screen_width = win32api.GetSystemMetrics(0)

    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, win32api.GetSystemMetrics(win32con.SM_CYSCREEN) - HEIGHT, 0, 0, win32con.SWP_NOSIZE)

    # Enable "Always on Top" and fix overlapping issues for fullscreen apps
    def enable_fullscreen_overlay():
        # Register the overlay with DWM for modern fullscreen apps
        hwnd = pygame.display.get_wm_info()["window"]
        accent = ctypes.c_int(2)  # ACCENT_ENABLE_TRANSPARENT
        accent_struct_size = ctypes.sizeof(ctypes.c_int)
        data = ctypes.create_string_buffer(accent_struct_size)
        ctypes.memmove(data, ctypes.addressof(accent), accent_struct_size)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, data, ctypes.sizeof(data))

    enable_fullscreen_overlay()

    # Initialize best sector times
    best_sector_times = [float("inf")] * 3

    # Draw the overlay with styling
    def draw_overlay(data):
        # Semi-transparent background
        overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill(TRANSPARENT_BLACK)
        screen.blit(overlay_surface, (0, 0))

        if data:

            # Update best sector times
            for i in range(len(data["sector_times"])):
                if data["sector_times"][i] < best_sector_times[i]:
                    best_sector_times[i] = data["sector_times"][i]


            # Current lap time
            lap_time = data["current_lap_time"]
            lap_text = font_small.render(f"Lap Time: {lap_time:.2f}", True, WHITE)
            screen.blit(lap_text, (20, 10))

            # Current lap time
            lap_time = data["last_lap_time"]
            lap_text = font_small.render(f"Last Lap Time: {lap_time:.2f}", True, WHITE)
            screen.blit(lap_text, (300, 10))

            # Current sector times
            sector_texts = []
            for i, time in enumerate(data["sector_times"]):
                color = GREEN if time == best_sector_times[i] else YELLOW
                sector_texts.append(font_small.render(f"{time:.2f}", True, color))
            
            sector_text = font_small.render("Sector Times: ", True, WHITE)
            screen.blit(sector_text, (20, 35))
            for i, text in enumerate(sector_texts):
                screen.blit(text, (150 + i * 60, 35))

            # Best sector times
            best_sector_texts = [
                font_small.render(f"{t:.2f}" if t < float("inf") else "--", True, WHITE)
                for t in best_sector_times
            ]
            best_sector_text = font_small.render("Best Sector Times: ", True, WHITE)
            screen.blit(best_sector_text, (20, 60))
            for i, text in enumerate(best_sector_texts):
                screen.blit(text, (200 + i * 60, 60))

            # Best lap time
            best_lap_time = data["best_lap_time"]
            best_lap_text = font_small.render(
                f"Best Lap Time: {best_lap_time:.2f} ",
                True,
                GREEN if best_lap_time < float("inf") else WHITE,
            )
            screen.blit(best_lap_text, (20, 85))
        else:
            error_text = font_small.render("Error: Unable to fetch data", True, YELLOW)
            screen.blit(error_text, (20, 70))

    # Overlay loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        # Fetch and display data
        screen.fill(BLACK)  # Clear screen
        data = fetch_data()
        draw_overlay(data)

        pygame.display.flip()
        clock.tick(30)  # Limit to 30 FPS

    pygame.quit()
