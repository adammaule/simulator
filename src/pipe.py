import math
from src.fluid import Fluid
from src.state import NodeState

class Pipe:
    
    
    def __init__(self, L: float, D: float, roughness: float, fluid: Fluid, vertical_depth: float):
        
        # Класс трубопровода для расчета гидравлических потерь в НКТ и шлейфе
        self.L = L # длина dx [м]
        self.D = D # диаметр трубы/ствола [м]
        self.roughness = roughness # абсолютная шероховатость стенки [м]
        self.vertical_depth = vertical_depth # вертикальная глубина [м]
        self.fluid = fluid # модель флюида

    def get_lambda(self, Re: float) -> float:
        
        # Расчёт коэффициента трения лямбда
        # Защита от нулевого дебита
        if Re < 1e-10:
            return 0
        # Ламинарный режим
        if Re < 2300:
            return 64 / Re
        # Турбулентный режим
        # Начальное приближение
        lambda1 = 0.02
        for _ in range(100):
            # Формула итерации
            lambda2 = (-2 * math.log10(self.roughness / (3.7 * self.D) + 2.51 / (Re * math.sqrt(lambda1))))**(-2)
            if abs(lambda2 - lambda1) < 1e-6:
                return lambda2
            lambda1 = lambda2
        return lambda1

    def dP(self, P: float, q: float) -> NodeState:
        
        # Расчёт перепада давления и состояния покоя
        # P: давление в узле (атм), q: дебит при стандартных условиях (ст.м3/сут)
        # Свойства газа при текущем давлении
        rho = self.fluid.get_rho(P)
        mu = self.fluid.get_mu(P)
        mu_pas = mu / 1000 # Перевод сП в Па*с для Re
        bg = self.fluid.get_bg(P)
        # Расчет скорости газа
        v = (4 * q * bg) / (math.pi * self.D**2 * 86400)
        # Число Рейнольдса
        Re = (rho * v * self.D) / mu_pas
        # Коэффициент трения
        lamb = self.get_lambda(Re)
        # Перепад давления по Дарси-Вейсбаху
        friction = lamb * (self.L / self.D) * (rho * v**2 / 2)
        hydrostatic = rho * 9.81 * self.vertical_depth
        dP = (friction + hydrostatic) / 101325
        # Формирование состояния
        return NodeState(
            P_in = P,
            P_out = P - dP,
            dP = dP,
            q_std = q,
            q_res = q * bg,
            v = v,
            rho = rho
        )