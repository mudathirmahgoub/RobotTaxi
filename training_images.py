import cozmo
import os

number_of_images = 10  # total number of the same image
directory = 'data/training_images'  # directory for training images
image_class = 'turn-right-right'  # the image class or label


def cozmo_program(robot: cozmo.robot.Robot):
    global directory, image_class
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

    # take and save the images
    for index in range(1, number_of_images + 1):
        robot.world.wait_for(cozmo.world.EvtNewCameraImage)
        image = robot.world.latest_image.raw_image
        image = image.resize((224, 224))
        file_name = "{:04d}.jpeg".format(image_number + index)
        image.save(f"{class_directory}/{file_name}", "JPEG")


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=True)

