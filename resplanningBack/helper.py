from typing import List

def parse_people(slots: List[int], people: List[int], rules_by_person: List[dict]) -> List[dict]:
    for rule in rules_by_person:
        if rule['counter'] == 'all' and rule['slots'] and rule['slots'][0] == 'all':
            rule['counter'] = len(slots)
        elif rule['counter'] == 'all':
            rule['counter'] = len(rule['slots'])
        if rule['people'] and rule['people'][0] == 'all':
            rule['people'] = people
        if rule['slots'] and rule['slots'][0] == 'all':
            rule['slots'] = slots
    return rules_by_person

def parse_slots(slots: List[int], people: List[int], rules_by_slot: List[dict]) -> List[dict]:
    for rule in rules_by_slot:
        if rule['counter'] == 'all' and rule['people'] and rule['people'][0] == 'all':
            rule['counter'] = len(people)
        elif rule['counter'] == 'all':
            rule['counter'] = len(rule['people'])
        if rule['people'] and rule['people'][0] == 'all':
            rule['people'] = people
        if rule['slots'] and rule['slots'][0] == 'all':
            rule['slots'] = slots
        return rules_by_slot

def get_max_list_int(id_list: List[int]):
    if len(id_list) == 0:
        return 0
    else:
        return max(id_list) + 1

def get_max_list_str(ids_list: List[str]):
    max_list = 0
    for ids_sublist in ids_list:
        ids = ids_sublist.split('+')
        for id_atom in ids:
            if int(id_atom) > max_list:
                max_list = int(id_atom)
    return max_list + 1
