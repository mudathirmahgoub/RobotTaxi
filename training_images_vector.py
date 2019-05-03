import anki_vector
import os
import time

number_of_images = 5  # total number of the same image
directory = 'matlab/training_images/vector'  # directory for training images
image_class = 'person'  # the image class or label


def main():
    global directory, image_class
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial, ip='192.168.0.18', enable_camera_feed=True, show_viewer=True) as robot:
        robot.motors.set_lift_motor(-5.0)
        time.sleep(3.0)
        robot.motors.set_lift_motor(0.0)
        time.sleep(3.0)
        # the directory contains all images of the same class
        class_directory = f'{directory}/{image_class}'
        # create a directory for the class if it doesn't exist
        if not os.path.exists(class_directory):
            os.makedirs(class_directory)

        # get the image number of the last jpeg file
        files = [file for file in os.listdir(class_directory) if file.endswith('.jpeg')]
        if len(files) > 0:
            files.sort()
            last_name = files[-1].replace('.jpeg', '')
            image_number = int(last_name)
        else:
            image_number = 0
        latest_image = None
        for index in range(1, number_of_images + 1):
            image = robot.camera.latest_image
            while image == latest_image:
                image = robot.camera.latest_image
            latest_image = image
            image = image.resize((224, 224))
            file_name = "{:04d}.jpeg".format(image_number + index)
            image.save(f"{class_directory}/{file_name}", "JPEG")


if __name__ == "__main__":
    main()
