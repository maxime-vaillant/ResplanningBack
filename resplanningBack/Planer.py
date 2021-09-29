from itertools import combinations
from typing import List, Tuple, Dict
from pysat.solvers import Solver
from . import helper

class Planer:
    def __init__(self, slots: List[int], people: List[int], on_call_times: List[int], planning: dict[str: dict[str: dict]], rules_by_person: List[Dict], rules_by_slot: List[Dict]):
        self.__slots_id = slots
        self.__slots = helper.get_max_list_int(slots)
        self.__people_id = people
        self.__people = helper.get_max_list_int(people)
        self.__on_call_times_id = on_call_times
        self.__on_call_times = helper.get_max_list_int(on_call_times)
        self.__rules_by_person = rules_by_person
        self.__rules_by_slot = rules_by_slot
        self.__planning = planning

        for rule in self.__rules_by_slot + self.__rules_by_person:
            rule['vars'] = [[] for _ in range(len(rule['on_call_times']))]

        self.__solver = Solver()

    def __del__(self):
        self.__solver.delete()

    def __cell_to_variable(self, person_id: int, slot_id: int, on_call_time_id: int) -> int:
        return (person_id * self.__slots + slot_id) * self.__on_call_times + on_call_time_id + 1

    def __variable_to_cell(self, var: int) -> Tuple[int, int, int]:
        var -= 1
        person_id, rest = var // (self.__slots * self.__on_call_times), var % (
                    self.__slots * self.__on_call_times)
        slot_id = rest // self.__on_call_times
        on_call_time_id = var % self.__on_call_times
        return person_id, slot_id, on_call_time_id

    def __add_at_least(self, vars: List[int], param: int):
        for combination in combinations(vars, len(vars) - param + 1):
            clause = []
            for c in combination:
                clause.append(c)
            self.__solver.add_clause(clause)

    def __add_at_most(self, vars: List[int], param: int):
        for combination in combinations([-x for x in vars[:]], param + 1):
            clause = []
            for c in combination:
                clause.append(c)
            self.__solver.add_clause(clause)

    def __add_exact(self, vars: List[int], param: int):
        self.__add_at_least(vars, param)
        self.__add_at_most(vars, param)

    def __add_clause(self, method: str, vars: List[int], params: int):
        if method == 'exact':
            self.__add_exact(vars, params)
        elif method == 'at_least':
            self.__add_at_least(vars, params)
        elif method == 'at_most':
            self.__add_at_most(vars, params)

    def __create_rule_on_cell_available(self, person_id: int, slot_id: int):
        vars = []
        for on_call_time_id in self.__on_call_times_id:
            vars.append(self.__cell_to_variable(person_id, slot_id, on_call_time_id))
        self.__add_exact(vars, 1)

    def __create_rule_on_cell_unavailable(self, person_id: int, slot_id: int):
        for on_call_time_id in self.__on_call_times_id:
            self.__solver.add_clause([-self.__cell_to_variable(person_id, slot_id, on_call_time_id)])

    @staticmethod
    def __clear_rule_vars(rules):
        for rule in rules:
            for vars in rule['vars']:
                vars.clear()

    def __add_rule(self, rule, person_id, slot_id):
        for rule_index, on_call_time_str in enumerate(rule['on_call_times']):
            on_call_time_ids = on_call_time_str.split('+')
            for on_call_time_id in on_call_time_ids:
                rule['vars'][rule_index].append(
                    self.__cell_to_variable(
                        person_id,
                        slot_id,
                        int(on_call_time_id)
                    )
                )
            if len(rule['vars'][rule_index]) == rule['counter'] * len(on_call_time_ids):
                self.__add_clause(rule['method'], rule['vars'][rule_index], rule['param'])
                for _ in range(len(on_call_time_ids)):
                    rule['vars'][rule_index].pop(0)

    def __add_rules_on_cell_by_slot(self):
        for slot_id in self.__slots_id:
            self.__clear_rule_vars(self.__rules_by_slot)
            for person_id in self.__people_id:
                if str(person_id) in self.__planning and str(slot_id) in self.__planning[str(person_id)]:
                    self.__create_rule_on_cell_available(person_id, slot_id)
                else:
                    self.__create_rule_on_cell_unavailable(person_id, slot_id)
                for rule in self.__rules_by_slot:
                    if slot_id in rule['slots']:
                        self.__add_rule(rule, person_id, slot_id)

    def __add_rules_on_cell_by_person(self):
        for person_id in self.__people_id:
            self.__clear_rule_vars(self.__rules_by_person)
            for slot_id in self.__slots_id:
                for rule in self.__rules_by_person:
                    if person_id in rule['people']:
                        self.__add_rule(rule, person_id, slot_id)

    def __add_rules_on_planning(self):
        for person_id in self.__people_id:
            for slot_id in self.__slots_id:
                on_call_time_key = None
                row = self.__planning.get(str(person_id), None)
                if row:
                    on_call_time_key = row.get(str(slot_id), None)
                if on_call_time_key is not None:
                    self.__solver.add_clause([self.__cell_to_variable(person_id, slot_id, on_call_time_key)])

    def __print_model(self, model):
        for var in model:
            if var > 0:
                person_id, slot_id, on_call_time_id = self.__variable_to_cell(var)
                print(person_id, slot_id, on_call_time_id)
        print()

    def __return_model(self, model):
        for var in model:
            if var > 0:
                person_id, slot_id, on_call_time_id = self.__variable_to_cell(var)
                self.__planning[str(person_id)][str(slot_id)] = on_call_time_id
        return self.__planning

    def __evaluate_model(self):
        # TODO
        return

    def generate(self):
        self.__add_rules_on_planning()
        self.__add_rules_on_cell_by_slot()
        self.__add_rules_on_cell_by_person()
        self.__solver.conf_budget(2000)
        if self.__solver.solve_limited(expect_interrupt=True):
            for model in self.__solver.enum_models():
                return self.__return_model(model)
        return None