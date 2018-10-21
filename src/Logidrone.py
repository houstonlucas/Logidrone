import copy
import ast
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import zipfile


def main():
    circuit = [
        {
            'type':'AND',
            'inputs': ['A', 'B'],
            'outputs': ['D']
        },
        {
            'type':'OR',
            'inputs': ['D', 'C'],
            'outputs': ['E']
        }
    ]
    test_writer("test.drn", circuit)


class CircuitReader:
    """
    Base class for reading circuit files.
    """
    accepted_types = ["AND", "OR"]

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
        name = node['outputs']
        maps_to = []
        if name in mapping:
            maps_to = mapping[name]
        ans = []
        for node_index, n in enumerate(self.nodes):
            for output in n['outputs']:
                if output == maps_to:
                    ans.append(node_index)
        return ans
        # raise NotImplementedError

    def create_circuit(self):
        for node in self.nodes:
            connection_indices = self.forward(node)
            for index in connection_indices:
                if self.nodes[index]['type'] in CircuitReader.accepted_types:
                    self.nodes[index]['inputs'].append(node['outputs'])

        self.circuit = [node for node in self.nodes if node['type'] in CircuitReader.accepted_types]


class CircuitReader_Logisim(CircuitReader):

    def __init__(self):
        super(CircuitReader_Logisim, self).__init__()
        self.node_pin_offsets = {'PIN':  {'input':[[0,0]], 'output':[[0,0]]}, 'NOT':  {'input':[[-30,0]], 'output':[[0,0]]}, 'AND':  {'input':[[-50,-20],[-50,-10],[-50,0],[-50,10],[-50,20]], 'output':[[0,0]]}, 'OR':   {'input':[[-50,-20],[-50,-10],[-50,0],[-50,10],[-50,20]], 'output':[[0,0]]}, 'NOR':  {'input':[[-60,-20],[-60,-10],[-60,0],[-60,10],[-60,20]], 'output':[[0,0]]}, 'NAND': {'input':[[-60,-20],[-60,-10],[-60,0],[-60,10],[-60,20]], 'output':[[0,0]]}, 'XOR':  {'input':[[-60,-20],[-60,-10],[-60,0],[-60,10],[-60,20]], 'output':[[0,0]]}, 'XNOR': {'input':[[-70,-20],[-70,-10],[-70,0],[-70,10],[-70,20]], 'output':[[0,0]]}}

    def load_file(self, file_name):
        with open(file_name, 'rt') as base_file:
            self.loigisim_tree = ET.parse(base_file)
        self.loigisim_iter = self.loigisim_tree.getiterator()
        # raise NotImplementedError

    def get_nodes(self):
        for item in self.loigisim_iter:
            if item.tag == "comp":
                comp = {}
                comp['input_loc'] = []
                comp['output_loc'] = []
                comp['output_loc'].append(item.get("loc"))
                comp['type'] = item.get("name").split(' ')[0].upper()
                attributes = item.getchildren()
                for attr in attributes:
                    if attr.get("name") == 'label':
                        comp['name'] = attr.get("val")
                self.nodes.append(comp)
        # raise NotImplementedError

    def get_wires(self):
        for item in self.loigisim_iter:
            if item.tag == 'wire':
                self.wires.append([eval(item.get('from')),eval(item.get('to'))])
        # raise NotImplementedError

    def have_available(self, f_pos, l_pos):
        for wire in self.wires:
            if wire[0] == eval(str(f_pos)) and wire[1] != eval(str(l_pos)):
                return True
            elif wire[1] == eval(str(f_pos))  and wire[0] != eval(str(l_pos)):
                return True
        return False

    def get_next_layer(self, f_pos, l_pos):
        #l_pos = f_pos
        n_layer = []
        for wire in self.wires:
            if wire[0] == eval(str(f_pos)) and wire[1] != eval(str(l_pos)):
                n_layer.append(wire[1])
            elif wire[1] == eval(str(f_pos))  and wire[0] != eval(str(l_pos)):
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
                            if end_point[0] == offset[0]+eval(str(self.nodes[i]['output_loc'][0]))[0] and end_point[1] == offset[1]+eval(str(self.nodes[i]['output_loc'][0]))[1]:
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
        y_pos = 0
        for gate in circuit:
            x_pos = 0
            for orientation in ["n", "e", "s", "w"]:
                position = (x_pos, y_pos)
                self.add_gate(gate, position, orientation)
                x_pos += 4
            y_pos += 6

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
            name = "Input {}".format(input_index + 1)
            input_binding = self.generate_KeyBindingData(name, input_tag)
            child_keybindings.append(input_binding)

        child_eventbindings = child.find("EventBindings")

        for output_index, output_tag in enumerate(gate['outputs']):
            # TODO make this accept various names
            name = "Output"
            output_binding = self.generate_KeyBindingData(name, output_tag)
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


def test_writer(filename, circuit):
    dw = DroneWriter()
    dw.set_drone_name("test_article")
    dw.set_drone_description("This is a test article created by Logidrone!")
    dw.construct_circuit(circuit)
    dw.write_to_file(filename)


def test_reader():
    cr = CircuitReader()
    cr.nodes = [
        {
            'outputs': "A",
            'type': "INPUT",
            'inputs': []
        },
        {
            'outputs': "B",
            'type': "INPUT",
            'inputs': []
        },
        {
            'outputs': "C",
            'type': "INPUT",
            'inputs': []
        },
        {
            'outputs': "D",
            'type': "AND",
            'inputs': []
        },
        {
            'outputs': "E",
            'type': "OR",
            'inputs': []
        },
    ]
    cr.create_circuit()
    return cr.circuit


if __name__ == '__main__':
    main()
