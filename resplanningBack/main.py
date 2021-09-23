from Planer import Planer

def main():
    availabilities = [
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True, True, True, True]
    ]
    slots = 0 if len(availabilities) == 0 else len(availabilities[0])
    people = len(availabilities)
    on_call_times = 7
    rules_by_person = [
        {
            "method": "at_most",
            "param": 2,
            "counter": slots,
            "people": range(people),
            "on_call_times": ["0", "1"]
        },
        {
            "method": "at_most",
            "param": 3,
            "counter": slots,
            "people": range(people),
            "on_call_times": ["0+1"]
        },
        {
            "method": "at_most",
            "param": 1,
            "counter": 2,
            "people": range(people),
            "on_call_times": ["0+1", "6"]
        },
        {
            "method": "at_most",
            "param": 2,
            "counter": 3,
            "people": range(people),
            "on_call_times": ["2"]
        }
    ]
    rules_by_slot = [
        {
            "method": "exact",
            "param": 2,
            "counter": people,
            "slots": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "on_call_times": ["0", "1"]
        },
        {
            "method": "at_most",
            "param": 1,
            "counter": people,
            "slots": [0, 1, 2, 3, 4, 5, 6, 7],
            "on_call_times": ["3"]
        },
        {
            "method": "at_least",
            "param": 3,
            "counter": people,
            "slots": [0, 1, 2, 3, 4, 5, 6, 7],
            "on_call_times": ["2"]
        },
        {
            "method": "at_most",
            "param": 6,
            "counter": people,
            "slots": [0, 1, 2, 3, 4, 5, 6, 7],
            "on_call_times": ["2"]
        },
        {
            "method": "exact",
            "param": 0,
            "counter": people,
            "slots": [0, 1, 2, 3, 4, 5, 6, 7],
            "on_call_times": ["4", "5"]
        },
        {
            "method": "exact",
            "param": 0,
            "counter": people,
            "slots": [8, 9],
            "on_call_times": ["2", "6", "3"]
        },
        {
            "method": "at_most",
            "param": 3,
            "counter": people,
            "slots": [8, 9],
            "on_call_times": ["5"]
        },
    ]

    planer = Planer(on_call_times, availabilities, rules_by_person, rules_by_slot)
    print(planer.generate())

if __name__ == '__main__':
    main()