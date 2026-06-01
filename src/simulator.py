import numpy as np
from scipy.optimize import fsolve
from src.state import NodeState
from src.reservoir import Reservoir
from src.well import Well
from src.pipe import Pipe
from src.compressor import DCS


class FieldSimulator:

    # Класс-симулятор для нахождения гидравлического равновесия системы и моделирования разработки во времени
    def __init__(self, reservoir: Reservoir, wells: list[Well], pipes: list[Pipe], shlyf: Pipe, dcs: DCS):
        
        self.reservoir = reservoir # класс для расчёта материального баланса
        self.wells = wells # список из 3 объектов класса Well
        self.pipes = pipes # список из 3 объектов класса Pipe
        self.shlyf = shlyf # класс для расчёта dp
        self.dcs = dcs # класс для расчёта давления на входе в ДКС

    def solve(self, P_res: float) -> dict[str, NodeState]:
        
        # Нахождение рабочей точки: q1, q2, q3, P_man
        # P_res: текущее пластовое давление (атм)
        def equations(x):
            
            q1, q2, q3, P_man = x
            qs = [q1, q2, q3]
            res = []
            
            # Уравнения притока по Дарси для каждой скважины
            for i in range(3):
                # Состояние НКТ при заданном q и P_man
                state_well = self.pipes[i].dP(P_man, qs[i])
                # Перепад в трубе
                dP_tube = state_well.dP
                P_bhp = P_man + dP_tube
                q_calc = self.wells[i].q(P_res, P_bhp)
                res.append(qs[i] - q_calc)

            # Баланс давлений на манифольде
            q_total = sum(qs) + self.dcs.q_ext
            P_in_dcs = self.dcs.P_in()
            state_shlyf = self.shlyf.dP(P_in_dcs, q_total)
            dP_shlyf = state_shlyf.dP
            P_man_calc = P_in_dcs + dP_shlyf
            res.append(P_man - P_man_calc)
            return res

        # Начальное приближение
        initial_guess = [500, 500, 500, self.dcs.P_in() + 5]
        solution = fsolve(equations, initial_guess)
        # Дебиты положительные
        q_final = [max(0.0, i) for i in solution[:3]]
        P_man_final = solution[3]
        P_in_dcs = self.dcs.P_in()
        # Состояния объектов
        states: dict[str, NodeState] = {}
        # Cостояния скважин считаем через их трубы
        for i in range(3):
            states[f"well_{i+1}"] = self.pipes[i].dP(P_man_final, q_final[i])
        # Cостояние шлейфа
        states["shlyf"] = self.shlyf.dP(P_in_dcs, sum(q_final) + self.dcs.q_ext)
        # Cостояние ДКС
        states["DCS"] = self.dcs.state(sum(q_final))
        return states

    def run(self, N_days: int, dt: float = 1) -> list[dict]:
        
        # Динамическая симуляция на N_days
        history: list[dict] = []
        Gp_prev = 0
        for day in range(N_days):
            # Решение системы на текущем шаге
            step_state = self.solve(self.reservoir.resprops.P)
            q_total_cluster = sum(step_state[f"well_{i+1}"].q_std for i in range(3))
            Gp = Gp_prev + q_total_cluster * dt
            # Сохранение результатов
            history.append(
                {
                    "day": day,
                    "P_res": self.reservoir.resprops.P,
                    "q_1": step_state["well_1"].q_std,
                    "q_2": step_state["well_2"].q_std,
                    "q_3": step_state["well_3"].q_std,
                    "q_total": q_total_cluster,
                    "P_man": step_state["shlyf"].P_in,
                    "gp": Gp/1000,
                }
            )
            # Обновляем данные
            self.reservoir.resprops.P = self.reservoir.P2(q_total_cluster, dt)
            Gp_prev = Gp
            if day % 10 == 0:
                print(f"Шаг {day}/{N_days}: P_res = {self.reservoir.resprops.P:.2f} атм")
        return history