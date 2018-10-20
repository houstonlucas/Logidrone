import xml.etree.ElementTree as ET
from itertools import product
from PIL import Image, ImageDraw

WHITE = (255, 255, 255)
RED = (255, 0, 0)

shape_to_pixels = {
    'DroneCore': [(-3.5, -2.5), (-3.5, -1.5), (-3.5, -0.5), (-3.5, 0.5), (-3.5, 1.5), (-3.5, 2.5), (-2.5, -3.5), (-2.5, -2.5), (-2.5, -1.5), (-2.5, -0.5), (-2.5, 0.5), (-2.5, 1.5), (-2.5, 2.5), (-2.5, 3.5), (-1.5, -3.5), (-1.5, -2.5), (-1.5, -1.5), (-1.5, -0.5), (-1.5, 0.5), (-1.5, 1.5), (-1.5, 2.5), (-1.5, 3.5), (-0.5, -3.5), (-0.5, -2.5), (-0.5, -1.5), (-0.5, -0.5), (-0.5, 0.5), (-0.5, 1.5), (-0.5, 2.5), (-0.5, 3.5), (0.5, -3.5), (0.5, -2.5), (0.5, -1.5), (0.5, -0.5), (0.5, 0.5), (0.5, 1.5), (0.5, 2.5), (0.5, 3.5), (1.5, -3.5), (1.5, -2.5), (1.5, -1.5), (1.5, -0.5), (1.5, 0.5), (1.5, 1.5), (1.5, 2.5), (1.5, 3.5), (2.5, -3.5), (2.5, -2.5), (2.5, -1.5), (2.5, -0.5), (2.5, 0.5), (2.5, 1.5), (2.5, 2.5), (2.5, 3.5), (3.5, -2.5), (3.5, -1.5), (3.5, -0.5), (3.5, 0.5), (3.5, 1.5), (3.5, 2.5)],
    'Small Square': [(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5)],
    'Large Square': [(-1.5, -1.5), (-1.5, -0.5), (-1.5, 0.5), (-1.5, 1.5), (-0.5, -1.5), (-0.5, -0.5), (-0.5, 0.5), (-0.5, 1.5), (0.5, -1.5), (0.5, -0.5), (0.5, 0.5), (0.5, 1.5), (1.5, -1.5), (1.5, -0.5), (1.5, 0.5), (1.5, 1.5)],
    'Vertical Rectangle': [(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5), (0.5, -1.5), (-0.5, -1.5),(0.5, 1.5), (-0.5, 1.5)],
    'Horizontal Rectangle': [(1.5, 0.5), (1.5, -0.5), (0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5), (-1.5, -0.5), (-1.5, 0.5)],
    'L-Shape': [(0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5), (-1.5, -0.5), (-1.5, 0.5), (-2.5, 0.5), (-2.5, -0.5), (0.5, 1.5), (0.5, 2.5), (-0.5, 2.5), (-0.5, 1.5)],
    'Gigadrill': [(1.5, -0.5), (1.5, 0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5), (-1.5, 0.5), (-1.5, -0.5), (1.5, -2.5), (1.5, -1.5), (0.5, -2.5), (0.5, -1.5), (-0.5, -1.5), (-0.5, -2.5), (-1.5, -1.5), (-1.5, -2.5), (0.5, -3.5), (-0.5, -3.5)]
}

prefab_to_shape = {
    'ddce6270-82ec-45a6-a05c-2b7b33f8e81a': 'DroneCore',
    '0e0f91dc-d19e-433d-8813-b9877694f04c': 'Small Square',
    '2113d51c-e7f1-434a-a5a2-b67c7004547b': 'Horizontal Rectangle',
    'efbe71e5-1bff-43d0-b86c-a1d875d4a6d4': 'L-Shape',
    '6ce052d3-7376-45aa-a1af-240c5c724c09': 'Large Square',
    '3f7e9d96-20d4-41b9-8189-1e76dfcf682d': 'Small Square',
    'd13e85c4-79dc-47af-b007-5511ccac980b': 'Horizontal Rectangle',
    '318e562f-1a37-4103-9da5-8555ccee8cb7': 'Horizontal Rectangle',
    'bfc725cb-8be1-4199-be37-e4004e5e8b9a': 'Horizontal Rectangle',
    'b79f2511-7eed-46e9-b8f0-826e432a83fa': 'Small Square',
    'ba646fe7-06ec-4b80-825b-6e1f4b88414b': 'Horizontal Rectangle',
    'a0b74fbb-6780-4821-b129-1d50ed13aeb5': 'Large Square',
    '04a1156f-7f0e-4a3e-b9d8-833100539865': 'Large Square',
    '998e16a4-ca55-4cf6-a18a-669a4f44fd5d': 'Small Square',
    '1fee80e6-7c62-4f90-8585-8f5f718ded0b': 'Horizontal Rectangle',
    'f2a245b6-0ca3-4d7f-85e1-cd6f1fee2b10': 'Large Square',
    'f6236cdb-e3a1-4c10-80bc-c4a023537442': 'Large Square',
    '71c3352d-ea82-419c-a688-ac31502fa259': 'Small Square',
    '49e26ea0-62de-487a-82f7-3092109ef789': 'Small Square',
    '1f74c7d3-35a0-4259-bc7c-3357d3d1e43e': 'Small Square',
    '3149086a-e89a-4741-8dcd-237613bffc8f': 'Small Square',
    '27839368-eef4-46fa-abaf-a4b49eea1ae9': 'Small Square',
    '5a4350a6-bcd7-4ae0-b7c4-0b25806ff4f7': 'Small Square',
    '446640b0-0d9d-45ad-8af1-fc50f301bb90': 'Small Square',
    '581d29f6-630b-49a2-9d4a-51bc5e119940': 'Small Square',
    'e2aa2b19-3a41-412a-a37a-210ce0f37817': 'Small Square',
    '208a3409-7b89-4f24-a453-9439221d276b': 'Large Square',
    '80381463-f6bd-48fb-95a9-35378e5bb056': 'Large Square',
    'd7bb0b7a-cd9f-47f6-b8d0-ad24d0fe56b8': 'Small Square',
    'c8600c7e-9101-4405-b2b4-5ce9ab9b7604': 'Large Square',
    'd1c28e2a-9d37-4e87-a137-bf1f8b960870': 'Gigadrill',
    'bdc8b084-8c1b-47a9-b08d-0d5ada77e66b': 'Horizontal Rectangle',
    '40f66109-c08d-4a27-9b64-1121e41a5d50': 'Small Square',
    '3e90d4bd-2bea-4640-9eb9-694321c46f7e': 'Small Square',
    '92f885b3-ea18-41b0-a47a-1141ef18c112': 'Small Square',
    'daa343dc-e786-469b-bf86-17363175e4ca': 'Small Square',
    '91e7b774-bf80-4471-809e-b3e583b9045b': 'Small Square',
    '594e36dc-d01b-4088-9e84-99efc2273f54': 'Large Square',
    'c3bd453d-d21e-46dd-8a47-bcb3cd0206c7': 'Large Square',
    '8952d6fb-5310-4976-8056-fc49ea48f012': 'Large Square',
    '4140c75a-13c3-44c5-b949-99fd4d7033d9': 'Small Square',
    '79d96647-7679-4f19-9210-faf7fa5e69f9': 'Small Square',
    'fc2f8520-4708-41b5-b14a-2502580f8bf7': 'Horizontal Rectangle',
    'a011daee-4842-42e0-bbf8-e263432d9549': 'Large Square',
    'ba2a092c-033c-4184-b0c4-1a2e573f901c': 'Small Square',
    '342d81b0-2400-4f26-a027-b50c69350694': 'Horizontal Rectangle',
    '50729739-61f4-49e7-8c41-e31efb022fa5': 'Vertical Rectangle',
    '8bcf3ab6-fff7-43c5-ab51-ac18ad11e339': 'Horizontal Rectangle',
    '83d8bcdc-a7de-4e87-a453-6e242947ce1c': 'Horizontal Rectangle',
    'b5713ecf-dc95-4b92-b8d5-0dca8cc15ca8': 'Horizontal Rectangle',
    '2dc82d84-05c1-4874-ac2d-b69d4a02e88d': 'Horizontal Rectangle',
    'afeb2d03-7820-4ad8-8604-3d91a8ecf0db': 'Horizontal Rectangle',
    '79b0328f-a33c-4f9c-b386-1524a1ce9e91': 'Horizontal Rectangle',
    '6e199749-a05b-4369-8bc3-2b614b5cf911': 'Horizontal Rectangle',
    'c5c58836-b49d-446d-8488-be144ab2e02e': 'Horizontal Rectangle',
    '2be149a7-dd24-4fb8-9f7f-e812c96ff497': 'Horizontal Rectangle',
    '3ff7c4ef-1c36-41c7-9046-3395744f67f6': 'Horizontal Rectangle',
    '1951bd8f-47fd-477f-b355-c17a4ed9d769': 'Horizontal Rectangle',
    '98bf9bdb-6870-4dfe-9e6b-745cef4b5718': 'Horizontal Rectangle',
    'f05542bf-9010-4c72-8761-7c1184e79ad5': 'Horizontal Rectangle',
    '756041b4-fc0a-4723-ad98-e4040975e335': 'Horizontal Rectangle',
    '24d5e58e-3957-4654-9ec1-8b44e91b8041': 'Horizontal Rectangle',
    'fdf93d99-10b5-4a54-b198-918da2adeb49': 'Horizontal Rectangle',
    'd2652058-2815-46c0-8aad-bc6a96423ddc': 'Horizontal Rectangle',
    '25c66ac2-de8e-471f-9d5d-4df094a9ed27': 'Small Square'
}


def main():
    # TODO: unzip drn file programatically
    parts = get_parts("DroneData")
    im_out = "test.png"
    # make_image_from_parts(parts, im_out)
    im_in = "greened.png"
    tree = None

    place_circuit(im_in, tree, "bottom")


def get_rect_origin(current_pixel, orientation):
    short, long = 0.5, 1.5
    if orientation == 'h':
        return current_pixel[0] + long, current_pixel[1] + short
    else:
        return current_pixel[0] + short, current_pixel[1] + long


def place_circuit(im_in, tree, fill_first):
    im = Image.open(im_in)
    available_pixels = get_green_pixels(im)

    index = 0
    while len(available_pixels):
        current_pixel = available_pixels[index]
        can_place, orientation = examine_pixel(current_pixel, available_pixels, fill_first)
        if can_place:
            placement_offsets = get_placement_offsets(orientation)

            # TODO place gate in tree
            print(get_rect_origin(current_pixel, orientation), orientation)

            # Remove used locations from available
            for offset in placement_offsets:
                placement = (offset[0] + current_pixel[0], offset[1] + current_pixel[1])
                available_pixels.remove(placement)
            # Set index to first unused pixel.
            index = 0
        else:
            # Pixel was unusable, go to next unused pixel.
            index += 1
            print(len(available_pixels))

def get_placement_offsets(orientation):
    short = [0, 1]
    long = [0, 1, 2, 3]
    if orientation == 'h':
        return product(long, short)
    else:
        return product(short, long)


def examine_pixel(current_pixel, preferred_locations, fill_first):
    # TODO: use fill_first to determine order of search.
    for orientation in ['h', 'v']:
        can_place = True
        placement_offsets = get_placement_offsets(orientation)
        for offset in placement_offsets:
            placement = (offset[0] + current_pixel[0], offset[1] + current_pixel[1])
            if placement not in preferred_locations:
                can_place = False
                break
        # All good to place
        if can_place:
            return can_place, orientation
    return False, 'h'


def get_green_pixels(im):
    green_pixels = []
    for y_pos in range(im.height):
        for x_pos in range(im.width):
            pix_data = im.getpixel((x_pos, y_pos))
            if is_green(pix_data):
                green_pixels.append((x_pos, y_pos))
    return green_pixels


def is_green(pix_data):
    m = max(pix_data)
    r, g, b= pix_data
    return g == m and g != b and g != r


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

    part = {
        'PrefabId': 'ddce6270-82ec-45a6-a05c-2b7b33f8e81a',
        'position': (0, 0),
        'orientation': 0
    }
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


def apply_rotation(pixel_locations, orientation):
    rotation_functions = {
        0: lambda pos : pos,
        90: lambda pos : [pos[1], -pos[0]],
        180: lambda pos: [-pos[0], -pos[1]],
        270: lambda pos: [-pos[1], pos[0]]
    }
    pixel_locations = map(rotation_functions[orientation], pixel_locations)
    return pixel_locations


def draw_part(im, part, height, width, padding):
    part_shape = prefab_to_shape[part["PrefabId"]]
    print(part["PrefabId"], part_shape, part["position"], part["orientation"])
    pixel_locations = shape_to_pixels[part_shape]
    pixel_locations = apply_rotation(pixel_locations, part['orientation'])
    for pixel_location in pixel_locations:
        pos = apply_offset(part['position'], pixel_location, height, width, padding)
        pos = [ round(val - 0.5) for val in pos]
        im.putpixel(pos, RED)


def make_image_from_parts(parts, image_out, padding=10):
    height, width = get_drone_size_info(parts)
    image_size = [width + 2 * padding, height + 2 * padding]
    im = Image.new('RGB', image_size)
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0) + im.size, WHITE)

    for part in parts:
        draw_part(im, part, height, width, padding)

    im.show()
    im.save(image_out)


if __name__ == '__main__':
    main()
