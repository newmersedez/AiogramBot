from PIL import Image
from image_utility.bg import remove_image_background

SIMPLE_TEMPLATE_HEIGHT = 1200
SIMPLE_TEMPLATE_WIDTH = 900

COMPLEX_TEMPLATE_HEIGHT = 1200
COMPLEX_TEMPLATE_WIDTH = 900

COMPLEX_TEMPLATE_IMAGE_X = 450
COMPLEX_TEMPLATE_IMAGE_Y = 800


def resize_for_complex_template(image_path: str, base_width=COMPLEX_TEMPLATE_WIDTH, base_height=COMPLEX_TEMPLATE_HEIGHT) -> Image:
    """
    Crops and resizes image (image_path) and returns Image class object.

    :param image_path: path to source image
    :param base_height: default height for product_cover
    :param base_width: default_width for product cover
    :return Image class object
    """

    # image = Image.open(image_path).convert("RGBA")
    image = remove_image_background(image_path)

    image_components = image.split()
    rgb_image = Image.new("RGB", image.size, (0, 0, 0))
    # rgb_image.paste(image)
    rgb_image.paste(image, mask=image_components[3])

    image_box = image.getbbox()
    cropped_box = rgb_image.getbbox()
    if image_box != cropped_box:
        image = image.crop(cropped_box)

    # aspect_ratio = float(image.width) / float(image.height)
    # height = base_height
    # width = int(height * aspect_ratio)
    # if width <= base_width:
    #     image = image.resize((width, height), Image.ANTIALIAS)
    # else:
    #     height = int(base_width / aspect_ratio)
    #     image = image.resize((base_width, height), Image.ANTIALIAS)

    aspect_ratio = float(image.width) / float(image.height)
    height = int(base_height / 2.3)
    width = int(height * aspect_ratio)
    image = image.resize((width, height), Image.ANTIALIAS)
    # if width <= base_width:
    #     image = image.resize((width, height), Image.ANTIALIAS)
    # else:
    #     height = int(base_width / aspect_ratio)
    #     image = image.resize((base_width, height), Image.ANTIALIAS)
    return image


def resize_for_simple_template(image_path: str, base_width=SIMPLE_TEMPLATE_WIDTH, base_height=SIMPLE_TEMPLATE_HEIGHT) -> Image:
    """
    Resizes image and crops to default width and height.

    :param image_path: path to source image
    :param base_height: default height for product_cover
    :param base_width: default_width for product cover
    :return: Image class object
    """

    image = Image.open(image_path).convert("RGBA")
    resize_width = image.width
    resize_height = image.height

    if resize_width == image.height:
        if resize_width < base_width:
            resize_width = base_width
            resize_height = base_width
    else:
        aspect_ratio = float(resize_width) / float(resize_height)
        if resize_width < base_width:
            resize_width = base_width
            resize_height = int(resize_width / aspect_ratio)
        if resize_height < base_height:
            resize_height = base_height
            resize_width = int(resize_height * aspect_ratio)

    image = image.resize((resize_width, resize_height), Image.ANTIALIAS)
    if image.width > base_width:
        x0, y0 = (image.width // 2) - (base_width // 2), 0
        x1, y1 = (image.width // 2) + (base_width // 2), image.height
        image = image.crop((x0, y0, x1, y1))
    if image.height > base_height:
        x0, y0 = 0, 0
        x1, y1 = image.width, base_height
        image = image.crop((x0, y0, x1, y1))
    return image
