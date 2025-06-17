"""camera_pid controller."""
# LIBRARIES:


from controller import Display, Keyboard, Robot, Camera
from vehicle import Car, Driver
import numpy as np
import cv2
from datetime import datetime
import os


import logging



# CONFIGURATIONS:

img_path = r"C:\Users\Santiago Reyes\Desktop\AUTONOMOUIS_CAR\1_DataSet"

# Estoy Lo Voy a Estar Cambiando por cada Run para Guardar en Diferente Set/Carpeta
run_folder = "toma_11"

camera_mode_on = False

logging.basicConfig(
    filename='photo_mode.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# FUNCTIONS:

#Getting image from camera
def get_image(camera):
    raw_image = camera.getImage()  
    image = np.frombuffer(raw_image, np.uint8).reshape(
        (camera.getHeight(), camera.getWidth(), 4)
    )
    return image

#Image processing
def greyscale_cv2(image):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_img

#Display image 
def display_image(display, image):
    # Image to display
    image_rgb = np.dstack((image, image,image,))
    # Display image
    image_ref = display.imageNew(
        image_rgb.tobytes(),
        Display.RGB,
        width=image_rgb.shape[1],
        height=image_rgb.shape[0],
    )
    display.imagePaste(image_ref, 0, 0, False)

#initial angle and speed 
manual_steering = 0
steering_angle = 0
angle = 0.0
speed = 20

# set target speed
def set_speed(kmh):
    global speed
    speed = kmh
#update steering angle
def set_steering_angle(wheel_angle):
    global angle, steering_angle
    # Check limits of steering
    if (wheel_angle - steering_angle) > 0.1:
        wheel_angle = steering_angle + 0.1
    if (wheel_angle - steering_angle) < -0.1:
        wheel_angle = steering_angle - 0.1
    steering_angle = wheel_angle
  
    # limit range of the steering angle
    if wheel_angle > 0.5:
        wheel_angle = 0.5
    elif wheel_angle < -0.5:
        wheel_angle = -0.5
    # update steering angle
    angle = wheel_angle

#validate increment of steering angle
def change_steer_angle(inc):
    global manual_steering
    # Apply increment
    new_manual_steering = manual_steering + inc
    # Validate interval 
    if new_manual_steering <= 25.0 and new_manual_steering >= -25.0: 
        manual_steering = new_manual_steering
        set_steering_angle(manual_steering * 0.02)
    # Debugging
    if manual_steering == 0:
        print("going straight")
    else:
        turn = "left" if steering_angle < 0 else "right"
        print("turning {} rad {}".format(str(steering_angle),turn))
        print(f"SANTI - wheel_angle: ", steering_angle)

# Funcion para establecer setting de tomar 2 fotos por segundo
def photo_mode(camera, steering_angle, img_path, run_folder):
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    turn = "left" if steering_angle < 0 else "right"
    file_name = f"{current_datetime}__{steering_angle}_{turn}.png"
    full_path = os.path.join(img_path, run_folder)
    os.makedirs(full_path, exist_ok=True)  # Crea la carpeta si no existe
    save_path = os.path.join(full_path, file_name)
    logging.info(f"Image taken: {save_path}")
    camera.saveImage(save_path, 1)



# LOGIC: 


# main
def main(camera_mode_on):
    # Create the Robot instance.
    robot = Car()
    driver = Driver()

    # Get the time step of the current world.
    timestep = int(robot.getBasicTimeStep())

    # Create camera instance
    camera = robot.getDevice("camera")
    camera.enable(timestep)  # timestep

    # processing display
    display_img = Display("display")

    #create keyboard instance
    keyboard=Keyboard()
    keyboard.enable(timestep)

    while robot.step() != -1:
        # Get image from camera
        print("Car Speed: ", speed)
        image = get_image(camera)

        # Process and display image 
        grey_image = greyscale_cv2(image)
        display_image(display_img, grey_image)
        # Read keyboard
        key=keyboard.getKey()
        if key == keyboard.UP: #up
            set_speed(speed + 0.5)
            print("up")
        elif key == keyboard.DOWN: #down
            set_speed(speed - 0.5)
            print("down")
        elif key == keyboard.RIGHT: #right
            change_steer_angle(+0.1)
            print("right")
        elif key == keyboard.LEFT: #left
            change_steer_angle(-0.1)
            print("left")
        elif key == ord('A'):
            camera_mode_on = not camera_mode_on  # Cambia entre True y False
            print(f"Camera mode {'ON' if camera_mode_on else 'OFF'}")

        if camera_mode_on:
            print(f"Photomode status: {camera_mode_on}")
            photo_mode(camera, steering_angle, img_path, run_folder)
       
        #update angle and speed
        driver.setSteeringAngle(angle)
        driver.setCruisingSpeed(speed)


if __name__ == "__main__":
    main(camera_mode_on)