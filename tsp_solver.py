import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import io
from PIL import Image
import tempfile
import os

# Calculate distance between two cities
def distance(city1, city2):
    return np.sqrt(np.sum((city1 - city2)**2))

# Calculate total distance of a tour
def total_distance(tour, cities):
    return sum(distance(cities[tour[i]], cities[tour[i-1]]) for i in range(len(tour)))

# Simulated annealing function
def simulated_annealing(cities, initial_temp, cooling_rate, num_iterations):
    num_cities = len(cities)
    current_tour = list(range(num_cities))
    np.random.shuffle(current_tour)
    current_distance = total_distance(current_tour, cities)
    best_tour = current_tour.copy()
    best_distance = current_distance
    temp = initial_temp
    history = []

    for _ in range(num_iterations):
        new_tour = current_tour.copy()
        i, j = np.random.randint(0, num_cities, 2)
        new_tour[i], new_tour[j] = new_tour[j], new_tour[i]
        new_distance = total_distance(new_tour, cities)

        if new_distance < current_distance or np.random.random() < np.exp((current_distance - new_distance) / temp):
            current_tour = new_tour
            current_distance = new_distance

        if current_distance < best_distance:
            best_tour = current_tour.copy()
            best_distance = current_distance

        history.append((current_tour.copy(), current_distance, best_tour.copy(), best_distance))
        temp *= cooling_rate

    return best_tour, best_distance, history

# Streamlit app
st.title("Traveling Salesman Problem Solver")

# User inputs
num_cities = st.slider("Number of cities", 10, 100, 50)
initial_temp = st.number_input("Initial temperature", 1.0, 1000.0, 100.0)
cooling_rate = st.number_input("Cooling rate", 0.8, 0.9999, 0.995, format="%.4f")
num_iterations = st.number_input("Number of iterations", 100, 10000, 1000)

if st.button("Solve TSP"):
    # Generate random cities
    cities = np.random.rand(num_cities, 2)

    # Run simulated annealing
    best_tour, best_distance, history = simulated_annealing(cities, initial_temp, cooling_rate, num_iterations)

    # Create animation
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle("Traveling Salesman Problem - Simulated Annealing")

    for ax in (ax1, ax2):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.scatter(cities[:, 0], cities[:, 1], c='red', s=50)

    ax1.set_title("Current Tour")
    ax2.set_title("Best Tour")

    line1, = ax1.plot([], [], 'b-')
    line2, = ax2.plot([], [], 'g-')

    current_distance_text = ax1.text(0.05, 0.95, '', transform=ax1.transAxes)
    best_distance_text = ax2.text(0.05, 0.95, '', transform=ax2.transAxes)
    iteration_text = fig.text(0.5, 0.02, '', ha='center')

    def update(frame):
        current_tour, current_distance, best_tour, best_distance = history[frame]
        x1 = cities[current_tour + [current_tour[0]], 0]
        y1 = cities[current_tour + [current_tour[0]], 1]
        line1.set_data(x1, y1)
        current_distance_text.set_text(f'Distance: {current_distance:.2f}')

        x2 = cities[best_tour + [best_tour[0]], 0]
        y2 = cities[best_tour + [best_tour[0]], 1]
        line2.set_data(x2, y2)
        best_distance_text.set_text(f'Distance: {best_distance:.2f}')

        iteration_text.set_text(f'Iteration: {frame + 1}/{num_iterations}')
        return line1, line2, current_distance_text, best_distance_text, iteration_text

    anim = FuncAnimation(fig, update, frames=len(history), interval=50, blit=True)

    # Create a Streamlit placeholder for the animation
    animation_placeholder = st.empty()

    # Iterate through the history to update the animation in real-time
    for i in range(len(history)):
        current_tour, current_distance, best_tour, best_distance = history[i]
        
        # Update the plot
        update(i)
        
        # Convert the plot to an image
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        
        # Display the updated image
        animation_placeholder.image(img, caption=f"Iteration: {i + 1}/{num_iterations}", use_column_width=True)
        
        # Add a small delay to control the animation speed
        if i % 10 == 0:  # Update every 10 iterations to make the animation smoother
            st.text(f"Current Distance: {current_distance:.2f}, Best Distance: {best_distance:.2f}")

    plt.close(fig)  # Close the figure to free up memory

    # Display final results
    st.write(f"Best distance found: {best_distance:.2f}")

    # Plot final best tour
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.scatter(cities[:, 0], cities[:, 1], c='red', s=50)
    best_tour_coords = cities[best_tour + [best_tour[0]]]
    ax.plot(best_tour_coords[:, 0], best_tour_coords[:, 1], 'g-')
    ax.set_title("Final Best Tour")
    st.pyplot(fig)