import polynoms as pn
import numpy as np
from scipy.integrate import odeint
class Calculator:
    def __init__(self, startValues, maxValues, polynomCoefs):
        self.values = startValues
        self.maxValues = maxValues
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

        q1 = 0.1 if t <= 0.2 else (0.4 if t <= 0.5 else 0.6)
        q2 = 0.2 if t <= 0.2 else (0.4 if t <= 0.5 else 0.6)
        q3 = 0.5
        q4 = 0.7 if t <= 0.3 else (0.5 if t <= 0.6 else 0.2)
        q5 = 0.5 if t <= 0.3 else (0.3 if t <= 0.6 else 0.2)

        dL1_dx = 1 / 0.5 * (q4 - self.functions[0].calc(L3_t) * (q1 + q2 + q4 + q5))
        dL2_dx = 1 / 0.7 * (self.functions[1].calc(L1_t) * self.functions[2].calc(L4_t) * self.functions[3].calc(L6_t) - self.functions[4].calc(L7_t) * (q1 + q4))
        dL3_dx = 1 / 0.3 * (self.functions[5].calc(L6_t) * self.functions[6].calc(L10_t) * self.functions[7].calc(L14_t) * (q2 + q5) - self.functions[8].calc(L5_t))
        dL4_dx = 1 / 0.5 * (q4 + q5)
        dL5_dx = 1 / 0.8 * ((q4 + q5) - (self.functions[9].calc(L2_t) * self.functions[10].calc(L6_t)))
        dL6_dx = 1 / 0.5 * (self.functions[11].calc(L2_t) * q5 - (q1 + q4))
        dL7_dx = 1 / 0.5 * (self.functions[12].calc(L14_t) * (q2 + q4) - self.functions[13].calc(L2_t) * self.functions[14].calc(L13_t) * self.functions[15].calc(L15_t))
        dL8_dx = 1 / 0.5 * (self.functions[16].calc(L9_t) * self.functions[17].calc(L13_t) * self.functions[18].calc(L15_t) - q1)
        dL9_dx = 1 / 0.5 * (self.functions[19].calc(L1_t))
        dL10_dx = 1 / 0.5 * (self.functions[20].calc(L7_t) * (q1 + q2 + q3 + q4 + q5) - self.functions[21].calc(L4_t) *self.functions[22].calc(L12_t) * self.functions[23].calc(L13_t))
        dL11_dx = 1 / 0.6 * q1
        dL12_dx = 1 / 0.3 * (-(q1 * self.functions[24].calc(L7_t)))
        dL13_dx = 1 / 0.9 * (- q1)
        dL14_dx = 1 / 0.5 * (self.functions[25].calc(L8_t) * self.functions[26].calc(L12_t) - q2)
        dL15_dx = 1 / 0.7 * (self.functions[27].calc(L9_t) - q1)

        return [dL1_dx, dL2_dx, dL3_dx, dL4_dx, dL5_dx, dL6_dx, dL7_dx, dL8_dx, dL9_dx, dL10_dx, dL11_dx, dL12_dx, dL13_dx, dL14_dx, dL15_dx]

