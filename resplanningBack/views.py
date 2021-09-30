from typing import List

from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from . import Planer as Pln
from . import helper

@api_view(['GET'])
def getDoc(request):
    return HttpResponse("<a href='https://app.swaggerhub.com/apis-docs/maxime-vaillant/resplanning-api/1.0.0' target='_blank'>Documentation</a>")

@api_view(['POST'])
def generate(request):
    try:
        on_call_times: List[int] = request.data['on_call_times']
        slots: List[int] = request.data['slots']
        people: List[int] = request.data['people']
        old_planning: dict[dict] = request.data['planning']
        rules_by_person_brut: List[dict] = request.data['rules_by_person']
        rules_by_slot_brut: List[dict] = request.data['rules_by_slot']
        rules_by_person_active: List[dict] = [x for x in rules_by_person_brut if not x.get('disable', True)]
        rules_by_slot_active: List[dict] = [x for x in rules_by_slot_brut if not x.get('disable', True)]
        rules_by_person: List[dict] = helper.parse_people(slots, people, rules_by_person_active)
        rules_by_slot: List[dict] = helper.parse_slots(slots, people, rules_by_slot_active)
        try:
            planer = Pln.Planer(slots, people, on_call_times, old_planning, rules_by_person, rules_by_slot)
        except:
            return HttpResponse(status=409)
        print('Processing')
        new_planning = planer.generate()
        print(new_planning)
        if new_planning:
            return JsonResponse({'planning': new_planning})
        return HttpResponse(status=404)
    except:
        return HttpResponse(status=400)
