import pandas as pd
import helper

from typing import List, Dict
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from planer import Planer
from settings import origins


app = FastAPI(title='Resplanning')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/parse-csv/")
def parse_csv(file: UploadFile = File(...)):
    slots = []
    people = []
    slot_count = 0
    person_count = 0
    planning = {}
    try:
        file_data = pd.read_csv(file.file)
        for index, data in enumerate(file_data.iloc):
            if index == 0:
                for text in data:
                    if not pd.isna(text):
                        slots.append({"key": slot_count, "text": text})
                        slot_count += 1
            else:
                for ind, text in enumerate(data):
                    if ind == 0:
                        if not pd.isna(text):
                            people.append({"key": person_count, "text": text})
                            planning[str(person_count)] = {}
                    else:
                        if not pd.isna(text) and text in ['Oui', 'Yes']:
                            planning[str(person_count)][str(ind - 1)] = None
                person_count += 1
        return {'slots': slots, 'people': people, 'planning': planning}
    except Exception as err:
        return JSONResponse(status_code=400, content='Data error: {}'.format(err))


class GenerateItem(BaseModel):
    on_call_times: List[int]
    slots: List[int]
    people: List[int]
    planning: Dict[str, Dict]
    rules_by_person: List[Dict]
    rules_by_slot: List[Dict]


@app.post("/generate/")
def generate(generate_item: GenerateItem):
    try:
        on_call_times = generate_item.on_call_times
        slots = generate_item.slots
        people = generate_item.people
        old_planning = generate_item.planning
        raw_rules_by_person = generate_item.rules_by_person
        raw_rules_by_slot_brut = generate_item.rules_by_slot

        rules_by_person_active: List[dict] = [
            rule for rule in raw_rules_by_person if not rule.get('disable', True)
        ]
        rules_by_slot_active: List[dict] = [
            rule for rule in raw_rules_by_slot_brut if not rule.get('disable', True)
        ]

        rules_by_person: List[dict] = helper.parse_people(slots, people, rules_by_person_active)
        rules_by_slot: List[dict] = helper.parse_slots(slots, people, rules_by_slot_active)

        try:
            planer = Planer(
                slots,
                people,
                on_call_times,
                old_planning,
                rules_by_person,
                rules_by_slot
            )
            print('Processing')
            new_planning = planer.generate()
            print(new_planning)

            if new_planning:
                return {'planning': new_planning}

        except Exception as err:
            return JSONResponse(status_code=409, content='Process error: {}'.format(err))

        return JSONResponse(status_code=404, content='No model found')

    except Exception as err:
        return JSONResponse(status_code=400, content='Data error: {}'.format(err))
