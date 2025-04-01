import pygame
import time

# Initialize pygame
pygame.init()
pygame.joystick.init()

# Initialize the first connected joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Joystick name: {joystick.get_name()}")

# Main loop to read D-pad input
running = True
while running:
    pygame.event.pump()  # Process internal pygame events
    
    # Read D-pad (hat) input
    hat_x, hat_y = joystick.get_hat(0)
    
    print(f"hat_x: {hat_x}, hat_y: {hat_y}")

    # Interpret the direction
    if (hat_x, hat_y) == (0, 1):
        print("D-pad: UP")
    elif (hat_x, hat_y) == (0, -1):
        print("D-pad: DOWN")
    elif (hat_x, hat_y) == (-1, 0):
        print("D-pad: LEFT")
    elif (hat_x, hat_y) == (1, 0):
        print("D-pad: RIGHT")
    elif (hat_x, hat_y) == (-1, 1):
        print("D-pad: UP-LEFT")
    elif (hat_x, hat_y) == (1, 1):
        print("D-pad: UP-RIGHT")
    elif (hat_x, hat_y) == (-1, -1):
        print("D-pad: DOWN-LEFT")
    elif (hat_x, hat_y) == (1, -1):
        print("D-pad: DOWN-RIGHT")
    elif (hat_x, hat_y) == (0, 0):
        print("D-pad: CENTER (Not Pressed)")
    
    # Exit condition (press "Back" button - usually button 6)
    if joystick.get_button(6):
        print("Exiting...")
        running = False

    time.sleep(0.2)  # Delay to avoid spamming output

# Cleanup
pygame.quit()
