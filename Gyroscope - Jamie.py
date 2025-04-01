import smbus
import time
import serial
import math
import pygame

# Initialize I2C for MPU6050
bus = smbus.SMBus(1)
MPU6050_ADDR = 0x68

# Initialize Serial Communication with Arduino
ser = serial.Serial('/dev/ttyUSB3', 9600, timeout=1)  # Update with correct port

# Wake up MPU6050
bus.write_byte_data(MPU6050_ADDR, 0x6B, 0)

# Initialize Pygame for Xbox controller input
pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

def read_raw_data(addr):
    """ Read raw data from the given address of the MPU6050 """
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr+1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

def get_tilt_angle():
    """ Get the tilt angle using the accelerometer """
    acc_x = read_raw_data(0x3B) / 16384.0
    acc_y = read_raw_data(0x3D) / 16384.0
    acc_z = read_raw_data(0x3F) / 16384.0
   
    # Calculate tilt angle in degrees
    angle_x = math.degrees(math.atan2(acc_y, acc_z))
    angle_y = math.degrees(math.atan2(acc_x, acc_z))
   
    return angle_x, angle_y

TILT_THRESHOLD = 30  # Adjust threshold angle as needed

running = True
while running:
    try:
        pygame.event.pump()  # Process controller events

        angle_x, angle_y = get_tilt_angle()
        print(f"Tilt X: {angle_x:.2f}°, Tilt Y: {angle_y:.2f}°")

        if abs(angle_x) > TILT_THRESHOLD or abs(angle_y) > TILT_THRESHOLD:
            print("Tilt too great! Stopping motors.")
            arduino.write(b'STOP\n')  # Send stop command to Arduino

        # Exit if Button 1 (B button) is pressed
        if joystick.get_button(1):
            send_command("E")
            print("Button B pressed. Exiting program...")
            running = False

        time.sleep(0.1)

    except KeyboardInterrupt:
        print("KeyboardInterrupt: Exiting program...")
        break
    except Exception as e:
        print(f"Error: {e}")
        break

# Cleanup
pygame.quit()
ser.close()
