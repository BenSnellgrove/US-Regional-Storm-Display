from machine import Pin
from time import sleep

# Don't touch 0 in boot
# See https://docs.espressif.com/projects/esp-idf/en/latest/esp32/_images/esp32-devkitC-v4-pinout.png

# 2 is update/error pin

for pin in [32, 33, 25, 26, 27, 14, 12, 13, 15, 2]:# 0
  print(pin)
  led = Pin(pin, Pin.OUT)
  led.value(True)
  sleep(0.04)

for pin in [23, 22, 21, 19, 18, 5, 17, 16, 4, ]:
  print(pin)
  led = Pin(pin, Pin.OUT)
  led.value(True)
  sleep(0.04)
  
for pin in [32, 33, 25, 26, 27, 14, 12, 13, 15, 2]:# 0
  print(pin)
  led = Pin(pin, Pin.OUT)
  led.value(False)
  sleep(0.04)
  
for pin in [23, 22, 21, 19, 18, 5, 17, 16, 4, ]:
  print(pin)
  led = Pin(pin, Pin.OUT)
  led.value(False)
  sleep(0.04)

# Establish network connection
exec(open('network.py').read(), globals())
# Wait for connection
sleep(10)

# Main script
exec(open('gov_api_reader.py').read(), globals())

