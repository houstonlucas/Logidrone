import ast
import json
import xml.etree.ElementTree as ET


def main():
    test_writer()


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
                self.gates.append({'type':gate[0],'inputs':i_names,'outputs':[gate[0]['name']]})

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

    def __init__(self):
        pass


def test_writer():
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




if __name__ == '__main__':
    main()
