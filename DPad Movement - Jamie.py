import serial
import pygame
import time

# Initialize serial connection to Arduino
ser = serial.Serial('/dev/ttyUSB3', 9600, timeout=1)
time.sleep(2)  # Allow time for Arduino to reset

# Initialize pygame for Xbox controller input
pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

def send_command(command):
    ser.write(command.encode())  # Send command as bytes
    print(f"Sent: {command}")

# Main loop for reading Xbox controller input
running = True
while running:
    pygame.event.pump()

    # Read D-pad (hat) input
    hat_x, hat_y = joystick.get_hat(0)

    if hat_y == 1:  # D-pad up (Forward)
        send_command("F")
    elif hat_y == -1:  # D-pad down (Backward)
        send_command("B")
   
    if hat_x == -1:  # D-pad left (Turn left)
        send_command("L")
    elif hat_x == 1:  # D-pad right (Turn right)
        send_command("R")
   
    # Check for exit condition (press Xbox 'B' button)
    if joystick.get_button(1):  # 'B' button
        send_command("E")
        print("Button B pressed. Exiting program...")
        running = False

    time.sleep(0.1)  # Small delay to prevent spamming commands

# Cleanup
pygame.quit()
ser.close()