from typing import List

from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import Planer as p

@api_view(['GET', 'POST'])
def helloWorld(request):
    if request.method == 'POST':
        return JsonResponse({"message": "Hello world from POST"})
    return JsonResponse({"message": "Hello, world!"})

@api_view(['POST'])
def generate(request):
    on_call_times: List[dict] = request.data['on_call_times']
    slots = request.data['slots']
    people = request.data['people']
    old_planning = request.data['planning']
    rules_by_person = request.data['rules_by_person']
    rules_by_slot = request.data['rules_by_slot']
    for rule in rules_by_person:
        if rule['counter'] == 'all' and rule['slots'] and rule['slots'][0] == 'all':
            rule['counter'] = len(slots)
        elif rule['counter'] == 'all':
            rule['counter'] = len(rule['slots'])
        if rule['people'] and rule['people'][0] == 'all':
            rule['people'] = people
        if rule['slots'] and rule['slots'][0] == 'all':
            rule['slots'] = slots
    for rule in rules_by_slot:
        if rule['counter'] == 'all' and rule['people'] and rule['people'][0] == 'all':
            rule['counter'] = len(people)
        elif rule['counter'] == 'all':
            rule['counter'] = len(rule['people'])
        if rule['people'] and rule['people'][0] == 'all':
            rule['people'] = people
        if rule['slots'] and rule['slots'][0] == 'all':
            rule['slots'] = slots
    '''
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
            "on_call_times": ["0+1", "6", "3"]
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
            "method": "exact",
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
            "on_call_times": ["5", "4"]
        },
        {
            "method": "exact",
            "param": 0,
            "counter": people,
            "slots": [8, 9],
            "on_call_times": ["2", "3", "6"]
        },
        {
            "method": "at_most",
            "param": 3,
            "counter": people,
            "slots": [8, 9],
            "on_call_times": ["5"]
        },
    ]
    '''
    planer = p.Planer(slots, people, on_call_times, old_planning, rules_by_person, rules_by_slot)
    print('Processing')
    new_planning = planer.generate()
    print(new_planning)
    if new_planning:
        return JsonResponse({'planning': new_planning})
    return HttpResponse(status=404)
