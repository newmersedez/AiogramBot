import os
from PIL import Image
from image_utility.template_helper import (
    resize_for_complex_template,
    resize_for_simple_template,
    SIMPLE_TEMPLATE_WIDTH,
    SIMPLE_TEMPLATE_HEIGHT,
    COMPLEX_TEMPLATE_IMAGE_X,
    COMPLEX_TEMPLATE_IMAGE_Y
)

ROOT_DIR = os.path.abspath(os.path.pardir)
IMAGE_UTILITY_DIR = os.path.join(ROOT_DIR, 'image_utility')
IMAGES_DIR = os.path.join(IMAGE_UTILITY_DIR, 'images')
WATERMARK_PATH = os.path.join(IMAGES_DIR, 'watermark.png')


def create_simple_template(image_path: str, output_path: str, background=str, watermark=WATERMARK_PATH):
    """
    Creates simple shop product cover with title and given image (image_path). The result is stored in output_path.

    :param image_path: path to source image
    :param output_path: path to result image
    :param background: path to header image (set to default)
    :param watermark path to watermark layout (set to default)
    :param default_background: path to default background if image is too small
    """

    image = resize_for_simple_template(image_path, SIMPLE_TEMPLATE_WIDTH, SIMPLE_TEMPLATE_HEIGHT)

    if image.width != SIMPLE_TEMPLATE_WIDTH or image.height != SIMPLE_TEMPLATE_HEIGHT:
        expand_image = Image.new("RGBA", (SIMPLE_TEMPLATE_WIDTH, SIMPLE_TEMPLATE_HEIGHT), (255, 255, 255))
        expand_image.paste(image,
                           (SIMPLE_TEMPLATE_WIDTH // 2 - image.width // 2, SIMPLE_TEMPLATE_HEIGHT - image.height),
                           image)
        image = expand_image

    background = Image.open(background)
    watermark = Image.open(watermark)
    image.paste(background, (0, 0), background)
    image.paste(watermark, (0, 0), watermark)
    image.save(output_path)


def create_complex_template(image_path: str, output_path: str, background=str, watermark=WATERMARK_PATH):
    """
    Creates complex shop product cover with title and given image (image_path). The result is stored in output_path.

    :param image_path: path to source image
    :param output_path: path to result image
    :param background: path to header image (set to default)
    :param watermark path to watermark layout (set to default)
    """

    image = resize_for_complex_template(image_path)
    background = Image.open(background)
    watermark = Image.open(watermark)
    background.paste(image,
                     (COMPLEX_TEMPLATE_IMAGE_X - image.width // 2, COMPLEX_TEMPLATE_IMAGE_Y - image.height // 2),
                     image)
    background.paste(watermark, (0, 0), watermark)
    background.save(output_path)
