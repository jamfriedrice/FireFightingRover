from picamera2 import Picamera2
import pygame
import time

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

print("Press 'A' button on Xbox to capture a photo.")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # 'A' button
                filename = f"photo_{int(time.time())}.jpg"
                picam2.start()
                time.sleep(2)  # Camera warm-up time
                picam2.capture_file(filename)
                print(f"Picture saved as {filename}")
                picam2.stop()

            elif event.button == 6:  # Back button to quit
                running = False
                print("Exiting...")

pygame.quit()