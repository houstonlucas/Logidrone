import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

WHITE = (255, 255, 255)
RED = (255, 0, 0)

# TODO: Map out parts to pixels
pixel_mapping = {
    'efbe71e5-1bff-43d0-b86c-a1d875d4a6d4': [(0, 0)]
}


def main():
    # TODO: unzip drn file programatically
    parts = get_parts("DroneData")
    make_image_from_parts(parts)


def get_position(elem):
    pos_elem = elem.find("CurrentPosition")
    x = round(float(pos_elem.find("x").text))
    y = round(float(pos_elem.find("y").text))
    return x, y


def get_orientation(elem):
    rotation = elem.find("CurrentRotation").find("eulerAngles").find("z").text
    return round(float(rotation))


def get_parts(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    parts = []
    drone_parts = root.iter("DronePartData")
    for part_elem in drone_parts:
        part = {
            'PrefabId': part_elem.find("PrefabId").text,
            'position': get_position(part_elem),
            'orientation': get_orientation(part_elem)}
        parts.append(part)
    return parts


def get_drone_size_info(parts):
    max_x = max([abs(part['position'][0]) for part in parts])
    max_y = max([abs(part['position'][1]) for part in parts])
    width = 2 * max_x
    height = 2 * max_y
    return height, width


def apply_offset(position, pixel_location, height, width, padding):
    new_x = position[0] + pixel_location[0] + padding + width // 2
    new_y = -position[1] + pixel_location[1] + padding + height // 2
    return new_x, new_y


def draw_part(im, part, height, width, padding):
    # TODO: use orientation
    pixel_locations = pixel_mapping[part['PrefabId']]
    for pixel_location in pixel_locations:
        pos = apply_offset(part['position'], pixel_location, height, width, padding)
        im.putpixel(pos, RED)


def make_image_from_parts(parts, padding=10):
    height, width = get_drone_size_info(parts)
    image_size = [width + 2 * padding, height + 2 * padding]
    im = Image.new('RGB', image_size)
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0) + im.size, WHITE)

    for part in parts:
        draw_part(im, part, height, width, padding)

    im.show()
    im.save("test.png")


if __name__ == '__main__':
    main()
