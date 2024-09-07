// TODO: remove unnecessary includes form testing
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "hardware/dma.h"
#include "pico/time.h"
#include "hardware/pll.h"
#include "hardware/clocks.h"
#include "hardware/structs/pll.h"
#include "hardware/structs/clocks.h"

// ST7789 display pins
#define SPI_PORT spi0
#define PIN_MISO 16
#define PIN_CS   21
#define PIN_SCK  18
#define PIN_MOSI 19
#define PIN_DC   17
#define PIN_RST  20
#define PIN_BL   16

// Display configuration
#define SCREEN_WIDTH  240
#define SCREEN_HEIGHT 320

// Colors in RGB565
#define ST7789_BLACK  0x0000
#define ST7789_WHITE  0xFFFF
#define ST7789_RED    0xF800
#define ST7789_GREEN  0x07E0
#define ST7789_BLUE   0x001F
#define ST7789_MAGENTA 0xF81F

// Drawing parameters
#define XS 1
#define YS 1
#define WIDTH2  (SCREEN_WIDTH/2)
#define HEIGHT2 (SCREEN_HEIGHT/2)
#define COL     ST7789_MAGENTA

// Enable performance measurement
#define ENABLE_PERFORMANCE_MEASUREMENT 1
#define PERFORMANCE_PRINT_INTERVAL 50

// Clock frequency in MHz (default 150 MHz)
#define CLOCK_MHZ  150

// Double buffer
#define BUFFER_SIZE (SCREEN_WIDTH * SCREEN_HEIGHT * 2)  // 16bit - 2 bytes per pixel
uint8_t framebuffer[2][BUFFER_SIZE];  // define 2 buffers
int current_buffer = 0;  // Index of the current buffer

// DMA channel
int dma_channel;

// Function prototypes
void dma_init(void);
void st7789_init(void);
void st7789_command(uint8_t cmd);
void st7789_data(uint8_t data);
void st7789_write(const uint8_t *buf, size_t len);
void st7789_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
void buffer_fill_color(uint8_t *buffer, uint16_t color);
void buffer_draw_pixel(uint8_t *buffer, uint16_t x, uint16_t y, uint16_t color);
void flush_framebuffer_dma(uint8_t *buffer);
void draw_frame(uint8_t *buffer, float a);
void print_performance_stats(uint32_t total_frame_time, uint32_t calc_time, uint32_t dma_wait_time);


// Main function
// - inicialization
// - main loop
// -- calculate drawing to buffer
// -- wait for empty DMA channel
// -- send data to display through DMA
// -- switch buffers
int main() {

    /*
    // Overclocking
    // also change it in st7789_init to half
    set_sys_clock_khz(CLOCK_MHZ * KHZ, false);
    
    clock_configure(
        clk_peri,                                         // perifery clock
        0,                                                // no offset
        CLOCKS_CLK_PERI_CTRL_AUXSRC_VALUE_CLK_SYS,        // CLK_SYS is the source
        CLOCK_MHZ * MHZ,                                        // source frequency
        CLOCK_MHZ * MHZ                                         // target clk_peri frequency
    );
    */


    // https://www.raspberrypi.com/documentation/pico-sdk/runtime.html#group_pico_stdio_1ga0e604311fb226dae91ff4eb17a19d67a
    stdio_init_all();
    // Initialize display
    st7789_init();
    // Initialize DMA
    dma_init();

    
    float a = 0;
    
    #if ENABLE_PERFORMANCE_MEASUREMENT
    absolute_time_t frame_start, calc_start, dma_wait_start, frame_end;
    uint32_t total_frame_time, calc_time, dma_wait_time;
    uint32_t frame_count = 0;
    #endif

    while (1) {
        #if ENABLE_PERFORMANCE_MEASUREMENT
        frame_start = get_absolute_time();
        #endif
        
        #if ENABLE_PERFORMANCE_MEASUREMENT
        calc_start = get_absolute_time();
        #endif
        // draw to current buffer
        draw_frame(framebuffer[current_buffer], a);
        #if ENABLE_PERFORMANCE_MEASUREMENT
        calc_time = absolute_time_diff_us(calc_start, get_absolute_time());
        #endif
        
        #if ENABLE_PERFORMANCE_MEASUREMENT
        dma_wait_start = get_absolute_time();
        #endif
        // wait for end of the previous DMA transfer
        dma_channel_wait_for_finish_blocking(dma_channel);
        #if ENABLE_PERFORMANCE_MEASUREMENT
        dma_wait_time = absolute_time_diff_us(dma_wait_start, get_absolute_time());
        #endif
        // send the current buffer to the display through DMA on background while preparing the next frame
        flush_framebuffer_dma(framebuffer[current_buffer]);
        // switch current buffer
        current_buffer = 1 - current_buffer;
     
        #if ENABLE_PERFORMANCE_MEASUREMENT
        frame_end = get_absolute_time();
        total_frame_time = absolute_time_diff_us(frame_start, frame_end);
        
        frame_count++;
        
        if (frame_count % PERFORMANCE_PRINT_INTERVAL == 0) {
            print_performance_stats(total_frame_time, calc_time, dma_wait_time);
        }
        #endif
        
        a += 0.1f;
    }

    return 0;
}

// Print performance measurement statistics
void print_performance_stats(uint32_t total_frame_time, uint32_t calc_time, uint32_t dma_wait_time) {
    #if ENABLE_PERFORMANCE_MEASUREMENT
    float fps = 1000000.0f / total_frame_time;  // Calculate FPS
    printf("FPS: %.2f, Total: %lu us, Calc: %lu us, DMA wait: %lu us\n", 
           fps, total_frame_time, calc_time, dma_wait_time);
    #endif
}

// Initialize DMA
void dma_init(void) {
    dma_channel = dma_claim_unused_channel(true);
    dma_channel_config c = dma_channel_get_default_config(dma_channel);
    channel_config_set_transfer_data_size(&c, DMA_SIZE_8);
    channel_config_set_dreq(&c, spi_get_dreq(SPI_PORT, true));
    dma_channel_configure(dma_channel, &c,
                          &spi_get_hw(SPI_PORT)->dr,  // Write address
                          NULL,  // Read address (set later)
                          BUFFER_SIZE,  // Transfer count
                          false  // Don't start yet
    );
}

// Initialize the ST7789 display
void st7789_init(void) {
    // Initialize SPI at 75 MHz (maximum tested speed for my LCD)
    spi_init(SPI_PORT, CLOCK_MHZ / 2 * MHZ);
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    
    // Initialize CS, DC and RST pins
    gpio_init(PIN_CS);
    gpio_set_dir(PIN_CS, GPIO_OUT);
    gpio_put(PIN_CS, 1);
    gpio_init(PIN_DC);
    gpio_set_dir(PIN_DC, GPIO_OUT);
    gpio_init(PIN_RST);
    gpio_set_dir(PIN_RST, GPIO_OUT);

    // Initialize backlight
    gpio_init(PIN_BL);
    gpio_set_dir(PIN_BL, GPIO_OUT);
    gpio_put(PIN_BL, 1);  // Turn on backlight

    // Reset display
    gpio_put(PIN_RST, 1);
    sleep_ms(5);
    gpio_put(PIN_RST, 0);
    sleep_ms(20);
    gpio_put(PIN_RST, 1);
    sleep_ms(150);

    // ST7789 initialization sequence
    // https://www.waveshare.com/wiki/File:ST7789_Datasheet.pdf
    st7789_command(0x01);  // Software reset
    sleep_ms(150);

    st7789_command(0x11);  // Sleep out
    sleep_ms(500);

    st7789_command(0x3A);  // Set color mode
    st7789_data(0x55);     // 16 bit color RGB565
    sleep_ms(10);

    st7789_command(0x36);  // Memory Data Access Control
    st7789_data(0x00);     // Normal orientation

    st7789_command(0x20);  // Display inversion off
    sleep_ms(10);

    st7789_command(0x13);  // Normal display mode on
    sleep_ms(10);

    st7789_command(0x29);  // Display on
    sleep_ms(500);

    // set drawing window to full screen
    st7789_set_window(0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1);
   
}

// Send a command to the display DC=0, CS=0
void st7789_command(uint8_t cmd) {
    gpio_put(PIN_DC, 0);  // Command mode
    gpio_put(PIN_CS, 0);  // Select display
    spi_write_blocking(SPI_PORT, &cmd, 1);
    gpio_put(PIN_CS, 1);  // Deselect display
}

// Send data to the display DC=1, CS=0
void st7789_data(uint8_t data) {
    gpio_put(PIN_DC, 1);  // Data mode
    gpio_put(PIN_CS, 0);  // Select display
    spi_write_blocking(SPI_PORT, &data, 1);
    gpio_put(PIN_CS, 1);  // Deselect display
}

// Write a buffer to the display DC=1, CS=0
void st7789_write(const uint8_t *buf, size_t len) {
    gpio_put(PIN_DC, 1);  // Data mode
    gpio_put(PIN_CS, 0);  // Select display
    spi_write_blocking(SPI_PORT, buf, len);
    gpio_put(PIN_CS, 1);  // Deselect display
}

// Set the drawing window on the display (full screen on our case)
void st7789_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    st7789_command(0x2A);  // Column Address Set
    st7789_data(x0 >> 8);
    st7789_data(x0 & 0xFF);
    st7789_data(x1 >> 8);
    st7789_data(x1 & 0xFF);

    st7789_command(0x2B);  // Row Address Set
    st7789_data(y0 >> 8);
    st7789_data(y0 & 0xFF);
    st7789_data(y1 >> 8);
    st7789_data(y1 & 0xFF);

    st7789_command(0x2C);  // Memory Write
}

// Fill the entire buffer with a specific color
void buffer_fill_color(uint8_t *buffer, uint16_t color) {
    uint8_t high = color >> 8;
    uint8_t low = color & 0xFF;
    for (int i = 0; i < BUFFER_SIZE; i += 2) {
        buffer[i] = high;
        buffer[i + 1] = low;
    }
}

// Draw a single pixel into the buffer
void buffer_draw_pixel(uint8_t *buffer, uint16_t x, uint16_t y, uint16_t color) {
    if (x >= SCREEN_WIDTH || y >= SCREEN_HEIGHT) return;
    uint32_t index = (y * SCREEN_WIDTH + x) * 2;
    buffer[index] = color >> 8;
    buffer[index + 1] = color & 0xFF;
}

// Start a DMA transfer to flush the framebuffer to the display
void flush_framebuffer_dma(uint8_t *buffer) {
    //st7789_set_window(0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1);
    gpio_put(PIN_DC, 1);  // Data mode
    gpio_put(PIN_CS, 0);  // Select display

    dma_channel_set_read_addr(dma_channel, buffer, true);
}

// Draw a single frame of the animation
void draw_frame(uint8_t *buffer, float a) {
    buffer_fill_color(buffer, ST7789_BLACK);

    int x, y, m, n, s;
    float i, p, q, r;

    for (y = 0; y < HEIGHT2; y += YS) {
        s = y * y;
        p = sqrtf(HEIGHT2 * HEIGHT2 - s);
        for (i = -p; i < p; i += 6 * XS) {
            r = sqrtf(s + i * i) / HEIGHT2;
            q = (r - 1) * sinf(24 * r + a);
            x = (int)(i / 3 + q * WIDTH2);
            if (i == -p) { m = x; n = x; }
            if (x > m) m = x;
            if (x < n) n = x;
            if ((m == x) || (n == x)) {
                buffer_draw_pixel(buffer, WIDTH2 + x, HEIGHT2 + y, COL);
                buffer_draw_pixel(buffer, WIDTH2 + x, HEIGHT2 - y, COL);
            }
        }
    }
}
