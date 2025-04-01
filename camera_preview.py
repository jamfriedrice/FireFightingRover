from picamera2 import Picamera2, Preview
import pygame
import time
import os

# Create 'pictures' directory if it doesn't exist
os.makedirs("pictures", exist_ok=True)

# Initialize Xbox controller
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Initialize Camera
picam2 = Picamera2()

# Set full-resolution preview and enable auto settings
config = picam2.create_preview_configuration(main={"size": (4056, 3040)}, lores={"size": (1280, 720)})
picam2.configure(config)

# Ensure auto exposure and white balance
picam2.set_controls({"AeEnable": True, "AwbEnable": True})

print("Live preview started.")
print("Press 'SS' button to capture a photo.")
print("Press 'LB' button to exit.")

picam2.start_preview(Preview.QTGL)  # OpenGL preview
picam2.start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 6:  # 'Screenshot' button
                filename = f"pictures/photo_{int(time.time())}.jpg"
                picam2.capture_file(filename)
                print(f"Picture saved as {filename}")

            elif event.button == 4:  # 'LB' button to quit
                running = False
                print("Exiting...")

picam2.stop_preview()
picam2.stop()
pygame.quit()

