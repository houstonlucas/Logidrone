import copy
import ast
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import zipfile
import argparse

from PngDrone import *


def main():
    args = process_args()

    if args.command == "circuit_gen":
        circuit_gen(args)
    elif args.command == "mask_gen":
        mask_gen(args)
    elif args.command == "mask_merge":
        mask_merge(args)
    else:
        print("Invalid command: %s" % args.command)
        print("Run with -h flag for information on commands.")
        exit()


multi_input_gates = ["AND", "OR", "NAND", "NOR", "XOR", "XNOR"]

default_description = "This is a test article created by Logidrone!"
default_name = "Logidrone"
default_drone_file = "out.drn"
default_mask_file = "mask.png"

command_help = '''The available commands are:

circuit_gen: Generates a drone with the circuitry given.
    Parameters used: circuit_file, drone_file_out, description, name
    
mask_gen: Generates a mask image from a given drone.
    Parameters used: input_drone, mask_file

mask_merge: Merges the given mask, drone, and circuit.
    Parameters used: circuit_file, input_drone, mask_file, drone_file_out,
        description, name
'''


def circuit_gen(args):
    print("Loading circuit file")
    circuit = retrieve_circuit(args.circuit_file)
    print("Circuit loaded, attempting to generate drone in file: %s" % args.drone_file_out)
    write_circuit_to_new_file(args.drone_file_out, circuit, args.name, args.description)
    print("Successfully written to %s." % args.drone_file_out)


def mask_gen(args):
    print("Parsing drone file")
    parts = get_parts(args.input_drone)
    print("Parts have been parsed, writing to file.")
    make_image_from_parts(parts, args.mask_file)
    print("Succesfully written to %s"%args.mask_file)


def mask_merge(args):
    print("This feature is not fully functional yet. Sorry!")


def process_args():
    parser = argparse.ArgumentParser(
        description='Convert Logisim files into .drn files.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('command', help=command_help)
    parser.add_argument(
        '-f', "--circuit_file",
        help="The path to the digital circuit file."
    )
    parser.add_argument(
        '-i', "--input_drone",
        help='The drone to create a mask from.'
    )
    parser.add_argument(
        '-m', "--mask_file",
        help="The mask image file to decide where gates can be placed."
    )
    parser.add_argument(
        '-o', '--drone_file_out',
        default=default_drone_file, help="The path to output the drone."
    )
    parser.add_argument(
        '-d', '--description', default=default_description,
        help='The description of the drone. (Shown in game.)'
    )
    parser.add_argument(
        '-n', '--name', default=default_name,
        help='The name of the drone. (Shown in game.)'
    )

    args = parser.parse_args()

    check_required_args(args)
    return args


def check_required_args(args):
    requirements_met = True
    if args.command == "circuit_gen":
        if args.circuit_file is None:
            requirements_met = False
            print("Circuit file is a required argument for circuit_gen.")
    elif args.command == "mask_gen":
        if args.input_drone is None:
            requirements_met = False
            print("Input drone file is a required argument for mask_gen.")
        if args.mask_file is None:
            requirements_met = False
            print("Mask file is a required argument for mask_gen.")
    elif args.command == "mask_merge":
        if args.input_drone is None:
            requirements_met = False
            print("Input drone file is a required argument for mask_merge.")
        if args.mask_file is None:
            requirements_met = False
            print("Mask file is a required argument for mask_merge.")
        if args.circuit_file is None:
            requirements_met = False
            print("Circuit file is a required argument for mask_merge.")
    else:
        requirements_met = False
        print("Invalid command: %s" % args.command)
        print("Run with -h flag for information on commands.")

    if not requirements_met:
        exit()


class CircuitReader:
    """
    Base class for reading circuit files.
    """
    accepted_types = ["AND", "OR", "NAND", "NOR", "XOR", "XNOR", "NOT"]

    def __init__(self):
        self.nodes = []
        self.wires = []
        self.circuit = []

        # The structure of this variable is determined by the derived class.
        self.circuit_data = None

    def load_file(self, file_name):
        """
        Loads relevant data to 'circuit_data' as some
        """
        raise NotImplementedError

    def get_nodes(self):
        """
        Retrieves the nodes (gates, inputs, outputs) from 'circuit_data'.
        """
        raise NotImplementedError

    def get_wires(self):
        """
        Retrieves the wires from 'circuit_data'.
        """
        raise NotImplementedError

    def forward(self, node):
        """
        Returns a list of nodes to which the given node passes data.
        """
        mapping = {
            'A': 'D',
            'B': 'D',
            'C': 'E',
            'D': 'E'
        }
        name = node['output']
        maps_to = []
        if name in mapping:
            maps_to = mapping[name]
        ans = []
        for node_index, n in enumerate(self.nodes):
            for output in n['output']:
                if output == maps_to:
                    ans.append(node_index)
        return ans
        # raise NotImplementedError

    def create_circuit(self):
        self.get_nodes()
        self.get_wires()
        for node in self.nodes:
            connection_indices = self.forward(node)
            for index in connection_indices:
                if self.nodes[index]['type'] in CircuitReader.accepted_types:
                    self.nodes[index]['inputs'].append(node['output'])

        self.circuit = [node for node in self.nodes if node['type'] in CircuitReader.accepted_types]


class CircuitReader_Logisim(CircuitReader):

    def __init__(self):
        super(CircuitReader_Logisim, self).__init__()
        self.node_pin_offsets = {'PIN': {'input': [[0, 0]], 'output': [[0, 0]]},
                                 'NOT': {'input': [[-30, 0]], 'output': [[0, 0]]},
                                 'AND': {'input': [[-50, -20], [-50, -10], [-50, 0], [-50, 10], [-50, 20]],
                                         'output': [[0, 0]]},
                                 'OR': {'input': [[-50, -20], [-50, -10], [-50, 0], [-50, 10], [-50, 20]],
                                        'output': [[0, 0]]},
                                 'NOR': {'input': [[-60, -20], [-60, -10], [-60, 0], [-60, 10], [-60, 20]],
                                         'output': [[0, 0]]},
                                 'NAND': {'input': [[-60, -20], [-60, -10], [-60, 0], [-60, 10], [-60, 20]],
                                          'output': [[0, 0]]},
                                 'XOR': {'input': [[-60, -20], [-60, -10], [-60, 0], [-60, 10], [-60, 20]],
                                         'output': [[0, 0]]},
                                 'XNOR': {'input': [[-70, -20], [-70, -10], [-70, 0], [-70, 10], [-70, 20]],
                                          'output': [[0, 0]]}}

    def load_file(self, file_name):
        with open(file_name, 'rt') as base_file:
            self.loigisim_tree = ET.parse(base_file)
        self.loigisim_iter = self.loigisim_tree.getiterator()
        # raise NotImplementedError

    def get_nodes(self):
        for item in self.loigisim_iter:
            if item.tag == "comp":
                comp = {}
                comp['inputs'] = []
                comp['input_loc'] = []
                comp['output_loc'] = []
                comp['output_loc'].append(item.get("loc"))
                comp['type'] = item.get("name").split(' ')[0].upper()
                for attr in item:
                    if attr.get("name") == 'label':
                        comp['name'] = attr.get("val")
                        comp['output'] = comp['name']
                self.nodes.append(comp)

    def get_wires(self):
        for item in self.loigisim_iter:
            if item.tag == 'wire':
                self.wires.append([eval(item.get('from')), eval(item.get('to'))])
        # raise NotImplementedError

    def have_available(self, f_pos, l_pos):
        for wire in self.wires:
            if wire[0] == eval(str(f_pos)) and wire[1] != eval(str(l_pos)):
                return True
            elif wire[1] == eval(str(f_pos)) and wire[0] != eval(str(l_pos)):
                return True
        return False

    def get_next_layer(self, f_pos, l_pos):
        # l_pos = f_pos
        n_layer = []
        for wire in self.wires:
            if wire[0] == eval(str(f_pos)) and wire[1] != eval(str(l_pos)):
                n_layer.append(wire[1])
            elif wire[1] == eval(str(f_pos)) and wire[0] != eval(str(l_pos)):
                n_layer.append(wire[0])
        return n_layer

    def get_end_points(self, f_pos, l_pos):
        end_points = []
        next_layer = self.get_next_layer(f_pos, l_pos)
        for ft_pos in next_layer:
            if self.have_available(ft_pos, f_pos):
                end_points.extend(self.get_end_points(ft_pos, f_pos))
            else:
                end_points.append(ft_pos)
        return end_points

    def forward(self, node):
        current_layer = []
        current_layer.append(node['output_loc'][0])
        end_points = self.get_end_points(current_layer[0], current_layer[0])

        indexes = []
        for i in range(len(self.nodes)):
            for comp_type in self.node_pin_offsets:
                if comp_type in self.nodes[i]['type'].upper():
                    for offset in self.node_pin_offsets[comp_type]['input']:
                        for end_point in end_points:
                            if end_point[0] == offset[0] + eval(str(self.nodes[i]['output_loc'][0]))[0] and end_point[
                                1] == offset[1] + eval(str(self.nodes[i]['output_loc'][0]))[1]:
                                indexes.append(i)
        return indexes


class DroneWriter:
    prefab_id_lookup = {
        'BUTTON': '8bcf3ab6-fff7-43c5-ab51-ac18ad11e339',
        'IF': '83d8bcdc-a7de-4e87-a453-6e242947ce1c',
        'NOT': 'b5713ecf-dc95-4b92-b8d5-0dca8cc15ca8',
        'AND': '2dc82d84-05c1-4874-ac2d-b69d4a02e88d',
        'OR': 'afeb2d03-7820-4ad8-8604-3d91a8ecf0db',
        'NOR': '79b0328f-a33c-4f9c-b386-1524a1ce9e91',
        'NAND': '6e199749-a05b-4369-8bc3-2b614b5cf911',
        'XOR': 'c5c58836-b49d-446d-8488-be144ab2e02e',
        'XNOR': '2be149a7-dd24-4fb8-9f7f-e812c96ff497',
        'SWITCH': '3ff7c4ef-1c36-41c7-9046-3395744f67f6',
        'ONOFFSWITCH': '1951bd8f-47fd-477f-b355-c17a4ed9d769',
        'LED': '25c66ac2-de8e-471f-9d5d-4df094a9ed27'
    }
    data_file = "DroneData"
    image_file = "Image.png"

    def __init__(self):
        # Load templates
        template_tree = ET.parse('template.xml')
        template_root = template_tree.getroot()

        self.doc = template_root.find("Base_Format")[0]
        self.root_drone_part = self.doc.find("RootDronePart")
        self.part_format = template_root.find("Part_Format")[0]
        self.keybinding_format = template_root.find("KeyBinding_Format")[0]

        self.clean_up_temp = False

    def construct_circuit(self, circuit):
        y_pos = 5
        x_pos = 0
        for gate in circuit:
            position = (x_pos, y_pos)
            self.add_gate(gate, position, 'n')
            y_pos += 2

    def set_drone_name(self, drone_name):
        self.doc.find("DroneName").text = drone_name

    def set_drone_description(self, drone_description):
        self.doc.find("Description").text = drone_description

    def write_to_file(self, filename):
        str_data = prettify(self.doc)
        with open(DroneWriter.data_file, 'w+') as f:
            f.write(str_data)
        drn_file = zipfile.ZipFile(filename, 'w')
        drn_file.write(DroneWriter.data_file, compress_type=zipfile.ZIP_DEFLATED)
        drn_file.write(DroneWriter.image_file, compress_type=zipfile.ZIP_DEFLATED)
        drn_file.close()

        if self.clean_up_temp:
            os.remove(DroneWriter.data_file)

    def add_gate(self, gate, position, orientation):
        drone_children = self.root_drone_part.find("Children")

        new_child = self.make_child(gate, position, orientation)
        drone_children.append(new_child)

    def make_child(self, gate, position, orientation):
        gate_type = gate['type']
        prefab_id = DroneWriter.prefab_id_lookup[gate_type]

        child = copy.deepcopy(self.part_format)
        prefab = child.find("PrefabId")
        prefab.text = prefab_id

        orig_pos = child.find("OriginalPosition")
        self.set_position_elem(orig_pos, position)

        orig_rotation = child.find("OriginalRotation")
        self.set_rotation_elem(orig_rotation, orientation)

        current_pos = child.find("CurrentPosition")
        self.set_position_elem(current_pos, position)

        current_rotation = child.find("CurrentRotation")
        self.set_rotation_elem(current_rotation, orientation)

        child_keybindings = child.find("KeyBindings")

        for input_index, input_tag in enumerate(gate['inputs']):
            if gate_type in multi_input_gates:
                name = "Input {}".format(input_index + 1)
            else:
                name = "Input"
            input_binding = self.generate_KeyBindingData(name, input_tag)
            child_keybindings.append(input_binding)

        child_eventbindings = child.find("EventBindings")

        # TODO make this accept various names
        name = "Output"
        output_binding = self.generate_KeyBindingData(name, gate['output'])
        child_eventbindings.append(output_binding)

        return child

    def set_position_elem(self, elem, pos):
        x_pos, y_pos = pos
        x_field = elem.find('x')
        y_field = elem.find('y')
        x_field.text = str(x_pos)
        y_field.text = str(y_pos)

    def set_rotation_elem(self, elem, orientation):
        elem.find('x').text = "0"
        elem.find('y').text = "0"
        euler = elem.find("eulerAngles")
        euler.find('x').text = "0"
        euler.find('y').text = "0"
        if orientation == 'n':
            elem.find('z').text = "0"
            elem.find('w').text = "1"
            euler.find('z').text = "0"
        elif orientation == 'w':
            elem.find('z').text = "0.7071068"
            elem.find('w').text = "-0.7071068"
            euler.find('z').text = "90"
        elif orientation == 's':
            elem.find('z').text = "1"
            elem.find('w').text = "0"
            euler.find('z').text = "180"
        elif orientation == 'e':
            elem.find('z').text = "0.7071068"
            elem.find('w').text = "0.7071068"
            euler.find('z').text = "270"
        else:
            raise Exception("Invalid orientation")

    def generate_KeyBindingData(self, name, tag):
        binding = copy.deepcopy(self.keybinding_format)
        binding_name = binding.find("Name")
        binding_name.text = name

        binding_tag = binding.find("Tag")
        binding_tag.text = tag

        binding_set = binding.find("HasBeenAssigned")
        binding_set.text = "true"

        return binding


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    # Inspired from https://pymotw.com/2/xml/etree/ElementTree/create.html
    indent = "  "
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    reparsed = reparsed.toprettyxml(indent=indent)
    lines = reparsed.split("\n")
    filtered_lines = [line for line in lines if not re.match(r'^\s*$', line)]
    reparsed = "\n".join(filtered_lines)
    return reparsed


def write_circuit_to_new_file(filename, circuit, name, description):
    dw = DroneWriter()
    dw.set_drone_name(name)
    dw.set_drone_description(description)
    dw.construct_circuit(circuit)
    dw.write_to_file(filename)


def retrieve_circuit(file_path):
    cr = CircuitReader_Logisim()
    cr.load_file(file_path)
    cr.create_circuit()

    return cr.circuit


if __name__ == '__main__':
    main()
