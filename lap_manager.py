import time

class LapManager:
    def __init__(self, track_divisions, terminal_colors):
        self.track_divisions = track_divisions
        self.terminal_colors = terminal_colors
        self.best_sector_times = [float("inf")] * (len(track_divisions) + 1)
        self.best_lap_time = float("inf")
        self.lap_data = {
            "number_of_track_divisions": (len(track_divisions) + 1),
            "current_lap": 0,
            "current_lap_time": 0,
            "last_lap_time": 0,
            "sector_times": [],
            "best_sector_times": [],
            "best_lap_time": float("inf"),
        }
        self.lap_number = 0
        self.start_time = 0
        self.sector_index = 0
        self.laps_times_and_sectors = {}

        launch_time_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        self.file_name = f"lap_data_{launch_time_str}.txt"

        with open(self.file_name, "w") as file:
            file.write("Lap ")
            for i in range(len(track_divisions) + 1):
                file.write(f"S{i + 1} ")
            file.write("LapTime\n")

    def manage_sectors(self, sector_index, sector_time):
        if sector_time < self.best_sector_times[sector_index]:
            self.best_sector_times[sector_index] = sector_time
            color = self.terminal_colors["GREEN"]
        else:
            color = self.terminal_colors["YELLOW"]

        print(f"  {color}Sector {sector_index + 1}: {sector_time:.2f} s{self.terminal_colors['END']}")
        self.lap_data["sector_times"] = self.laps_times_and_sectors.get(self.lap_number, [])

    def manage_lap(self, lap_time):
        if lap_time < self.best_lap_time:
            self.best_lap_time = lap_time
            color = self.terminal_colors["GREEN"]
        else:
            color = self.terminal_colors["YELLOW"]

        print(f"{color}Lap time: {lap_time:.2f} s{self.terminal_colors['END']}")
        self.lap_data["last_lap_time"] = lap_time

    def update_lap_data(self, current_time):
        self.lap_data["current_lap_time"] = current_time - self.start_time
        self.lap_data["best_sector_times"] = self.best_sector_times
        self.lap_data["best_lap_time"] = self.best_lap_time

    def calculate_sector_time(self, current_time):
        sector_time = round(current_time - self.start_time, 2)
        if self.lap_number in self.laps_times_and_sectors:
            sector_time -= sum(self.laps_times_and_sectors[self.lap_number])
        return sector_time

    def store_sector_time(self, sector_time):
        self.laps_times_and_sectors[self.lap_number] = (
            self.laps_times_and_sectors.get(self.lap_number, []) + [sector_time]
        )

    def wait_for_next_lap(self, memory_reader):
        while int(memory_reader.read_double()) == self.lap_number:
            self.update_lap_data(time.time())
            time.sleep(0.001)

    def save_lap_data(self):
        with open(self.file_name, "a") as file:  # Change "w" to "a" to append instead of overwrite
            file.write(f"{self.lap_number} ")
            for sector in self.laps_times_and_sectors[self.lap_number]:
                file.write(f"{sector:.2f} ")
            file.write(f"{self.lap_data['last_lap_time']:.2f}\n")

    def reset_for_new_lap(self):
        self.save_lap_data()
        self.sector_index = 0
        self.start_time = time.time()
        self.lap_number += 1
        self.lap_data["current_lap"] = self.lap_number
