import matplotlib.pyplot as plt
import time

# Enable interactive mode
plt.ion()

# Create a figure
fig, ax = plt.subplots()
x = [0]
y = [0]
line, = ax.plot(x, y, label="Dynamic Plot")
ax.legend()

# Show the plot
plt.show()

# Update the plot dynamically
for i in range(1, 20):
    x.append(i)
    y.append(i**2)
    line.set_data(x, y)
    ax.relim()
    ax.autoscale_view()
    plt.pause(0.1)  # Short pause for GUI responsiveness
    print(f"Main thread is free. Iteration {i}")

print("Main thread finished execution.")