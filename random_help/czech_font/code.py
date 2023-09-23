import board
from adafruit_display_text import label
from extra_font import ExtraFont

display = board.DISPLAY

font = ExtraFont("/czech.bdf")

text = "Příliš žluťoučký kůň pěje ďábelské ódy!"
text_label = label.Label(font, text=text, color=0xFFFFFF)
text_label.x = 0
text_label.y = 110

display.show(text_label)


while True:
    pass

