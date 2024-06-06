import argparse
from faker import Faker
import random
import json
from pathlib import Path
import time
import os


fake = Faker()

LAYERS = {
    "0": ["RM"],
    "1": ["RP1", "RP2", "RP3", "RD"],
    "2": ["RG"],
    "3": ["RC"],
    "4": ["RV"]
}

SUB_LAYERS = {
    "1":  "RD",
    "2": "RG",
    "3": "RC",
    "4": "RV"
}

PERCENTAGE_OF_POPULATION = {
    "RP1": 0.05,
    "RP2": 0.05,
    "RP3": 0.05,
    "RD": 0.05,
    "RG": 0.2,
    "RC": 0.2,
    "RV": 0.4
}


def write_data(data):
    os.system(f'rm -f data/*')
    Path("data").mkdir(parents=True, exist_ok=True)
    payload={}
    for tree in data:
        for key in tree.keys():
            items = tree[str(key)]
            if key not in payload:
                payload[key]=[]
            for item in items:
                payload[key].append(item)

    for key in payload.keys():
            payload_to_insert = payload[str(key)]
            with open(f"data/{key.lower()}.json", 'a', encoding='utf-8') as file:
                json.dump(payload_to_insert, file, ensure_ascii=False)


def generate_cpf():
    numbers = [str(random.randint(0, 9)) for _ in range(11)]
    return ''.join(numbers)


def new_person():
    return {
        "id": time.time(),
        "name": fake.name(),
        "cpf": generate_cpf(),
        "name": fake.name(),
        "email": fake.email(),
    }


def generate_persons(n, subordinate_of):
    data = []
    for i in range(n):
        p = new_person()
        p["subordinateOf"] = subordinate_of
        data.append(p)
        print(f'\rProcessing Person {i+1}/{n}...', end='')
    print('\n Generate persons complete!')
    return data


def generate_new_tree(layers_number, layers_element_numbers):
    rm = new_person()
    tree = {"RM": [rm]}
    for layear_number in range(1, layers_number+1):
        print(f'\rGenerate Tree {layear_number+1}/{layers_number+1}', end='')
        layear_labels = LAYERS[str(layear_number)]
        for label in layear_labels:
            if label not in tree:
                tree[label]=[]
            percentage = PERCENTAGE_OF_POPULATION[str(label)]
            number_of_elements = int(layers_element_numbers*percentage)
            if label in ["RP1", "RP2", "RP3", "RD"]:
                tree[label] = generate_persons(number_of_elements, rm["id"])
            else:
                overlayer_label = SUB_LAYERS[str(layear_number-1)]
                overlayer_items = tree[str(overlayer_label)]
                for overlayer in overlayer_items:
                    tree[label]=tree[label]+generate_persons(number_of_elements, overlayer["id"])

            print(f"\nGenerated {number_of_elements} -> {label}")
    return tree


def generate(rm_number, layers_number, element_numbers):
    data = []
    for i in range(rm_number):
        data.append(generate_new_tree(layers_number, element_numbers))
    write_data(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Data - NEO4J")
    parser.add_argument(
        "--rm_number", help="Numero de RMS que devem ser gerados(Default: 1)")
    parser.add_argument("--layers_number", type=int,
                        help="Numero de Camadas abaixo do RM que devem ser criadas(Default: 4 MIN:1)")
    parser.add_argument("--element_numbers", type=int,
                        help="Numero de elementos base (Default:20)")
    args = parser.parse_args()
    rm_number = args.rm_number
    layers_number = args.layers_number
    element_numbers = args.element_numbers
    if rm_number is None or int(rm_number) < 0:
        rm_number = 1
    if layers_number is None or layers_number < 0 or layers_number < 1:
        layers_number = 4
    if element_numbers is None or element_numbers < 0 or element_numbers < 20:
        element_numbers = 20

    generate(int(rm_number), layers_number, element_numbers)
