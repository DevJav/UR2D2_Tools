import pandas as pd
import matplotlib.pyplot as plt

# Set the style to dark
plt.style.use('dark_background')

# Load the data from the CSV file
data = pd.read_csv('data.csv', header=None, names=['throttle', 'brake', 'right', 'left', 'speed'])

# Create a time axis based on the sample rate
sample_rate = 0.01  # sample rate in seconds
data['time'] = data.index * sample_rate

# Plot the data
plt.figure(figsize=(10, 6))

plt.subplot(3, 1, 1)
plt.plot(data['time'], data['throttle'], label='Throttle', color='g')
plt.plot(data['time'], data['brake'], label='Brake', color='r')
plt.legend()
plt.title('Throttle and Brake')

data['steering'] = data['right'] - data['left']
plt.subplot(3, 1, 2)
plt.plot(data['time'], data['steering'], label='Steering', color='orange') 
plt.legend()
plt.title('Steering')

plt.subplot(3, 1, 3)
plt.plot(data['time'], data['speed'], label='Speed', color='b')
plt.legend()
plt.title('Speed')

plt.xlabel('Time (s)')
plt.tight_layout()
plt.show()