import smbus
import time
import math
import pygame

# Initialize I2C for MPU6050
bus = smbus.SMBus(1)
MPU6050_ADDR = 0x68

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
        pygame.event.pump()  # Process controller input

        angle_x, angle_y = get_tilt_angle()
        print(f"Tilt X: {angle_x:.2f}°, Tilt Y: {angle_y:.2f}°")

        if abs(angle_x) > TILT_THRESHOLD or abs(angle_y) > TILT_THRESHOLD:
            print("Tilt too great! (Would stop motors here)")

        # Exit if Button 1 (usually 'B' button) is pressed
        if joystick.get_button(1):
            print("Button B pressed. Exiting program...")
            running = False

        time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting by KeyboardInterrupt...")
        break
    except Exception as e:
        print(f"Error: {e}")
        break

# Cleanup
pygame.quit()
