import serial
import time
import math
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt.QtCore import QTimer

PORT = "COM4"
BAUD_RATE = 115200
TIMEOUT = 1

array = np.full(181, np.nan)

def parse_line(raw):
    """Recebe os bytes de uma linha e devolve (angulo, distancia) ou None."""
    try:
        text = raw.decode("utf-8", errors="ignore").strip()
        angle_str, distance_str = text.split(",")
        angle = int(angle_str)
        distance = int(distance_str)
    except ValueError:
        return None

    if not 0 <= angle <= 180:
        return None

    return angle, distance

def convert_to_cartesian(angle, distance):
    """Converte coordenadas polares (ângulo, distância) para cartesianas (x, y)."""
    radians = math.radians(angle)
    x = distance * math.cos(radians)
    y = distance * math.sin(radians)
    return x, y


def main():
    with serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
        time.sleep(2)
        ser.reset_input_buffer()
        ser.readline()              

        try:
            last_angle = None 
            rejections = 0

            def update():
                nonlocal last_angle, rejections

                while ser.in_waiting:
                    result = parse_line(ser.readline())
                    if result is None:
                        continue

                    angle, distance = result

                    if last_angle is None:
                        last_angle = angle
                
                    if abs(angle - last_angle) not in (0, 5):
                        rejections = rejections + 1
                        if rejections == 10:
                            last_angle = None
                            rejections = 0
                        continue
                    else: 
                        last_angle = angle
                        rejections = 0

                    if not 2 <= distance <= 400:
                        distance = np.nan
                    
                    array[angle] = distance  # armazena a distância no array  

            app = pg.mkQApp()

            win = pg.PlotWidget(); win.setAspectLocked(True); win.setXRange(-100, 100); win.setYRange(0, 100)

            scatter = pg.ScatterPlotItem(size=5, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
            win.addItem(scatter)

            def draw():
                x = []
                y = []
                for angle in range(181):
                    distance = array[angle]
                    if not np.isnan(distance):
                        x_coord, y_coord = convert_to_cartesian(angle, distance)
                        x.append(x_coord)
                        y.append(y_coord)
                scatter.setData(x, y)

            def tick():
                update()
                draw()

            timer = QTimer(); timer.timeout.connect(tick); timer.start(50)

            win.resize(900, 450)

            win.show(); app.exec()
            
        except KeyboardInterrupt:
            print("A terminar...")

if __name__ == "__main__":
    main()