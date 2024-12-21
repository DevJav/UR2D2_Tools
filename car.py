import time
from memory_reader import MemoryReader
from lap_manager import LapManager
from server import start_server

# Constants
GAME_NAME = "Ultimate_Racing_2D_2.exe"
POINTER_OFFSET = 0x021ACA98
OFFSETS = [0x8, 0x68, 0x10, 0x48, 0x10, 0xEA0]
TRACK_DIVISIONS = [0.33, 0.66]
TERMINAL_COLORS = {"YELLOW": "\033[93m", "GREEN": "\033[92m", "PURPLE": "\033[95m", "END": "\033[0m"}

class Car:
    def __init__(self):
        # Initialize components
        self.memory_reader = MemoryReader(GAME_NAME, POINTER_OFFSET)
        self.lap_manager = LapManager(TRACK_DIVISIONS, TERMINAL_COLORS)

        # Attach to game and resolve memory pointers
        self.memory_reader.attach()
        self.memory_reader.resolve_pointer(OFFSETS)

        # Start Flask server
        start_server(self.lap_manager.lap_data)

        # Start main loop
        self.run()

    def run(self):
        # Wait for current lap to finish
        self.lap_manager.lap_number = int(self.memory_reader.read_double())
        print(f"Waiting for lap {self.lap_manager.lap_number + 1} to start...")
        while int(self.memory_reader.read_double()) == self.lap_manager.lap_number:
            time.sleep(0.001)

        self.lap_manager.lap_number += 1

        # Main loop
        self.lap_manager.start_time = time.time()

        while True:
            try:
                # self.handle_pause(OFFSETS, self.memory_reader, self.lap_manager)
                        
                full_percentage = self.memory_reader.read_double()

                # Check if still in the same lap
                if int(full_percentage) == self.lap_manager.lap_number:
                    percentage = full_percentage - int(full_percentage)
                    if self.lap_manager.sector_index < len(TRACK_DIVISIONS):
                        # Check if it's time to process the next sector
                        if percentage >= TRACK_DIVISIONS[self.lap_manager.sector_index]:
                            current_time = time.time()
                            sector_time = self.lap_manager.calculate_sector_time(current_time)

                            self.lap_manager.store_sector_time(sector_time)
                            self.lap_manager.manage_sectors(self.lap_manager.sector_index, sector_time)

                            self.lap_manager.sector_index += 1

                # Check if lap is finished
                elif int(full_percentage) == self.lap_manager.lap_number + 1:
                    current_time = time.time()
                    sector_time = self.lap_manager.calculate_sector_time(current_time)
                    self.lap_manager.store_sector_time(sector_time)

                    self.lap_manager.manage_sectors(self.lap_manager.sector_index, sector_time)

                    lap_time = current_time - self.lap_manager.start_time
                    self.lap_manager.manage_lap(lap_time)

                    self.lap_manager.reset_for_new_lap()

                # Continuously update lap data
                self.lap_manager.update_lap_data(time.time())
                time.sleep(0.001)

            except Exception as e:
                print(f"Error: {e}")
                break

    def handle_pause(self):
        if self.memory_reader.read_4bytes(0xE414D8BE90) == 1:
            print(f"Pause {self.memory_reader.read_4bytes(0xE414D8BE90)}")
            pause_start = time.time()
            while self.memory_reader.read_4bytes(0xE414D8BE90) == 1:
                time.sleep(0.001)
            pause_end = time.time()
            pause_duration = pause_end - pause_start
            self.lap_manager.start_time += pause_duration

            # Check if lap has changed, meaning the game was restarted
            if int(self.memory_reader.read_double()) != self.lap_manager.lap_number:
                # reestart class
                    pass