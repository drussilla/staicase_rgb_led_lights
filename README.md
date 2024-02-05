# staicase_rgb_led_lights
Code for my home project of DIY Staircase With RGB LED Lights And Motion Sensors 
You can find some instructions here: https://ivanderevianko.com/2020/12/diy-staircase-renovation-with-rgb-led-lights-and-motion-sensors

Before you can run this do the following:

```bash
sudo apt-get install python3-rpi.gpio python3-pip
sudo pip install rpi_ws281x
```

This code is designed to work with two led strips that are indexed from the middle of my staicase. 
So `strip1` goes from the middle of my staircase to the bottom and 
`strip2` goes from the middle to the top.
They also have different amount of leds and different amound of leds per stair.

This is why I have `map_leds` function. This will return the array of led indexes so they can be later addresed in regular `for` loops.

If you have only one led strip you can simplify the code and remove `map_leds` function.


To run this code do the following:
```bash
sudo python3 control.py
```

By default it will run `rainbowCycle` until you press `Ctrl+C` in the console. They it will swtich to a "motion" detection mode and will light up the stairs based on the data from motion sensors.
