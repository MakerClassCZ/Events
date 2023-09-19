import time
import board
import neopixel


pixel_pin = board.A0
num_pixels = 4
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=True, pixel_order=neopixel.RGBW
)


while True:
	pixels.fill((255, 0, 0, 0))
	time.sleep(1)

	pixels.fill((0, 255, 0, 0))
	time.sleep(1)

	pixels.fill((0, 0, 255, 0))
	time.sleep(1)

	pixels.fill((0, 0, 0, 255))
	time.sleep(1)