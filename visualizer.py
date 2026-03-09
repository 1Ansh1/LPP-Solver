import matplotlib.pyplot as plt
import numpy as np

def plot_lpp(c, A, b, results):
    """Plots the 2D feasible region and the optimal point."""
    plt.figure(figsize=(6, 5))
    
    # 1. Define the range for x and y
    x_vals = np.linspace(0, max(b) * 1.5, 400)
    
    # 2. Plot each constraint line
    for i in range(len(A)):
        # ai1*x + ai2*y = bi  =>  y = (bi - ai1*x) / ai2
        if A[i, 1] != 0:
            y_vals = (b[i] - A[i, 0] * x_vals) / A[i, 1]
            plt.plot(x_vals, y_vals, label=f'Constraint {i+1}')
        else:
            # Handle vertical lines (x = bi / ai1)
            plt.axvline(x=b[i]/A[i, 0], label=f'Constraint {i+1}')

    # 3. Shade the Feasible Region (Simplified logic for 2D)
    # This finds the minimum y-value among all constraint lines for each x
    y_feasible = np.zeros_like(x_vals) + 1000 # Start with a high value
    for i in range(len(A)):
        if A[i, 1] != 0:
            y_line = (b[i] - A[i, 0] * x_vals) / A[i, 1]
            y_feasible = np.minimum(y_feasible, np.maximum(0, y_line))
    
    plt.fill_between(x_vals, 0, y_feasible, color='gray', alpha=0.3, label='Feasible Region')

    # 4. Plot the Optimal Point
    opt_x, opt_y = results['vars'][0], results['vars'][1]
    plt.scatter(opt_x, opt_y, color='red', s=100, edgecolors='black', zorder=5, label='Optimal Point')
    plt.annotate(f'({opt_x:.1f}, {opt_y:.1f})', (opt_x, opt_y), textcoords="offset points", xytext=(10,10), ha='center')

    # 5. Formatting
    plt.xlim(0, max(b))
    plt.ylim(0, max(b))
    plt.xlabel('$x_1$')
    plt.ylabel('$x_2$')
    plt.title('Feasible Region & Optimal Solution')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()