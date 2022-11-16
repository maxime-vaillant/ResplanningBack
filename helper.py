from typing import List


def parse_people(slots: List[int], people: List[int], rules_by_person: List[dict]) -> List[dict]:
    for rule in rules_by_person:
        if rule['counter'] == -1 and rule['slots'] and rule['slots'][0] == -1:
            rule['counter'] = len(slots)
        elif rule['counter'] == -1:
            rule['counter'] = len(rule['slots'])
        if rule['people'] and rule['people'][0] == -1:
            rule['people'] = people
        if rule['slots'] and rule['slots'][0] == -1:
            rule['slots'] = slots
    return rules_by_person


def parse_slots(slots: List[int], people: List[int], rules_by_slot: List[dict]) -> List[dict]:
    for rule in rules_by_slot:
        if rule['counter'] == -1 and rule['people'] and rule['people'][0] == -1:
            rule['counter'] = len(people)
        elif rule['counter'] == -1:
            rule['counter'] = len(rule['people'])
        if rule['people'] and rule['people'][0] == -1:
            rule['people'] = people
        if rule['slots'] and rule['slots'][0] == -1:
            rule['slots'] = slots
    return rules_by_slot


def get_max_list_int(id_list: List[int]) -> int:
    if len(id_list) == 0:
        return 0
    return max(id_list) + 1
