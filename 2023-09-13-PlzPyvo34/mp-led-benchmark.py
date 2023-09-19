import time, machine

led = machine.Pin(25, machine.Pin.OUT)
N = 100_000


def timeit(func):
    def wrapper(*args, **kwargs):
        n = N
        t = time.ticks_us
        t0 = t()
        result = func(*args, **kwargs)
        t1 = t()
        dt = t1 - t0
        print(f'\033[0;30;46m {dt * 1e-6:.3f} s, {n/dt*1e3:.1f} kHz \033[1;30;49m\n')
        return result
    return wrapper

@timeit
def blink1():
    for i in range(N):
        led.on()
        led.off()


@timeit
def blink2(n):
    on = led.on
    off = led.off
    r = range(n)
    for i in r:
        on()
        off()

@timeit
@micropython.native
def blink3(n):
    on = led.on
    off = led.off
    r = range(n)
    for i in r:
        on()
        off()

@timeit
@micropython.asm_thumb
def blink4(r0):
    #r1 SIO_BASE (0xd0000000)
    #r2 GPIO25
    mov(r1, 0xd0)
    lsl(r1, r1, 24)
    mov(r2, 1)
    lsl(r2, r2, 25)

    # r4 0x14 SET
    mov(r3, 0x14)
    add(r4, r1, r3)

    # r5 0x18 CLR
    mov(r3, 0x18)
    add(r5, r1, r3)

    mov(r3, 1)

    label(LOOP)
    str(r2, [r4, 0])
    str(r2, [r5, 0])
    sub(r0, r0, r3)
    bne(LOOP)

print("for i in range(N):\n  led.on()\n  led.off()\033[1;30;49m\n")
input()
input("Start - naive\n")




t0 = time.ticks_us()

for i in range(N):
    led.on()
    led.off()

t1 = time.ticks_us()
dt = t1 -t0
print(f'\033[0;30;46m {dt * 1e-6:.3f} s, {N/dt*1e3:.1f} kHz \033[1;30;49m\n')

input("Continue - move to function\n")

blink1()

input("Continue - local variables\n")

blink2(N)

input("Continue - native code\n")

blink3(N)

input("Continue - :-)\n")

blink4(N)


