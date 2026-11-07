import math
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt.QtCore import QTimer
import serial
import time

# Configuração da Porta Série (ajuste para a sua porta: "COM3", "COM4" no Windows ou "/dev/ttyUSB0" no Linux)
PORT = "COM4"
BAUD_RATE = 115200
TIMEOUT = 1
MAX_DISTANCE = 200  # Alcance máximo visualizado em centímetros

array = np.full(181, np.nan)
current_angle = 90  # Posição atual do feixe do radar


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


def setup_radar_grid(win):
  """Desenha os arcos semicirculares de distância e os raios dos ângulos."""
  # Arcos de distância (semi-círculos a 50cm, 100cm, 150cm e 200cm)
  for r in [50, 100, 150, 200]:
    angles = np.linspace(0, np.pi, 100)
    x = r * np.cos(angles)
    y = r * np.sin(angles)
    win.plot(
        x,
        y,
        pen=pg.mkPen(color=(0, 120, 0, 140), width=1, style=pg.QtCore.Qt.DashLine),
    )

    # Marcadores de texto para as distâncias
    text = pg.TextItem(f"{r} cm", color=(0, 220, 0, 180), anchor=(0.5, 1))
    text.setPos(0, r)
    win.addItem(text)

  # Linhas radiais dos ângulos (0°, 30°, 60°, 90°, 120°, 150°, 180°)
  for angle in [0, 30, 60, 90, 120, 150, 180]:
    rad = math.radians(angle)
    x_end = MAX_DISTANCE * math.cos(rad)
    y_end = MAX_DISTANCE * math.sin(rad)
    win.plot(
        [0, x_end],
        [0, y_end],
        pen=pg.mkPen(
            color=(0, 100, 0, 100), width=1, style=pg.QtCore.Qt.DotLine
        ),
    )

    # Etiquetas dos ângulos na extremidade do radar
    text = pg.TextItem(f"{angle}°", color=(0, 220, 0, 180))
    text.setPos(
        (MAX_DISTANCE + 12) * math.cos(rad), (MAX_DISTANCE + 12) * math.sin(rad)
    )
    win.addItem(text)


def main():
  global current_angle

  app = pg.mkQApp("Radar ESP32")

  # Configuração da janela gráfica
  win = pg.PlotWidget()
  win.setBackground("#050B05")  # Fundo verde-escuro estilo monitor militar
  win.setAspectLocked(True)
  win.setXRange(-MAX_DISTANCE - 25, MAX_DISTANCE + 25)
  win.setYRange(-10, MAX_DISTANCE + 25)
  win.setTitle("SISTEMA DE RADAR ESP32 + HC-SR04", color="#00FF00", size="14pt")

  # Desenha a grelha polar
  setup_radar_grid(win)

  # Camada dos pontos de obstáculos detetados (Vermelho Néon)
  scatter = pg.ScatterPlotItem(
      size=9, pen=pg.mkPen(None), brush=pg.mkBrush(255, 40, 40, 230)
  )
  win.addItem(scatter)

  # Linha de varrimento do feixe (Linha Verde Néon que roda com o servo)
  sweep_line = pg.PlotCurveItem(
      pen=pg.mkPen(color=(0, 255, 120, 220), width=2)
  )
  win.addItem(sweep_line)

  # Conexão à porta Série
  try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
    time.sleep(2)
    ser.reset_input_buffer()
    print(f"Conectado com sucesso à porta {PORT}.")
  except Exception as e:
    print(f"Erro ao abrir a porta {PORT}: {e}")
    print(
        "Aviso: Certifique-se de que o Monitor Série do Arduino IDE / VS Code"
        " está FECHADO para libertar a porta!"
    )
    return

  last_angle = None
  rejections = 0

  def update():
    nonlocal last_angle, rejections
    global current_angle

    while ser.in_waiting:
      result = parse_line(ser.readline())
      if result is None:
        continue

      angle, distance = result

      if last_angle is None:
        last_angle = angle

      # Filtro de salto de passos do servo
      if abs(angle - last_angle) not in (0, 5):
        rejections += 1
        if rejections == 10:
          last_angle = None
          rejections = 0
        continue
      else:
        last_angle = angle
        rejections = 0

      current_angle = angle

      # Rejeita leituras fora da escala útil do sensor (2 cm a 200 cm)
      if not 2 <= distance <= MAX_DISTANCE:
        distance = np.nan

      array[angle] = distance

  def draw():
    # Desenha todos os alvos armazenados no array
    x_coords = []
    y_coords = []
    for angle in range(181):
      dist = array[angle]
      if not np.isnan(dist):
        x, y = convert_to_cartesian(angle, dist)
        x_coords.append(x)
        y_coords.append(y)
    scatter.setData(x_coords, y_coords)

    # Desenha a linha do feixe de varrimento atual
    sweep_x, sweep_y = convert_to_cartesian(current_angle, MAX_DISTANCE)
    sweep_line.setData([0, sweep_x], [0, sweep_y])

  def tick():
    update()
    draw()

  timer = QTimer()
  timer.timeout.connect(tick)
  timer.start(30)

  win.resize(1000, 550)
  win.show()
  app.exec()


if __name__ == "__main__":
  main()