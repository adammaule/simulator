from src.fluid import Fluid

class ResProps:
    
    def __init__(self, P: float, V: float, T: float):
        
        # Задание начальных свойств пласта
        self.P = P # давление P1 в паласте (баке) [атм]
        self.V = V # объём пласта [м3]
        self.T = T # температура пласта [К]

class Reservoir:

    def __init__(self, ResProps, Fluid):
        
        # Класс для расчёта материального баланса 
        self.resprops = ResProps # начальные свойства пласта
        self.fluid = Fluid # модель флюида

    def P2(self, q_total: float, dt: float = 1.0) -> float:
        
        # Пластовое давление по формуле материального баланса
        # q_total: суммарная добыча из пласта (ст.м3/сут), dt: шаг по времени (сут)
        P = self.resprops.P
        V = self.resprops.V
        z = self.fluid.get_z(P)
        rho = self.fluid.get_rho(P)
        rho_с = self.fluid.rho_c # стандартная плотность
        P2 = P - (z * rho_с / rho) * (q_total / V) * dt
        return P2