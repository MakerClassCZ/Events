import time
import displayio
import rainbowio
from mb_setup import setup, qr_gen, text_gen
from adafruit_bitmap_font import bitmap_font

import gc

# minimum display refresh time (seconds)
ttr = 40

(display, touch, led_matrix, colors) = setup(time_to_refresh=ttr)


wb_palette = displayio.Palette(2)
wb_palette[0] = colors['white']
wb_palette[1] = colors['black']

font = bitmap_font.load_font("/cozette-13.pcf")

# prepare the slides
def make_slide0():
    slide = displayio.Group()


    label = text_gen("Vláďa Smitka", 15, 20, font, 3)
    slide.append(label)
    label = text_gen("@smitka", 90, 50, font)
    slide.append(label)
    label = text_gen("Lynt services s.r.o.", 5, 80, font, 2)
    slide.append(label)
    label = text_gen("Yes, it runs Python!", 60, 110, font)
    slide.append(label)

    bmp = displayio.Bitmap(display.width, display.height, 1)
    background = displayio.TileGrid(bmp, pixel_shader=wb_palette)
    
    screen = displayio.Group()
    screen.append(background)
    screen.append(slide)
    
    display.show(screen)
    display.refresh()


def make_slide1():
    slide = displayio.Group()

    qr_bitmap = qr_gen("cislo_ticketu")
    scale = display.height // qr_bitmap.height
    tile = displayio.TileGrid(qr_bitmap, pixel_shader=wb_palette)

    code_group = displayio.Group(
        x=(display.width - qr_bitmap.width*scale) // 2,
        y=(display.height - qr_bitmap.height*scale) // 2,
        scale=scale
    )
    code_group.append(tile)
    slide.append(code_group)
    label = text_gen("PyCon", 4, 20, font, 2)
    slide.append(label)
    label = text_gen("Ticket", 180, 20, font, 2)
    slide.append(label)

    bmp = displayio.Bitmap(display.width, display.height, 1)
    background = displayio.TileGrid(bmp, pixel_shader=wb_palette)
    
    screen = displayio.Group()
    screen.append(background)
    screen.append(slide)
    
    display.show(screen)
    display.refresh()


def make_slide2():
    slide = displayio.Group()


    label = text_gen("Ask me about", 15, 20, font, 3)
    slide.append(label)
    label = text_gen("Python on MCU", 5, 70, font, 3)
    slide.append(label)

    bmp = displayio.Bitmap(display.width, display.height, 1)
    background = displayio.TileGrid(bmp, pixel_shader=wb_palette)
    
    screen = displayio.Group()
    screen.append(background)
    screen.append(slide)
    
    display.show(screen)
    display.refresh()


def make_slide3():

    with open("/lynt.bmp", "rb") as f:
        slide = displayio.Group()
        
        bitmap = displayio.OnDiskBitmap(f)
        slide.append(displayio.TileGrid(
            bitmap, pixel_shader=bitmap.pixel_shader))
        
        label = text_gen("The proud sponsor of PyCon CZ 23", 28, 110, font, 1)
        slide.append(label)
        
        bmp = displayio.Bitmap(display.width, display.height, 1)
        background = displayio.TileGrid(bmp, pixel_shader=wb_palette)
        
        screen = displayio.Group()
        screen.append(background)
        screen.append(slide)
        
        display.show(screen)
        display.refresh()

# display remaing time to refresh on the LED matrix
# each LED represents 45 seconds (when time to refresh = 180s)

def time_to_refresh():
    led_matrix.fill(colors['red'])
    t = display.time_to_refresh
    q = ttr // 4
    
    if t < 3*q:
        led_matrix[0] = colors['black']
    if t < 2*q:
        led_matrix[1] = colors['black']
    if t < q:
        led_matrix[2] = colors['black']

    led_matrix.show()
    time.sleep(2)
    led_matrix.fill(colors['black'])
    led_matrix.show()


# display slide
def show_slide(display, n):

    if display.time_to_refresh == 0:
        print("Displaying slide", n)
        slides = [make_slide0, make_slide1, make_slide2, make_slide3]
        slides[n]()

    else:
        print("Wait:", display.time_to_refresh)
        time_to_refresh()


i = 0
wheel = False

while True:

    for t in touch:
        t.update()

    if touch[0].rose:
        show_slide(display, 0)
        gc.collect()

    if touch[1].rose:
        show_slide(display, 1)
        gc.collect()

    if touch[2].rose:
        show_slide(display, 2)
        gc.collect()

    if touch[3].rose:
        show_slide(display, 3)
        gc.collect()

    if touch[4].rose:
        if not (wheel := not wheel):
            led_matrix.fill(colors['black'])
            led_matrix.show()

    if wheel:
        led_matrix[0] = (rainbowio.colorwheel(i))
        led_matrix[1] = (rainbowio.colorwheel(i+64))
        led_matrix[2] = (rainbowio.colorwheel(i+128))
        led_matrix[3] = (rainbowio.colorwheel(i+192))
        led_matrix.show()

    i = (i + 1) % 256
