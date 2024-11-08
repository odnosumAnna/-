import numpy as np
import matplotlib.pyplot as plt
from math import exp


def attacker_success_probability(q, z, threshold):
    p = 1.0 - q
    lambda_param = z * (q / p)

    sum_prob = 1.0
    for k in range(z + 1):
        poisson = exp(-lambda_param)
        for i in range(1, k + 1):
            poisson *= lambda_param / i
        sum_prob -= poisson * (1 - pow(q / p, z - k))

    return sum_prob


def find_min_confirmations(q, threshold):
    z = 1
    while True:
        prob = attacker_success_probability(q, z, threshold)
        if prob < threshold:
            return z
        z += 1
        if z > 1000:
            return -1


def analyze_and_plot():
    q_values = np.arange(0.1, 0.46, 0.05)  #  0.1 to 0.45  step 0.05
    thresholds = [1e-3, 1e-4, 1e-5]

    results = {}
    for threshold in thresholds:
        confirmations = []
        for q in q_values:
            z = find_min_confirmations(q, threshold)
            confirmations.append(z)
        results[threshold] = confirmations

    plt.figure(figsize=(10, 6))
    colors = ['b', 'g', 'r']
    markers = ['o', 's', '^']

    for (threshold, color, marker) in zip(thresholds, colors, markers):
        plt.plot(q_values, results[threshold],
                 label=f'Threshold = {threshold}',
                 color=color, marker=marker, linestyle='-')

    plt.xlabel('Attacker Hash Power Ratio (q)')
    plt.ylabel('Required Confirmation Blocks (z)')
    plt.title('Required Confirmations vs Attacker Hash Power')
    plt.grid(True)
    plt.legend()
    plt.ylim(bottom=0)
    plt.show()
    return results

results = analyze_and_plot()

print("\nRequired number of confirmations for different attack probabilities:")
print("\nq\t\tP=10^-3\tP=10^-4\tP=10^-5")
print("-" * 40)
for i, q in enumerate(np.arange(0.1, 0.46, 0.05)):
    print(f"{q:.2f}\t\t{results[1e-3][i]}\t\t{results[1e-4][i]}\t\t{results[1e-5][i]}")
