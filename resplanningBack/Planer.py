from itertools import combinations
from typing import List, Tuple, Dict, TypedDict
from pysat.solvers import Solver

class RawRule(TypedDict):
    counter: int
    disable: bool
    exigency: int
    method: str
    on_call_times: List[str]
    param: int
    people: List[int]
    slots: List[int]

class ParsedRule(TypedDict):
    counter: int
    disable: bool
    exigency: int
    method: str
    on_call_times: List[List[int]]
    param: int
    people: List[int]
    slots: List[int]
    vars: List[List[int]]

class Planer:
    def __init__(self, slots: List[int], people: List[int], on_call_times: List[int], planning: dict[str: dict[str: dict]], rules_by_person: List[RawRule], rules_by_slot: List[RawRule]):
        self.__slots_id: List[int] = slots
        self.__slots_length: int = len(slots)

        self.__people_id: List[int] = people
        self.__people_length: int = len(people)

        self.__on_call_times_id: List[int] = on_call_times
        self.__on_call_times_length: int = len(on_call_times)

        self.__rules_by_person = self.__parse_rules(rules_by_person)
        self.__rules_by_slot = self.__parse_rules(rules_by_slot)
        self.__planning = planning

        print(self.__rules_by_slot)

        self.__solver = Solver()

    def __del__(self):
        self.__solver.delete()

    @staticmethod
    def __get_actual_id(solve_id: int, actual_ids: List[int]) -> int:
        return actual_ids[solve_id]

    @staticmethod
    def __get_solver_id(actual_id: int, actual_ids: List[int]) -> int:
        return actual_ids.index(actual_id)

    @staticmethod
    def __parse_rules(rules: List[RawRule]) -> List[ParsedRule]:
        parsed_rule: List[ParsedRule] = []
        for rule in rules:
            parsed_rule.append({
                'counter': rule['counter'],
                'disable': rule['disable'],
                'exigency': rule['exigency'],
                'method': rule['method'],
                'on_call_times': [
                    [int(i) for i in on_call_time_str.split('+')] for on_call_time_str in rule['on_call_times']
                ],
                'param': rule['param'],
                'people': rule['people'],
                'slots': rule['slots'],
                'vars': [[] for _ in range(len(rule['on_call_times']))]
            })
        return parsed_rule

    def __cell_to_variable(self, person_id: int, slot_id: int, on_call_time_id: int) -> int:
        person_solver_id: int = self.__get_solver_id(person_id, self.__people_id)
        slot_solver_id: int = self.__get_solver_id(slot_id, self.__slots_id)
        on_call_time_solver_id: int = self.__get_solver_id(on_call_time_id, self.__on_call_times_id)
        return (person_solver_id * self.__slots_length + slot_solver_id) * self.__on_call_times_length + on_call_time_solver_id + 1

    def __variable_to_cell(self, var: int) -> Tuple[int, int, int]:
        var -= 1
        person_id, rest = var // (self.__slots_length * self.__on_call_times_length), var % (
                    self.__slots_length * self.__on_call_times_length)
        slot_id = rest // self.__on_call_times_length
        on_call_time_id = var % self.__on_call_times_length
        return (
            self.__get_actual_id(person_id, self.__people_id),
            self.__get_actual_id(slot_id, self.__slots_id),
            self.__get_actual_id(on_call_time_id, self.__on_call_times_id)
        )

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

    def __create_rule_on_cell_available(self, person_id: int, slot_id: int, on_call_times_concerned: List[List[int]]):
        vars = []
        for on_call_time_id in self.__on_call_times_id:
            if [on_call_time_id] in on_call_times_concerned:
                vars.append(self.__cell_to_variable(person_id, slot_id, on_call_time_id))
            else:
                self.__solver.add_clause([-self.__cell_to_variable(person_id, slot_id, on_call_time_id)])
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
        for rule_index, on_call_time_ids in enumerate(rule['on_call_times']):
            for on_call_time_id in on_call_time_ids:
                rule['vars'][rule_index].append(
                    self.__cell_to_variable(
                        person_id,
                        slot_id,
                        on_call_time_id
                    )
                )
            if len(rule['vars'][rule_index]) == rule['counter'] * len(on_call_time_ids):
                self.__add_clause(rule['method'], rule['vars'][rule_index], rule['param'])
                for _ in range(len(on_call_time_ids)):
                    rule['vars'][rule_index].pop(0)

    def __add_rules_on_cell_by_slot(self):
        for slot_id in self.__slots_id:
            on_call_times_concerned = [[0]]
            for rule in self.__rules_by_slot:
                if slot_id in rule['slots']:
                    for on_call_time in rule['on_call_times']:
                        if on_call_time not in on_call_times_concerned:
                            on_call_times_concerned.append(on_call_time)
            print(slot_id, on_call_times_concerned)
            self.__clear_rule_vars(self.__rules_by_slot)
            for person_id in self.__people_id:
                if str(person_id) in self.__planning and str(slot_id) in self.__planning[str(person_id)]:
                    self.__create_rule_on_cell_available(person_id, slot_id, on_call_times_concerned)
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

    @staticmethod
    def __variance(list_var) -> float:
        avg: float = sum(list_var) / len(list_var)
        tot: int = 0
        for elem in list_var:
            tot += (elem - avg) ** 2
        return tot / (len(list_var) - 1)

    def __evaluate_model(self, model):
        model_counter = {}
        for on_call_time_id in self.__on_call_times_id:
            model_counter[str(on_call_time_id)] = {}
            for person_id in self.__people_id:
                model_counter[str(on_call_time_id)][str(person_id)] = 0
        for var in model:
            if var > 0:
                person_id, slot_id, on_call_time_id = self.__variable_to_cell(var)
                model_counter[str(on_call_time_id)][str(person_id)] += 1
        tot = 0
        for on_call_time_id in self.__on_call_times_id:
            tot += self.__variance(model_counter[str(on_call_time_id)].values())
        return tot / len(self.__on_call_times_id)

    def __find_best_model(self):
        best_model = None
        min_avg_variance = 1000
        self.__solver.conf_budget(2000)
        if self.__solver.solve_limited(expect_interrupt=True):
            current_count = 0
            for counter, model in enumerate(self.__solver.enum_models()):
                current_count += 1
                avg_variance = self.__evaluate_model(model)
                if avg_variance < min_avg_variance:
                    current_count = 0
                    best_model = model
                    min_avg_variance = avg_variance
                    print(min_avg_variance)
                elif counter > 15000 and current_count > 2000:
                    break
        return best_model

    def generate(self):
        self.__add_rules_on_planning()
        self.__add_rules_on_cell_by_slot()
        self.__add_rules_on_cell_by_person()
        best_model = self.__find_best_model()
        if best_model:
            return self.__return_model(best_model)
        return None