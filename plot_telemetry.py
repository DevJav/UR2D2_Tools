import pandas as pd
import matplotlib.pyplot as plt

# Set the style to dark
plt.style.use('dark_background')

# Load the data from the CSV file
data = pd.read_csv('telemetry_data_2024-12-13_11-56-54.csv', header=None, names=['lap', 'throttle', 'brake', 'right', 'left', 'speed'])

# Create a time axis based on the sample rate
sample_rate = 0.01  # sample rate in seconds

# Initialize the time column
data['time'] = 0.0

# Reset time for each lap
current_lap = data['lap'][0]
time_counter = 0.0

for i in range(len(data)):
    if data['lap'][i] != current_lap:
        current_lap = data['lap'][i]
        time_counter = 0.0
    data.at[i, 'time'] = time_counter
    time_counter += sample_rate

# Get unique laps
unique_laps = data['lap'].unique()

# Plot data for each lap
for lap in unique_laps:
    lap_data = data[data['lap'] == lap]
    
    plt.figure(figsize=(10, 6))
    
    plt.subplot(3, 1, 1)
    plt.plot(lap_data['time'], lap_data['throttle'], label='Throttle', color='g')
    plt.plot(lap_data['time'], lap_data['brake'], label='Brake', color='r')
    plt.legend()
    plt.title(f'Lap {lap} - Throttle and Brake')
    
    lap_data['steering'] = lap_data['right'] - lap_data['left']
    plt.subplot(3, 1, 2)
    plt.plot(lap_data['time'], lap_data['steering'], label='Steering', color='orange')
    plt.legend()
    plt.title(f'Lap {lap} - Steering')
    
    plt.subplot(3, 1, 3)
    plt.plot(lap_data['time'], lap_data['speed'], label='Speed', color='b')
    plt.legend()
    plt.title(f'Lap {lap} - Speed')
    
    plt.xlabel('Time (s)')
    plt.tight_layout()
    # shwo without stopping to close the window to see the next lap
    plt.show(block=False)

# wait for user to close the windows
plt.show()