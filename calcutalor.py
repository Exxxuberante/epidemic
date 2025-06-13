import math
import polynoms as pn
import numpy as np
from scipy.integrate import odeint

class Calculator:
    def __init__(self, startValues, maxValues, polynomCoefs):
        self.values = [max(0, min(1, val)) for val in startValues]
        self.maxValues = [max(0, min(1, val)) for val in maxValues]
        self.functions = self.initFunctions(polynomCoefs)

    def initFunctions(self, coefs):
        functions = []
        for coef_set in coefs:
            num_coefs = len(coef_set)

            if num_coefs == 2:
                polynomial = pn.LinearPolynomial(*coef_set)
            elif num_coefs == 3:
                polynomial = pn.QuadraticPolynomial(*coef_set)
            elif num_coefs == 4:
                polynomial = pn.CubicPolynomial(*coef_set)
            else:
                raise ValueError(f"Неподдерживаемое количество коэффициентов: {num_coefs}")

            functions.append(polynomial)

        return functions

    def calculate(self, timeIntervals):
        solution = odeint(self.calcFunctions, self.values, timeIntervals)
        return solution

    def calcFunctions(self, u, t):
        [L1_t, L2_t, L3_t, L4_t, L5_t, L6_t, L7_t, L8_t, L9_t, L10_t, L11_t, L12_t, L13_t, L14_t, L15_t] = u

        # НОВАЯ ПРОСТАЯ И ДИНАМИЧНАЯ МОДЕЛЬ
        
        # Эпидемические волны и фазы
        epidemic_wave1 = 0.5 + 0.4 * math.sin(4 * math.pi * t) * math.exp(-2 * t)  # Затухающие колебания
        epidemic_wave2 = 0.3 + 0.5 * t * (1-t) * (1-t)  # Пик в начале, затем спад
        outbreak_phase = math.exp(-5 * (t - 0.3)**2)  # Гауссов пик в середине
        
        # Влияние полиномов (сильнее, чем раньше)
        poly_effects = []
        for i, func in enumerate(self.functions):
            if i < 15:  # Для каждого параметра свой полином
                poly_effects.append(0.3 * func.calc(u[i % 15]))
            else:
                poly_effects.append(0.2 * func.calc(u[(i-15) % 15]))
        
        # РЕАЛИСТИЧНАЯ ДИНАМИКА для каждого параметра
        
        # L1 - Летальность (растет с развитием эпидемии, потом падает)
        dL1_dx = 1.5 * (epidemic_wave2 * 0.8 - L1_t) + poly_effects[0]
        
        # L2 - Инфицированные (волнообразно с пиками)
        dL2_dx = 2.0 * (epidemic_wave1 * 0.9 - L2_t) + poly_effects[1] + 0.1 * L6_t * (1 - L5_t)
        
        # L3 - Население региона (медленные изменения)
        dL3_dx = 0.3 * (outbreak_phase * 0.6 - L3_t) + poly_effects[2] - 0.05 * L1_t
        
        # L4 - Госпитализированные (следует за инфицированными с задержкой)
        dL4_dx = 1.2 * ((epidemic_wave1 * 0.7 + 0.2 * L2_t) - L4_t) + poly_effects[3]
        
        # L5 - Изолированность (обратно пропорциональна скорости распространения)
        dL5_dx = 1.0 * (outbreak_phase * 0.8 * (1 - L6_t) - L5_t) + poly_effects[4]
        
        # L6 - Скорость распространения (быстрые изменения)
        dL6_dx = 1.8 * (epidemic_wave1 * (1 - L7_t * 0.5) - L6_t) + poly_effects[5]
        
        # L7 - Доступность лекарств (постепенно улучшается)
        dL7_dx = 0.8 * ((0.3 + 0.6 * t + outbreak_phase * 0.3) - L7_t) + poly_effects[6]
        
        # L8 - Тяжесть симптомов (зависит от штамма/мутаций)
        dL8_dx = 1.1 * (epidemic_wave2 * 0.6 + 0.2 * math.sin(6 * math.pi * t) - L8_t) + poly_effects[7]
        
        # L9 - Умершие (интегрируется от летальности)
        dL9_dx = 0.7 * (L1_t * L2_t * 0.8 - L9_t) + poly_effects[8]
        
        # L10 - Уровень медицины (медленно растет)
        dL10_dx = 0.5 * ((0.4 + 0.4 * t) - L10_t) + poly_effects[9] + 0.1 * L7_t
        
        # L11 - Инкубационный период (изменяется со штаммами)
        dL11_dx = 0.9 * (epidemic_wave2 * 0.5 + 0.1 * math.cos(3 * math.pi * t) - L11_t) + poly_effects[10]
        
        # L12 - Период развития болезни
        dL12_dx = 0.8 * (outbreak_phase * 0.7 + 0.2 * L8_t - L12_t) + poly_effects[11]
        
        # L13 - Период реабилитации (обратно пропорционален уровню медицины)
        dL13_dx = 0.6 * (epidemic_wave1 * 0.6 * (1 - L10_t * 0.5) - L13_t) + poly_effects[12]
        
        # L14 - Устойчивость к лекарствам (растет со временем)
        dL14_dx = 0.7 * ((0.2 + 0.5 * t + 0.2 * L8_t) - L14_t) + poly_effects[13]
        
        # L15 - Степень осложнений
        dL15_dx = 1.0 * (epidemic_wave2 * 0.8 + 0.1 * L14_t - L15_t) + poly_effects[14]

        derivatives = [dL1_dx, dL2_dx, dL3_dx, dL4_dx, dL5_dx, dL6_dx, dL7_dx, dL8_dx, dL9_dx, dL10_dx, dL11_dx, dL12_dx, dL13_dx, dL14_dx, dL15_dx]

        # Очень мягкие ограничения
        for i in range(len(derivatives)):
            if u[i] < 0.02:
                derivatives[i] += 0.2 * (0.02 - u[i])
            elif u[i] > 0.98:
                derivatives[i] -= 0.2 * (u[i] - 0.98)
            
            # Ограничение скорости
            derivatives[i] = max(-1.5, min(1.5, derivatives[i]))

        return derivatives