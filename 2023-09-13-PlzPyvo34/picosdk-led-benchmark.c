#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/time.h"

int main() {
    stdio_init_all();

    const uint LED_PIN = PICO_DEFAULT_LED_PIN;
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    uint32_t t0, t1;

    while (true) {
        t0 =  time_us_32();
        
        for (int i = 0; i <= 100000; i++) {
            gpio_put(LED_PIN, 1);
            gpio_put(LED_PIN, 0);
        }
        
        t1 =  time_us_32();
        
        uint32_t time_diff_us = t1 - t0;
        printf("Time: %d us\n", time_diff_us);

        sleep_ms(1000);
    }
}