import pygame
import RPi.GPIO as GPIO
import time

# Setup GPIO
HFAN_PIN5 = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(HFAN_PIN5, GPIO.OUT, initial=GPIO.LOW)  # Set initial state to HIGH (Fan OFF)

# Initialize pygame for Xbox controller input
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

fan_state = False  # Fan is OFF at the beginning

try:
    print("Press RB to toggle fan ON/OFF.")
    while True:
        pygame.event.pump()
        buttons = joystick.get_button(5)  # B button index

        if buttons:  # If B is pressed
            fan_state = not fan_state
            GPIO.output(HFAN_PIN5, GPIO.HIGH if fan_state else GPIO.LOW)
            print("Fan ON" if fan_state else "Fan OFF")
            time.sleep(0.5)  # Debounce delay

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()
    pygame.quit()
