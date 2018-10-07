import copy
import ast
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import zipfile


def main():
    test_writer("test.drn")


class CircuitReader:
    accepted_types = ["AND", "OR"]

    def __init__(self):
        self.data = ''
        self.gates = []

    def load_file(self, file_name):
        with open(file_name, 'r') as myfile:
            self.data = myfile.read().replace('\n', '')
        self.data = ast.literal_eval(self.data)
        self.data = ast.literal_eval(self.data['data'])

    def parse_gates(self):
        for gate in self.data[0]:
            if gate[0] in self.accepted_types:
                i_names = []
                for i_put in gate[0]['input']:
                    for t_gate in self.data[0]:
                        if i_put['id'] == t_gate[1]['id']:
                            i_names.append(t_gate[1]['name'])
                self.gates.append({'type': gate[0], 'inputs': i_names, 'outputs': [gate[0]['name']]})


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
        self.part_format = template_root.find("Part_Format")
        self.keybinding_format = template_root.find("KeyBinding_Format")

        self.x_pos = 0
        self.y_pos = 5

        self.clean_up_temp = False

    def construct_circuit(self, circuit):
        for gate in circuit:
            self.add_gate(gate)

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

    def add_gate(self, gate):
        drone_children = self.root_drone_part.find("Children")
        new_child = self.make_child(gate)
        drone_children.append(new_child)

    def make_child(self, gate):
        gate_type = gate['type']
        prefab_id = DroneWriter.prefab_id_lookup[gate_type]

        child = copy.deepcopy(self.part_format[0])
        prefab = child.find("PrefabId")
        prefab.text = prefab_id
        orig_pos = child.find("OriginalPosition")
        orig_x = orig_pos.find('x')
        orig_y = orig_pos.find('y')
        orig_x.text = str(self.x_pos)
        orig_y.text = str(self.y_pos)
        self.y_pos += 2

        return child


# Inspired from https://pymotw.com/2/xml/etree/ElementTree/create.html
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    indent = "  "
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    reparsed = reparsed.toprettyxml(indent=indent)
    lines = reparsed.split("\n")
    filtered_lines = [line for line in lines if not re.match(r'^\s*$', line)]
    reparsed = "\n".join(filtered_lines)
    return reparsed


def test_writer(filename):
    circuit = [
        {
            'type': 'AND',
            'inputs': ['A', 'B'],
            'outputs': ['D']
        },
        {
            'type': 'OR',
            'inputs': ['D', 'C'],
            'outputs': ['E']
        }
    ]
    dw = DroneWriter()
    dw.construct_circuit(circuit)
    dw.write_to_file(filename)


if __name__ == '__main__':
    main()
