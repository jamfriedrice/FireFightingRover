import os
import glob
import RPi.GPIO as GPIO
import pygame
import smbus
import math as m
import time as t
import serial as ser
from picamera2 import Picamera2, Preview

# Initialize GPIO for Fans
IFAN_PIN6 = 6
HFAN_PIN5 = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(IFAN_PIN6, GPIO.OUT, initial=GPIO.LOW)  # Intake Fans initially OFF
GPIO.setup(HFAN_PIN5, GPIO.OUT, initial=GPIO.LOW)  # Head Fan initially OFF

# Initialize serial connection to Arduino
ardu = ser.Serial('/dev/ttyUSB3', 9600, timeout=1) 
t.sleep(2)  # Allow time for Arduino to reset

# Initialize I2C for MPU6050
bus = smbus.SMBus(1)
MPU6050_ADDR = 0x68
bus.write_byte_data(MPU6050_ADDR, 0x6B, 0)  # Wake up MPU6050

# Initialize pygame for Xbox controller input
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

# Initialize Camera
picam2 = Picamera2()
os.makedirs("pictures", exist_ok=True)
config = picam2.create_preview_configuration(main={"size": (4056, 3040)}, lores={"size": (1280, 720)})
picam2.configure(config)
picam2.set_controls({"AeEnable": True, "AwbEnable": True})
picam2.start_preview(Preview.QTGL)  # OpenGL preview
picam2.start()

# Temperature sensor setup
base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')

if not device_folders:
    print("Temperature sensor not found! Exiting...")
    GPIO.cleanup()
    exit()

device_file = device_folders[0] + '/w1_slave'

# Function to read temperature
def read_temp_raw():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        t.sleep(0.2)
        lines = read_temp_raw()
    
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    return None

# Serial connection
def send_command(command):
    ardu.write(command.encode())  # Send command to Arduino
    print(f"Sent: {command}")

# Gyroscope
def read_raw_data(addr):
    """ Read raw data from the given address of the MPU6050 """
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr+1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

# Tilt angle function
def get_tilt_angle():
    """ Get the tilt angle using the accelerometer """
    acc_x = read_raw_data(0x3B) / 16384.0
    acc_y = read_raw_data(0x3D) / 16384.0
    acc_z = read_raw_data(0x3F) / 16384.0
    angle_x = m.degrees(m.atan2(acc_y, acc_z))
    angle_y = m.degrees(m.atan2(acc_x, acc_z))
    return angle_x, angle_y

# Main loop
running = True
fan_state = False
TILT_THRESHOLD = 30  # Adjust threshold for tilt angle
while running:
    try:
        # Read temperature
        temperature = read_temp()
        if temperature is not None:
            print(f"\rTemperature: {temperature:.2f}°C", end="")

            # Control fan based on temperature
            if temperature > 37:
                GPIO.output(IFAN_PIN6, GPIO.HIGH)  # Turn ON fan
                print("  | Fan ON", end="")
            else:
                GPIO.output(IFAN_PIN6, GPIO.LOW)  # Turn OFF fan
                print("  | Fan OFF", end="")

        # Read D-pad (hat) input for Arduino control
        pygame.event.pump()
        hat_x, hat_y = joystick.get_hat(0)

        if hat_y == 1:
            send_command("F")  # Forward
        elif hat_y == -1:
            send_command("B")  # Backward
        if hat_x == -1:
            send_command("L")  # Left
        elif hat_x == 1:
            send_command("R")  # Right

        # Read accelerometer data
        angle_x, angle_y = get_tilt_angle()
        print(f"Tilt X: {angle_x:.2f}°, Tilt Y: {angle_y:.2f}°")

        if abs(angle_x) > TILT_THRESHOLD or abs(angle_y) > TILT_THRESHOLD:
            print("Tilt too great! Stopping motors.")
            send_command("E")  # Send stop command to Arduino

        # Capture photo if 'SS' button is pressed
        if joystick.get_button(6):  # Screenshot button
            filename = f"pictures/photo_{int(t.time())}.jpg"
            picam2.capture_file(filename)
            print(f"Picture saved as {filename}")

        # Exit if 'B' button is pressed
        if joystick.get_button(1):  # B button to exit
            send_command("E")  # Send exit/stop command to Arduino
            running = False
            print("Exiting...")

        t.sleep(0.1)  # Small delay

    except KeyboardInterrupt:
        print("Exiting program...")
        break
    except Exception as e:
        print(f"Error: {e}")
        break

# Cleanup
picam2.stop_preview()
picam2.stop()
GPIO.cleanup()
pygame.quit()
ardu.close()
