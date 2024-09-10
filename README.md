# Optimizing TSP using Simulated Annealing

## Introduction

This project aims to solve the Traveling Salesman Problem (TSP) using Simulated Annealing (SA). The TSP is a classic optimization problem where the goal is to find the shortest possible route that visits a set of cities and returns to the origin city.

## Algorithm Explanation

### Simulated Annealing (SA)

Simulated Annealing is a probabilistic technique for approximating the global optimum of a given function. It is inspired by the annealing process in metallurgy and is particularly useful for large optimization problems like the TSP. The algorithm works as follows:

1. Start with a random solution and an initial high temperature.
2. Repeatedly:
   - Generate a neighboring solution.
   - If the new solution is better, accept it.
   - If the new solution is worse, accept it with a probability that decreases as the temperature cools.
3. Decrease the temperature according to a cooling schedule.
4. Repeat until a satisfactory solution is found or the temperature reaches a minimum value.

## Installation

To run this project, you need to have Python installed. You can install the required dependencies using pip:

```sh
pip install -r requirements.txt
```

The `requirements.txt` file should contain:

```
streamlit
numpy
matplotlib
pillow
```

## Usage

To run the Streamlit app, use the following command:

```sh
streamlit run tsp_solver.py
```

This will open a web interface where you can:

1. Adjust the number of cities
2. Set the initial temperature for the simulated annealing process
3. Adjust the cooling rate
4. Set the number of iterations
5. Click the "Solve TSP" button to start the optimization process

The app will display a real-time animation of the TSP solution process, showing both the current tour and the best tour found so far.

## Features

- Interactive web interface using Streamlit
- Real-time visualization of the TSP solving process
- Adjustable parameters for the Simulated Annealing algorithm
- Final visualization of the best tour found

## Future Work

- Implement the Chaotic Whale Optimization Algorithm (CWOA) for comparison with Simulated Annealing
- Add more TSP solving algorithms for benchmarking
- Improve the visualization with more detailed statistics and performance metrics
- Optimize the code for handling larger datasets