import pygame
import ctypes
import requests
import win32gui
import win32con
import win32api

# Constants
WIDTH, HEIGHT = 500, 120
FPS = 30
API_URL = "http://127.0.0.1:5000/get_data"
TRANSPARENT_BLACK = (0, 0, 0, 128)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Game Overlay")
font_small = pygame.font.Font(pygame.font.match_font('arial'), 24)
clock = pygame.time.Clock()

# Initialize Best Sector Times
best_sector_times = []

# Window Configuration
def configure_window():
    hwnd = pygame.display.get_wm_info()["window"]

    # Always on top and transparent
    ctypes.windll.user32.SetWindowLongW(hwnd, -20,
        ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x80000 | 0x20)  # WS_EX_LAYERED | WS_EX_TRANSPARENT
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 200, 0x2)  # Transparency
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,
        win32api.GetSystemMetrics(win32con.SM_CYSCREEN) - HEIGHT, 0, 0, win32con.SWP_NOSIZE)

    # Enable fullscreen overlay compatibility
    accent = ctypes.c_int(2)  # ACCENT_ENABLE_TRANSPARENT
    data = ctypes.create_string_buffer(ctypes.sizeof(ctypes.c_int))
    ctypes.memmove(data, ctypes.addressof(accent), ctypes.sizeof(ctypes.c_int))
    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, data, ctypes.sizeof(data))

configure_window()

# Fetch data from the API
def fetch_data():
    try:
        response = requests.get(API_URL)
        return response.json()
    except requests.ConnectionError:
        return None

# Update best sector times
def update_best_sector_times(sector_times):
    global best_sector_times
    for i, time in enumerate(sector_times):
        if time < best_sector_times[i]:
            best_sector_times[i] = time

# Draw overlay elements
def draw_overlay(data):
    overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surface.fill(TRANSPARENT_BLACK)
    screen.blit(overlay_surface, (0, 0))

    if data:
        # Update sector times
        update_best_sector_times(data["sector_times"])

        # Draw current lap time
        draw_text(f"Lap Time: {data['current_lap_time']:.2f}", (20, 10))

        # Draw last lap time
        draw_text(f"Last Lap Time: {data['last_lap_time']:.2f}", (300, 10))

        # Draw sector times
        draw_text("Sector Times:", (20, 35))
        draw_sector_times(data["sector_times"], (150, 35))

        # Draw best sector times
        draw_text("Best Sector Times:", (20, 60))
        draw_sector_times(best_sector_times, (200, 60), True)

        # Draw best lap time
        best_lap_time = data["best_lap_time"]
        color = GREEN if best_lap_time < float("inf") else WHITE
        draw_text(f"Best Lap Time: {best_lap_time:.2f}", (20, 85), color)
    else:
        draw_text("Error: Unable to fetch data", (20, 70), YELLOW)

# Helper: Draw text on the screen
def draw_text(text, position, color=WHITE):
    rendered_text = font_small.render(text, True, color)
    screen.blit(rendered_text, position)

# Helper: Draw sector times
def draw_sector_times(times, start_position, is_best=False):
    for i, time in enumerate(times):
        text = f"{time:.2f}" if not is_best or time < float("inf") else "--"
        if is_best:
            color = WHITE
        elif time == best_sector_times[i]:
            color = GREEN 
        else:
            color = YELLOW
        draw_text(text, (start_position[0] + i * 60, start_position[1]), color)

# Main Loop
def main():
    global best_sector_times

    # Initialize sector times
    data = fetch_data()
    track_divisions = data.get("number_of_track_divisions", 3) if data else 3
    best_sector_times = [float("inf")] * track_divisions

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # Fetch data and render overlay
        screen.fill(BLACK)
        data = fetch_data()
        draw_overlay(data)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
