import time
import board
import adafruit_scd4x


# initialize i2c bus
i2c = board.STEMMA_I2C()

# initialize SCD4x sensor
sensor = adafruit_scd4x.SCD4X(i2c)
sensor.start_periodic_measurement()

# read and show measured values every 5 seconds
while True:

    while not sensor.data_ready:
        time.sleep(0.2)
    
    # read and show measured values
    print("Temperature: %0.2f °C" % sensor.temperature)
    print("Humidity: %0.2f %%" % sensor.relative_humidity)
    print("CO2: %d ppm" % sensor.CO2)

    time.sleep(5)

