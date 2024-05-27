from faker import Faker
import json
import random
import math
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import insert

fake = Faker()

PERCENTAGE_OF_POPULATION = {
    "RM": 0.025,
    "RP1": 0.05,
    "RP2": 0.05,
    "RP3": 0.05,
    "RD": 0.05,
    "RG": 0.2,
    "RC": 0.25,
    "RV": 0.325,
}


def get_quantity_users_by_position():
    total_users = input(
        "Digite a quantidade total de pessoas que deseja gerar (o valor padrão é 1000): "
    )

    if (not total_users) or (not total_users.isdigit()) or (int(total_users) <= 0):
        total_users = 1000

    return {
        key: math.ceil(value * int(total_users))
        for key, value in PERCENTAGE_OF_POPULATION.items()
    }


def generate_possibilities(numbers_drawn, possible_ids):
    if len(numbers_drawn) == len(possible_ids):
        numbers_drawn.clear()
    return [number for number in possible_ids if number not in numbers_drawn]


def generate_users(all_values):
    all_users = {}
    for _, position in enumerate(all_values):
        users = []
        keys = list(all_values.keys())
        previous_position = keys[keys.index(position) - 1]

        if position in ["RP1", "RP2", "RP3", "RD"]:
            previous_position = "RM"
        possible_ids = list(range(1, (all_values[previous_position]) + 1))
        numbers_drawn = []

        for i in range(1, (all_values[position] + 1)):
            if position == "RM":
                users.append({"id": i, "name": fake.name()})
            else:
                possibilities = generate_possibilities(numbers_drawn, possible_ids)
                number_drawn = random.choice(possibilities)
                numbers_drawn.append(number_drawn)
                subordinateOf = number_drawn
                users.append(
                    {
                        "id": i,
                        "name": fake.name(),
                        "subordinateOf": subordinateOf,
                    }
                )
        all_users[position] = users
    return all_users


def save_users(users):
    for key, value in users.items():
        with open(f"data/{key.lower()}.json", "w") as f:
            json.dump(value, f, indent=4)


if __name__ == "__main__":

    quantity_users_by_position = get_quantity_users_by_position()
    all_users = generate_users(quantity_users_by_position)
    save_users(all_users)
    for key, value in all_users.items():
        print(f"{key} gerados: {len(value)}")
    insert.run()
