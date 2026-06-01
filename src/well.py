import math
from src.fluid import Fluid
from src.pipe import Pipe

class Well:
    
    # Класс скважины, описывающий приток газа из пласта (закон Дарси).
    def __init__(self, k: float, h: float, re: float, rw: float, fluid: Fluid, pipe: Pipe = None):
        
        self.k = k # проницаемость [мД]
        self.h = h # эффективная толщина пласта [м]
        self.re = re # радиус скважины [м]
        self.rw = rw # радиус контура питания [м]
        self.fluid = fluid # модель флюида
        self.pipe = pipe # модель скважины
        self.beta = 0.00852702 # коэффициент перевода единиц

    def q(self, P_res: float, P_bhp: float) -> float:

        # Расчет коэффициента продуктивности C
        mu = self.fluid.get_mu(P_res) # вязкость при пластовом давлении
        C = (self.beta * self.k * self.h) / (mu * math.log(self.re / self.rw))
        # Расчет дебита газа по закону Дарси (ст.м3/сут)
        if P_bhp >= P_res:
            return 0.0
        q_std = C * (P_res - P_bhp)
        return q_std