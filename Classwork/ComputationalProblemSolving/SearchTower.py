from itertools import combinations
def get_input():
    numbers = [int(i) for i in input().split()]
    first_tower = numbers[-2]
    second_tower = numbers[-1]
    numbers.pop()
    numbers.pop()
    return [numbers, first_tower, second_tower]

def build_towers(data_list):
    numbers = data_list[0]
    first_tower = data_list[1]
    second_tower = data_list[2]
    for combo in combinations(numbers, 3):
        if sum(combo) == first_tower:
            first_tower_boxes = sorted(combo, reverse=True)
            second_tower_boxes = sorted([n for n in numbers if n not in combo], reverse=True)
            break
    print(f"{first_tower_boxes[0]} {first_tower_boxes[1]} {first_tower_boxes[2]} {second_tower_boxes[0]} {second_tower_boxes[1]} {second_tower_boxes[2]}")
if __name__ == "__main__":
    build_towers(get_input())