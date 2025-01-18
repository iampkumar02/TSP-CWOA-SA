import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io

# Load the console styles
def load_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('styles/console.css')

def build_logs_html(logs):
    lines_html = []
    for i, log in enumerate(logs):
        if "Current Distance =" in log:
            parts = log.split(":")
            iteration = parts[0]
            values = parts[1].split(",")
            
            current_dist = values[0].split("=")[1].strip()
            best_dist = values[1].split("=")[1].strip()
            
            formatted_log = (
                f"{iteration}: "
                f"Current Distance = <span class='distance-value'>{current_dist}</span>, "
                f"Best Distance = <span class='distance-value'>{best_dist}</span>"
            )
        else:
            formatted_log = log

        if i == len(logs) - 1:
            lines_html.append(f"<div class='log-line highlight'>{formatted_log}</div>")
        else:
            lines_html.append(f"<div class='log-line'>{formatted_log}</div>")

    return "\n".join(lines_html)

def create_log_box(logs):
    """
    This version keeps the view at the top, showing oldest logs first
    """
    logs_html = build_logs_html(logs)

    log_box_html = f"""
    <div class="log-container">
        <div class="log-header">Logs</div>
        <div class="scrollable-log-box" id="log-box">
            <div class="log-content" style="display: flex; flex-direction: column-reverse;">
                {logs_html}
            </div>
        </div>
    </div>
    <script>
        (function() {{
            const logBox = document.getElementById('log-box');
            
            // Keep scroll at top
            function keepAtTop() {{
                if (logBox) {{
                    logBox.scrollTop = 0;
                }}
            }}

            // Handle content changes
            const observer = new MutationObserver(() => {{
                keepAtTop();
            }});

            observer.observe(logBox, {{ 
                childList: true, 
                subtree: true 
            }});

            // Initial position
            keepAtTop();
        }})();
    </script>
    """
    return log_box_html

# -- Simple TSP/Simulated Annealing code --

def distance(city1, city2):
    return np.sqrt(np.sum((city1 - city2)**2))

def total_distance(tour, cities):
    return sum(distance(cities[tour[i]], cities[tour[i-1]]) for i in range(len(tour)))

def simulated_annealing(cities, initial_temp, cooling_rate, num_iterations):
    num_cities = len(cities)
    current_tour = list(range(num_cities))
    np.random.shuffle(current_tour)
    current_dist = total_distance(current_tour, cities)
    best_tour = current_tour.copy()
    best_dist = current_dist
    temp = initial_temp
    history = []

    for _ in range(num_iterations):
        new_tour = current_tour.copy()
        i, j = np.random.randint(0, num_cities, 2)
        new_tour[i], new_tour[j] = new_tour[j], new_tour[i]
        new_dist = total_distance(new_tour, cities)

        # Accept new tour if it's better or with some probability
        if new_dist < current_dist or np.random.random() < np.exp((current_dist - new_dist) / temp):
            current_tour = new_tour
            current_dist = new_dist

        # Update best solution found so far
        if current_dist < best_dist:
            best_tour = current_tour.copy()
            best_dist = current_dist

        # Keep track of progress
        history.append((current_tour.copy(), current_dist, best_tour.copy(), best_dist))
        temp *= cooling_rate

    return best_tour, best_dist, history

# -- Streamlit App --

st.title("Traveling Salesman Problem Solver")

num_cities = st.slider("Number of cities", 10, 100, 20)
initial_temp = st.number_input("Initial temperature", 1.0, 1000.0, 100.0)
cooling_rate = st.number_input("Cooling rate", 0.8, 0.9999, 0.995, format="%.4f")
num_iterations = st.number_input("Number of iterations", 100, 10000, 500)

if st.button("Solve TSP"):
    # Generate random city positions
    cities = np.random.rand(num_cities, 2)

    # Run simulated annealing
    best_tour, best_dist, history = simulated_annealing(
        cities, initial_temp, cooling_rate, num_iterations
    )

    animation_placeholder = st.empty()
    log_placeholder = st.empty()

    logs = []

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

    def update_plot(frame):
        # Update lines for the current tour and best tour
        current_tour, current_dist, best_tour_frame, best_dist_frame = history[frame]
        
        # Current tour
        x1 = cities[current_tour + [current_tour[0]], 0]
        y1 = cities[current_tour + [current_tour[0]], 1]
        line1.set_data(x1, y1)
        current_distance_text.set_text(f'Distance: {current_dist:.2f}')

        # Best tour
        x2 = cities[best_tour_frame + [best_tour_frame[0]], 0]
        y2 = cities[best_tour_frame + [best_tour_frame[0]], 1]
        line2.set_data(x2, y2)
        best_distance_text.set_text(f'Distance: {best_dist_frame:.2f}')

    # Simulate "real-time" updates
    for i, (curr_tour, curr_dist, best_t, best_dist_iteration) in enumerate(history):
        update_plot(i)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        animation_placeholder.image(buf, caption=f"Iteration: {i + 1}/{num_iterations}", use_container_width=True)
        
        log_message = f"Iteration {i+1}: Current Distance = {curr_dist:.2f}, Best Distance = {best_dist_iteration:.2f}"
        logs.append(log_message)
        
        log_box_html = create_log_box(logs)
        log_placeholder.markdown(log_box_html, unsafe_allow_html=True)
    plt.close(fig)

    st.write(f"**Best distance found**: {best_dist:.2f}")
    st.success("Done!")
