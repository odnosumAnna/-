import math
from decimal import Decimal, getcontext
import numpy as np
import matplotlib.pyplot as plt

# Встановлення точності для обчислень з десятковими дробами
getcontext().prec = 50

def calculate_probabilities(p_m, alpha, d_h):
    """Розрахунок основних ймовірностей на основі вхідних параметрів."""
    p_h = 1 - p_m

    # Розрахунок α_h та α_m за допомогою рівняння (1)
    alpha_h = alpha * p_h
    alpha_m = alpha * p_m

    # Розрахунок p'_h та p'_m за допомогою рівняння (2)
    p_h_prime = math.exp(-alpha_m * d_h) * p_h
    p_m_prime = 1 - p_h_prime

    return p_h, alpha_h, alpha_m, p_h_prime, p_m_prime


def binomial_coefficient(n, k):
    """Обчислення біноміального коефіцієнта за допомогою логарифмів для роботи з великими числами."""
    if k > n:
        return 0
    if k == 0 or k == n:
        return 1

    # Використання логарифмів для обробки великих чисел
    log_result = 0
    for i in range(k):
        log_result += math.log(n - i)
        log_result -= math.log(i + 1)

    return round(math.exp(log_result))


def calculate_pz_k(z, k, p_h, alpha_m, d_h):
    """Обчислення P_z(k) за рівнянням з задачі."""
    if k < 0 or z < 0:
        return 0

    try:
        term1 = (p_h ** z) / math.factorial(z - 1)
        term2 = math.exp(-alpha_m * z * d_h) * ((alpha_m * z * d_h) ** k) / math.factorial(k)

        sum_term = 0
        for i in range(k + 1):
            factorial_term = math.factorial(z - i + 1)
            binom_coef = binomial_coefficient(k, i)
            power_term = (alpha_m * z * d_h) ** (-i)
            sum_term += factorial_term * binom_coef * power_term

        return term1 * term2 * sum_term
    except (OverflowError, ValueError):
        return 0


def calculate_attack_probability(z, p_h_prime, p_m_prime):
    """Обчислення ймовірності успішної атаки подвійних витрат після z підтверджень.""" #(3)
    if p_m_prime >= p_h_prime:
        return 1.0

    probability = 0
    ratio = p_m_prime / p_h_prime

    for k in range(z + 1):
        pz_k = calculate_pz_k(z, k, 1 - p_m_prime, -math.log(p_h_prime) / z, 1)
        if not math.isnan(pz_k):
            probability += pz_k * (1 - ratio ** (z - k))

    return 1 - probability


def find_minimum_confirmations(p_m, alpha, d_h, target_probability=1e-3):
    """Знайти мінімальну кількість підтверджень, необхідних для досягнення цільової ймовірності."""
    p_h, alpha_h, alpha_m, p_h_prime, p_m_prime = calculate_probabilities(p_m, alpha, d_h)

    z = 1
    while z <= 100:  # Встановлення розумного верхнього обмеження
        prob = calculate_attack_probability(z, p_h_prime, p_m_prime)
        if prob < target_probability:
            return z
        z += 1
    return None


def analyze_double_spend_attack(alpha=0.00167):
    """Аналіз атаки подвійних витрат для різних параметрів."""
    p_m_values = np.arange(0.1, 0.45, 0.05)
    d_h_values = [0, 15, 30, 60, 120, 180]
    results = {}

    for d_h in d_h_values:
        confirmations = []
        for p_m in p_m_values:
            z = find_minimum_confirmations(p_m, alpha, d_h)
            confirmations.append(z)
        results[d_h] = confirmations

    # Побудова графіка результатів
    plt.figure(figsize=(12, 8))
    for d_h, conf in results.items():
        plt.plot(p_m_values, conf, marker='o', label=f'D_H = {d_h}')

    plt.xlabel('Частка зловмисних майнерів (p_M)')
    plt.ylabel('Мінімальна кількість підтверджень, необхідна')
    plt.title(f'Аналіз атаки подвійних витрат (α = {alpha})')
    plt.legend()
    plt.grid(True)
    plt.show()

    return results

# Запуск аналізу для заданого α
print("Запуск аналізу для α = 0.00167...")
results_1 = analyze_double_spend_attack(alpha=0.00167)

# Запуск аналізу для іншого α (наприклад, α = 0.003)
print("\nЗапуск аналізу для α = 0.003...")
results_2 = analyze_double_spend_attack(alpha=0.003)