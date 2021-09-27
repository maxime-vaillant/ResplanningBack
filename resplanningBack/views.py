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
    rules_by_person_filtered = [x for x in rules_by_person if not x.get('disable', True)]
    rules_by_slot_filtered = [x for x in rules_by_slot if not x.get('disable', True)]
    for rule in rules_by_person_filtered:
        if rule['counter'] == 'all' and rule['slots'] and rule['slots'][0] == 'all':
            rule['counter'] = len(slots)
        elif rule['counter'] == 'all':
            rule['counter'] = len(rule['slots'])
        if rule['people'] and rule['people'][0] == 'all':
            rule['people'] = people
        if rule['slots'] and rule['slots'][0] == 'all':
            rule['slots'] = slots
    for rule in rules_by_slot_filtered:
        print(rule)
        if rule['counter'] == 'all' and rule['people'] and rule['people'][0] == 'all':
            rule['counter'] = len(people)
        elif rule['counter'] == 'all':
            rule['counter'] = len(rule['people'])
        if rule['people'] and rule['people'][0] == 'all':
            rule['people'] = people
        if rule['slots'] and rule['slots'][0] == 'all':
            rule['slots'] = slots
    planer = p.Planer(slots, people, on_call_times, old_planning, rules_by_person_filtered, rules_by_slot_filtered)
    print('Processing')
    new_planning = planer.generate()
    print(new_planning)
    if new_planning:
        return JsonResponse({'planning': new_planning})
    return HttpResponse(status=404)
