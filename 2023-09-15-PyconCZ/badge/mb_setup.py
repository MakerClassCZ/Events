import board
import time
import neopixel
import touchio
import displayio
import adafruit_ssd1680
from digitalio import DigitalInOut, Direction
from adafruit_debouncer import Debouncer
from adafruit_display_text import bitmap_label
import adafruit_miniqr



colors = {
        'black':  0x000000,
        'white':  0xFFFFFF,
        'red':    0xFF0000,
        'green':  0x00FF00,
        'blue':   0x0000FF,
        'yellow': 0xFFFF00,
}

def setup():

    # Define board pinout
    board_spi = board.SPI()  # Uses SCK and MOSI
    board_epd_cs = board.D41
    board_epd_dc = board.D40
    board_epd_reset = board.D39
    board_epd_busy = board.D42
    enable_display = DigitalInOut(board.D16)
    enable_display.direction = Direction.OUTPUT
    enable_display.value = False

    # Define touch buttons
    touch_threshold = 20000
    touch = []
    for pin in [board.D5,board.D4,board.D3,board.D2,board.D1]:
        tmp = touchio.TouchIn(pin)
        tmp.threshold = touch_threshold
        touch.append(Debouncer(tmp))

    led_matrix = neopixel.NeoPixel(board.D18, 4, brightness = 0.1, auto_write = False)



    # Define ePaper display resolution
    display_width = 250
    display_height = 122

    # Prepare ePaper display
    displayio.release_displays()
    display_bus = displayio.FourWire(
        board_spi, command = board_epd_dc, chip_select = board_epd_cs, reset = board_epd_reset, baudrate = 1000000
    )


    time.sleep(1)

    display = adafruit_ssd1680.SSD1680(
        display_bus, width = display_width, height = display_height, rotation = 270, busy_pin = board_epd_busy
    )
    

    return (display, touch, led_matrix, colors)


def qr_gen(data):
    qrcode = adafruit_miniqr.QRCode(qr_type=1)
    qrcode.add_data(data)
    qrcode.make()

    # bitmap the size of the matrix, plus border, monochrome (2 colors)
    qr_bitmap = displayio.Bitmap(qrcode.matrix.width + 2, qrcode.matrix.height + 2, 2)
    for i in range(qr_bitmap.width * qr_bitmap.height):
        qr_bitmap[i] = 0

    # transcribe QR code into bitmap
    for xx in range(qrcode.matrix.width):
        for yy in range(qrcode.matrix.height):
            qr_bitmap[xx + 1, yy + 1] = 1 if qrcode.matrix[xx, yy] else 0
    
    return qr_bitmap



def text_gen(text, x, y, font, scale = 1, color = colors['black']):

    label = bitmap_label.Label(font, text = text, color = color, scale = scale)
    label.x = x
    label.y = y
    return label