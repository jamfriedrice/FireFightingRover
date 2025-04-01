import os
import glob
import time
import RPi.GPIO as GPIO

# Initialize the GPIO Pin for the Fan
IFAN_PIN6 = 6
GPIO.setmode(GPIO.BCM)
GPIO.setup(IFAN_PIN6, GPIO.OUT, initial=GPIO.LOW)  # Fan initially OFF

# Initialize temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Find the correct device file that holds the temperature data
base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')

if not device_folders:
    print("Temperature sensor not found! Exiting...")
    GPIO.cleanup()
    exit()

device_file = device_folders[0] + '/w1_slave'

# Function to read raw temperature data
def read_temp_raw():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

# Function to read and process temperature
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    return None  # Return None if temperature reading fails

try:
    print("Monitoring temperature. Fan will turn ON above 24.5°C and OFF otherwise.")
    
    while True:
        temperature = read_temp()
        if temperature is not None:
            print(f"\rCurrent Temperature: {temperature:.2f}°C", end="")

            # Activate fan if temperature exceeds 24.5°C
            if temperature > 37:
                GPIO.output(IFAN_PIN6, GPIO.HIGH)  # Turn ON fan
                print("  | Fan ON", end="")
            else:
                GPIO.output(IFAN_PIN6, GPIO.LOW)  # Turn OFF fan
                print("  | Fan OFF", end="")

        time.sleep(1)  # Update temperature reading every second

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.output(IFAN_PIN6, GPIO.LOW)  # Ensure fan is OFF before exiting
    GPIO.cleanup()
