import pandas as pd

class LinearInterpolator:
    
    def __init__(self, xs: list, ys: list):

        if len(xs) == len(ys):
            xy = {'x': xs, 'y': ys}
            xy = pd.DataFrame(xy)
            xy.sort_values('x', ascending = True)
            self.xs = list(xy['x'])
            self.ys = list(xy['y'])
        else:
            print('Длины массивов должны быть одинаковыми')
            pass
    
    def predict(self, xp: float):

        if xp > self.xs[-1]:
            x2 = self.xs[-1]
            x1 = self.xs[-2]
            y2 = self.ys[-1]
            y1 = self.ys[-2]
            yp = y2 + (y2 - y1) / (x2 - x1)*(xp - x2)
            print('xp лежит за пределами диапазона x, будет произведена экстраполяция')
        elif xp < self.xs[0]:
            x2 = self.xs[0]
            x1 = self.xs[1]
            y2 = self.ys[0]
            y1 = self.ys[1]
            yp = y2 + (y2 - y1) / (x2 - x1)*(xp - x2)
            print('xp лежит за пределами диапазона x, будет произведена экстраполяция')
        else:
            for i in range(0, len(self.xs)):
                if self.xs[i] > xp:
                    x2 = self.xs[i]
                    x1 = self.xs[i-1]
                    y2 = self.ys[i]
                    y1 = self.ys[i-1]
                    yp = y1 + (y2 - y1) / (x2 - x1)*(xp - x1)
                    break
                elif self.xs[i] == xp:
                    yp = self.ys[i]
                    break
        return yp