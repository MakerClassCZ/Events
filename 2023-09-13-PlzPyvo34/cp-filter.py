import time

import adafruit_htu31d

import board
import displayio
from ulab import numpy as np

display = board.DISPLAY
display.root_group.hidden = True

h = np.array([
    0.001867519746044820,
    0.002275293677911463,
    0.002692845467883248,
    0.003119400211540369,
    0.003554151391578438,
    0.003996262853518041,
    0.004444870878876082,
    0.004899086349965267,
    0.005357997000181999,
    0.005820669743355830,
    0.006286153075466025,
    0.006753479541784039,
    0.007221668262275161,
    0.007689727507889525,
    0.008156657320192493,
    0.008621452166627776,
    0.009083103623574271,
    0.009540603079249766,
    0.009992944448431896,
    0.010439126890909214,
    0.010878157525543523,
    0.011309054131818317,
    0.011730847830767882,
    0.012142585737226980,
    0.012543333575412086,
    0.012932178249941664,
    0.013308230364524597,
    0.013670626680692492,
    0.014018532509122373,
    0.014351144026291085,
    0.014667690509420725,
    0.014967436482914990,
    0.015249683769748768,
    0.015513773441556675,
    0.015759087661469738,
    0.015985051414072162,
    0.016191134117190663,
    0.016376851110586923,
    0.016541765016997088,
    0.016685486971350718,
    0.016807677714403370,
    0.016908048547430839,
    0.016986362145057821,
    0.017042433223728004,
    0.017076129063764694,
    0.017087369883420026,
    0.017076129063764694,
    0.017042433223728004,
    0.016986362145057821,
    0.016908048547430839,
    0.016807677714403370,
    0.016685486971350718,
    0.016541765016997088,
    0.016376851110586923,
    0.016191134117190663,
    0.015985051414072162,
    0.015759087661469738,
    0.015513773441556675,
    0.015249683769748768,
    0.014967436482914990,
    0.014667690509420725,
    0.014351144026291085,
    0.014018532509122373,
    0.013670626680692492,
    0.013308230364524597,
    0.012932178249941664,
    0.012543333575412086,
    0.012142585737226980,
    0.011730847830767882,
    0.011309054131818317,
    0.010878157525543523,
    0.010439126890909214,
    0.009992944448431896,
    0.009540603079249766,
    0.009083103623574271,
    0.008621452166627776,
    0.008156657320192493,
    0.007689727507889525,
    0.007221668262275161,
    0.006753479541784039,
    0.006286153075466025,
    0.005820669743355830,
    0.005357997000181999,
    0.004899086349965267,
    0.004444870878876082,
    0.003996262853518041,
    0.003554151391578438,
    0.003119400211540369,
    0.002692845467883248,
    0.002275293677911463,
    0.001867519746044820,
])

#sampling frequency
dt = 50_000_000 # 20Hz

# Wait until after deadline_ns has passed
def sleep_deadline(deadline_ns):
    while time.monotonic_ns() < deadline_ns:
        pass

i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_htu31d.HTU31D(i2c)


data = np.zeros(len(h))
t0 = deadline = time.monotonic_ns()
offset = sensor.temperature

while True:

    deadline += dt
    sleep_deadline(deadline)
    value = (sensor.temperature - 0)
    data = np.roll(data, 1)
    data[-1] = value
    filtered = np.sum(data * h)
    #print((filtered, value))
    print(f">data:{value}\n>filtered:{filtered}")
    


