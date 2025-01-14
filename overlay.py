import pygame
import ctypes
import requests
import win32gui
import win32con
import win32api

# Constants
FPS = 30
API_URL = "http://127.0.0.1:5000/get_data"
TRANSPARENT_BLACK = (0, 0, 0, 128)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Pygame Initialization
pygame.init()

# Get the screen size
screen_width = win32api.GetSystemMetrics(0)
screen_height = win32api.GetSystemMetrics(1)

# Dynamic scaling factor based on screen height (you can adjust the multiplier)
scale_factor = screen_height / 1080  # Assuming 1080p as base

# Calculate the window size and font sizes based on screen resolution
# WIDTH = int(500 * scale_factor)
# HEIGHT = int(120 * scale_factor)
WIDTH=screen_width  
HEIGHT=screen_height
font_size_small = int(22 * scale_factor)
font_size_large = int(34 * scale_factor)
vertical_line_spacing = int(10 * scale_factor)
first_horizontal_line_spacing = int(10 * scale_factor)
second_horizontal_line_spacing = int(300 * scale_factor)
filler = int(10 * scale_factor)

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Game Overlay")
font_small = pygame.font.Font('Formula1-Regular_web_0.ttf', font_size_small)
font_large = pygame.font.Font('Formula1-Regular_web_0.ttf', font_size_large)
clock = pygame.time.Clock()

# Initialize Best Sector Times
best_sector_times = []

message = ""
message_color = WHITE
message_timer = 0
MESSAGE_DURATION = 2  # Display message for 2 seconds
ur2d2_center = (0, 0)

# Window Configuration
def configure_window():
    hwnd = pygame.display.get_wm_info()["window"]

    # Always on top and transparent
    ctypes.windll.user32.SetWindowLongW(hwnd, -20,
        ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x80000 | 0x20)  # WS_EX_LAYERED | WS_EX_TRANSPARENT
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 200, 0x2)  # Transparency

    # Find the Ultimate_Racing_2D_2.exe window
    ur2d2_hwnd = win32gui.FindWindow(None, "Ultimate Racing 2D 2")
    if ur2d2_hwnd:
        rect = win32gui.GetWindowRect(ur2d2_hwnd)
        ur2d2_x = rect[0]
        ur2d2_y = rect[1]
        ur2d2_width = rect[2] - rect[0]
        ur2d2_height = rect[3] - rect[1]

        # Position the overlay window at the bottom left of the Ultimate_Racing_2D_2 window
        overlay_x = ur2d2_x
        overlay_y = ur2d2_y + ur2d2_height - HEIGHT
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, overlay_x, overlay_y, 0, 0, win32con.SWP_NOSIZE)
    else:
        # Default position if Ultimate_Racing_2D_2 window is not found
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,
            win32api.GetSystemMetrics(win32con.SM_CYSCREEN) - HEIGHT, 0, 0, win32con.SWP_NOSIZE)

    # Enable fullscreen overlay compatibility
    accent = ctypes.c_int(2)  # ACCENT_ENABLE_TRANSPARENT
    data = ctypes.create_string_buffer(ctypes.sizeof(ctypes.c_int))
    ctypes.memmove(data, ctypes.addressof(accent), ctypes.sizeof(ctypes.c_int))
    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, data, ctypes.sizeof(data))

configure_window()

def update_overlay_position():
    global ur2d2_center
    hwnd = pygame.display.get_wm_info()["window"]
    ur2d2_hwnd = win32gui.FindWindow(None, "Ultimate Racing 2D 2")
    
    if ur2d2_hwnd:
        rect = win32gui.GetWindowRect(ur2d2_hwnd)
        ur2d2_x = rect[0]
        ur2d2_y = rect[1]
        ur2d2_width = rect[2] - rect[0]
        ur2d2_height = rect[3] - rect[1]
        ur2d2_center = (ur2d2_x + ur2d2_width // 2, ur2d2_y + ur2d2_height // 2)

        # Recalculate the overlay position
        overlay_x = ur2d2_x
        overlay_y = ur2d2_y + ur2d2_height - HEIGHT
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, overlay_x, overlay_y, 0, 0, win32con.SWP_NOSIZE)

# Fetch data from the API
def fetch_data():
    try:
        response = requests.get(API_URL)
        return response.json()
    except requests.ConnectionError:
        return None

# Update best sector times
def update_best_sector_times(sector_times):
    global best_sector_times, message, message_color, message_timer
    for i, time in enumerate(sector_times):
        if time < best_sector_times[i]:  # Better time found
            difference = best_sector_times[i] - time
            message = f"-{difference:.2f}"
            message_color = GREEN
            message_timer = MESSAGE_DURATION * FPS  # Convert seconds to frames
            best_sector_times[i] = time
        elif best_sector_times[i] != float("inf"):  # Not a better time, but valid
            difference = time - best_sector_times[i]
            message = f"+{difference:.2f}"
            message_color = YELLOW
            message_timer = MESSAGE_DURATION * FPS

# Draw the message at the center of the screen
def draw_message():
    global message_timer, ur2d2_center
    if message_timer > 0:
        rendered_message = font_large.render(message, True, message_color)
        text_rect = rendered_message.get_rect(center=ur2d2_center)
        screen.blit(rendered_message, text_rect)
        message_timer -= 1

# Draw overlay elements
def draw_overlay(data, previous_data):
    overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surface.fill(TRANSPARENT_BLACK)
    screen.blit(overlay_surface, (0, 0))

    if data:
        # Update sector times
        if previous_data["sector_times"] != data["sector_times"]:
            update_best_sector_times(data["sector_times"])

        # Draw current lap time
        draw_text(f"Lap Time: {data['current_lap_time']:.2f}", (first_horizontal_line_spacing, vertical_line_spacing))

        # Draw last lap time
        draw_text(f"Last Lap Time: {data['last_lap_time']:.2f}", (second_horizontal_line_spacing, vertical_line_spacing))

        # Draw sector times
        text_size_x, text_size_y = draw_text("Sector Times:", (first_horizontal_line_spacing, vertical_line_spacing + font_size_small))
        draw_sector_times(data["sector_times"], (first_horizontal_line_spacing + text_size_x + filler, vertical_line_spacing + font_size_small))

        # Draw best sector times
        text_size_x, text_size_y = draw_text("Best Sector Times:", (first_horizontal_line_spacing, vertical_line_spacing + font_size_small * 2))
        draw_sector_times(best_sector_times, (first_horizontal_line_spacing + text_size_x + filler, vertical_line_spacing + font_size_small * 2), is_best=True)

        # Draw best lap time
        best_lap_time = data["best_lap_time"]
        color = GREEN if best_lap_time < float("inf") else WHITE
        draw_text(f"Best Lap Time: {best_lap_time:.2f}", (first_horizontal_line_spacing, vertical_line_spacing + font_size_small * 3), color)
    else:
        draw_text("Error: Unable to fetch data", (first_horizontal_line_spacing, vertical_line_spacing))

# Helper: Draw text on the screen
def draw_text(text, position, color=WHITE):
    rendered_text = font_small.render(text, True, color)
    screen.blit(rendered_text, position)
    return rendered_text.get_size()

# Helper: Draw sector times
def draw_sector_times(times, start_position, is_best=False):
    text_size_x = 0
    for i, time in enumerate(times):
        text = f"{time:.2f}" if not is_best or time < float("inf") else "--"
        if is_best:
            color = WHITE
        elif time == best_sector_times[i]:
            color = GREEN 
        else:
            color = YELLOW
        text_width, _ = draw_text(text, (start_position[0] + text_size_x, start_position[1]), color)
        text_size_x += text_width + filler

# Main loop
def main():
    global best_sector_times

    # Initialize sector times
    data = fetch_data()
    previous_data = data
    track_divisions = data.get("number_of_track_divisions", 3) if data else 3
    best_sector_times = [float("inf")] * track_divisions

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # Update overlay position
        update_overlay_position()

        # Fetch data and render overlay
        screen.fill(BLACK)
        data = fetch_data()
        draw_overlay(data, previous_data)
        draw_message()  # Draw the message at the center of the screen

        pygame.display.flip()
        clock.tick(FPS)

        previous_data = data

    pygame.quit()

if __name__ == "__main__":
    main()
