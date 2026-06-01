from src.state import NodeState

class DCS:

    # Класс дожимной компрессорной станции (ДКС).
    def __init__(self, CR: float, P_line: float, q_ext: float = 0.0):
        
        self.CR = CR # степень сжатия (Compression Ratio)
        self.P_line = P_line # давление в магистрали (константа), атм  
        self.q_ext = q_ext # дебит стороннего газа, поступающего на манифолд, ст.м3/сут

    def P_in(self) -> float:
        
        # Расчет давления на входе в ДКС
        # Если CR = 1, станция отключена и давление на входе равно давлению в линии
        if self.CR <= 1:
            return self.P_line
        P_in = self.P_line / self.CR
        return P_in

    def state(self, q_cluster: float) -> NodeState:
        
        # Формирует объект состояния для ДКС
        # q_cluster_std: Суммарный дебит трех скважин куста, ст.м3/сут
        P_in = self.P_in()
        P_out = self.P_line
        # Общий дебит через ДКС включает газ куста и сторонний газ
        q_total = q_cluster + self.q_ext
        # Для ДКС поля q_res, v, rho могут быть None
        return NodeState(
            P_in = P_in,
            P_out = P_out,
            dP = P_in - P_out,
            q_std = q_total,
            q_res = None,
            v = None,
            rho = None
        )