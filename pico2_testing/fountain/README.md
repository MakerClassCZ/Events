# Quick test of Pico2 with RP2350 in a task that uses floating point

I performed the test by calculating an animated pattern on a 320x240 16-bit display (RGB565) with an ST7789 controller connected via SPI.
First, I did a simple test by rendering the pattern to a framebuffer and then transferring it to the display (main-single_buffer-no_dma.c). This test can also be done for comparison with RP2040.
The **main test** used a double buffer and **DMA** to allow the next frame to be counted during the data transfer. Double buffer cannot be used on the RP2040 because it does not have large enough RAM.
It turned out that the bottle neck is mainly transferring data from the buffer to the display over SPI.

The programs were compiled using PicoSDK 2.0.1.

## Main test

### RP2350 ARM
| Core Frequency |SPI Frequnency  | Calculating Time | DMA Waiting Time | Total Time |FPS |
|--|--|--|--|--|--|
| 154 MHz | 77 MHz | 11.8 ms | 7.2 ms | 19 ms | 52.8 FPS
| 308 MHz | 77 MHz | 4.7 ms | 14.3 ms | 19 ms | 52.8 FPS

### RP2350  RISC-V
| Core Frequency |SPI Frequnency  | Calculating Time | DMA Waiting Time | Total Time |FPS |
|--|--|--|--|--|--|
| 154 MHz | 77 MHz | 126 ms | 0 ms | 126 ms | 8 FPS
| 308 MHz | 77 MHz | 64 ms | 0 ms | 64 ms | 15.7 FPS

## Simple test

| TEST | FPS |
|--|--|
| RP2040 | 6.9 FPS |
| RP2350 ARM | 20.8 FPS |
| RP2350 RISC-V SDK2.0| 3.8 FPS |
| RP2350 RISC-V SDK2.0.1| 6 FPS |
| CircuitPython 9.2 alfa|1.2 FPS |
| CircuitPython 9.2 alfa @348MHz |2.9 FPS |


