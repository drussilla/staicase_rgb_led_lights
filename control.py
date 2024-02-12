import time
import datetime
import argparse
import colorsys

from rpi_ws281x import ws, Color, Adafruit_NeoPixel
import RPi.GPIO as GPIO

# LED strip configuration:

# Bottom - from top to bottom
# 75 75 75 75 75 75 | 75 90 105 85 80                                                                             │
LED_1_COUNT = 177        # Number of LED pixels.                                                        │
LED_1_PIN = 18          # GPIO pin connected to the pixels (must support PWM! GPIO 13 and 18 on RPi 3). │
LED_1_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)                                │
LED_1_DMA = 10          # DMA channel to use for generating signal (Between 1 and 14)                   │
LED_1_BRIGHTNESS = 128  # Set to 0 for darkest and 255 for brightest                                    │
LED_1_INVERT = False    # True to invert the signal (when using NPN transistor level shift)             │
LED_1_CHANNEL = 0       # 0 or 1                                                                        

# Top - From bottom to top
# 75 80 95 95 90 85
LED_2_COUNT = 104        # Number of LED pixels.                                                        │
LED_2_PIN = 13          # GPIO pin connected to the pixels (must support PWM! GPIO 13 or 18 on RPi 3).  │
LED_2_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)                                │
LED_2_DMA = 10          # DMA channel to use for generating signal (Between 1 and 14)                   │
LED_2_BRIGHTNESS = 128  # Set to 0 for darkest and 255 for brightest                                    │
LED_2_INVERT = False    # True to invert the signal (when using NPN transistor level shift)             │
LED_2_CHANNEL = 1       # 0 or 1                                                                        │
LED_STRIP_TYPE = ws.WS2811_STRIP_BRG

# from bottom to top
leds_per_stair = [ 16, 17, 21, 18, 15, 15, 15, 15, 15, 15, 15, 15, 16, 19, 19, 18, 17 ]

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

def colorWipe(led_indexes, color, wait_ms=1): 
    """Wipe color across display a pixel at a time."""   
    for stair in led_indexes:
        for i in range(len(stair) - 1):
            stair[0].setPixelColor(stair[i + 1], color)
            stair[0].show()
            time.sleep(wait_ms/1000)
            

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbowCycle(strip1, strip2, wait_ms=1, iterations=500):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    totalPixels = strip1.numPixels() + strip2.numPixels() 
    for j in range(256 * iterations):
        for i in range(totalPixels):
            if i >= strip1.numPixels():
                strip2.setPixelColor(strip2.numPixels() - (i - strip1.numPixels()) - 1, wheel(
                    (int(i * 256 / totalPixels) + j) & 255))
            else:
                strip1.setPixelColor(i, wheel(
                    (int(i * 256 / totalPixels) + j) & 255))
        strip1.show()
        strip2.show()
        time.sleep(wait_ms / 1000.0)

def yellowFullFill(led_indexes):
    for stair in led_indexes:
        for value in range(4):
            for i in range(len(stair) - 1):
                color = hsv2rgb(0.05, 1, value/10.0)
                stair[0].setPixelColor(stair[i+1], Color(color[0], color[1], color[2]))
            stair[0].show()
            time.sleep(5/1000)                

def rainbowPerStair(strip1, strip2, led_indexes, wait_ms=20, iterations=50):
    """Draw rainbow that uniformly distributes itself across pixels of each stair."""
    for j in range(256 * iterations):
        for stair in led_indexes:
            for i in range(len(stair) - 1):
                stair[0].setPixelColor(stair[i+1], wheel((int(i * 256 / (len(stair) - 1)) + j) & 255))
        strip1.show()
        strip2.show()
        time.sleep(wait_ms / 1000.0)

def map_leds(strip1, strip2):
    """
    Maps two different led strips to the signe data structure that is easy to work with
    Retunrs array of "stairs". Each stair it an array itself. where the first element is NeoPixel object to control strip
    And the rest elements in the "stair" inner array is the indexes of the individual leds in the strip.
    [ [strip1, 0, 1, 2, 3], [strip1, 4, 5, 6, 7, 8], ... [strip2, 178, 177, 176], [strip2, 175, 174, ...] ]
    """
    led_indexes = []
    indexes_used = 0
    for i in range(len(leds_per_stair)):
        if i < 11:
            led_indexes.append([strip1])
            for j in range(leds_per_stair[i]):
                led_indexes[i].append(176 - indexes_used)
                indexes_used = indexes_used + 1       
            # bottom part

            if indexes_used == 177:
                indexes_used = 0
        else:
            led_indexes.append([strip2])
            for j in range(leds_per_stair[i]):
                led_indexes[i].append(indexes_used)
                indexes_used = indexes_used + 1   
    return led_indexes

if __name__ == '__main__': 
    # Process arguments
    parser = argparse.ArgumentParser() 
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument('-m', '--mode', help='set mode: rainbow, detect', default='detect')
    args = parser.parse_args()

    # Create NeoPixel objects with appropriate configuration for each strip.                            │
    strip1 = Adafruit_NeoPixel(LED_1_COUNT, LED_1_PIN, LED_1_FREQ_HZ, LED_1_DMA, LED_1_INVERT, LED_1_BRIGHTNESS, LED_1_CHANNEL, LED_STRIP_TYPE)

    strip2 = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ, LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS, LED_2_CHANNEL, LED_STRIP_TYPE)

    led_indexes = map_leds(strip1, strip2)

    # Intialize the library (must be called once before other functions).                               │
    strip1.begin()
    strip2.begin()

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN)
    GPIO.setup(13, GPIO.IN) 

    print(f'Mode: {args.mode}')
    print('Press Ctrl-C to quit.')

    try:
        if args.mode == 'rainbow':
            while True:
                rainbowCycle(strip1, strip2)
        else:
            while True:
                top = GPIO.input(11)
                bottom = GPIO.input(13)
                if bottom == 1:
                    yellowFullFill(led_indexes)
                    time.sleep(15)            
                    colorWipe(led_indexes, Color(0, 0, 0), 5)
                elif top == 1:
                    yellowFullFill(reversed(led_indexes))
                    time.sleep(15)            
                    colorWipe(led_indexes, Color(0, 0, 0), 5)
                    
    except KeyboardInterrupt:  
        if args.clear: 
            colorWipe(led_indexes, Color(0, 0, 0), 2)
