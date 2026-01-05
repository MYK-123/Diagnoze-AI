#!/bin/env python3

from db import __core_db__ as coredb

class SymptomInput:

    def __init__(self, input_id, user_id, input_text, created_at):
        self.__input_id = input_id
        self.__user_id = user_id
        self.__input_text = input_text
        self.__created_at = created_at
    
    def get_input_id(self):
        return self.__input_id
    
    def get_user_id(self):
        return self.__user_id
    
    def get_input_text(self):
        return self.__input_text
    
    def get_created_at(self):
        return self.__created_at

class SymptomInputs:

    def __init__(self):
        self.__symptomsInputs: list[SymptomInput] = []
    
    def add(self, symptom: SymptomInput):
        if symptom is not None and  symptom not in self.__symptomsInputs:
            self.__symptoms.append(symptom)
    
    def get_symptom_inputs_by_id(self, id):
        l = SymptomInputs()
        for i in self.__symptomsInputs:
            if id == i.get_input_id():
                l.add(i)
        return l
    
    def get_symptom_inputs_by_user_id(self, user_id):
        l = SymptomInputs()
        for i in self.__symptomsInputs:
            if user_id in i.get_user_id():
                l.add(i)
        return l
    
    def get_symptom_inputs_by_created_on(self, created_at):
        l = SymptomInputs()
        for i in self.__symptomsInputs:
            if created_at == i.get_created_at():
                l.add(i)
        return l
    
    def get_symptom_inputs_list(self):
        return self.__symptoms



cache_all_symptom_inputs : SymptomInputs | None = None

def get_symptom_by_id(input_id: int) -> SymptomInputs:
    if cache_all_symptom_inputs is None:
        get_all_symptom_inputs()
    return cache_all_symptom_inputs.get_symptom_inputs_by_id(input_id)

def get_symptoms_by_name(name:str) -> SymptomInputs:
    if cache_all_symptom_inputs is None:
        get_all_symptom_inputs()
    return cache_all_symptom_inputs.get_symptom_inputs_by_user_id(name)

def get_symptoms_by_created_at(created_at) -> SymptomInputs:
    if cache_all_symptom_inputs is None:
        get_all_symptom_inputs()
    return cache_all_symptom_inputs.get_symptom_inputs_by_created_on(created_at)


def get_all_symptom_inputs() -> SymptomInputs:
    symptoms_list = SymptomInputs()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT input_id, user_id, input_text, created_at FROM symptom_inputs;")
        dat = cursor.fetchall()
        if dat:
            for dataOne in dat:
                if dataOne:
                    symptom_1 = SymptomInput(dataOne[0], dataOne[1], dataOne[2], dataOne[3])
                    symptoms_list.add(symptom=symptom_1)
    except Exception as e:
        print(f"Error retrieving all symptom_input from symptom_inputs table: {e}")
    conn.close()
    global cache_all_symptom_inputs
    cache_all_symptom_inputs = symptoms_list
    return symptoms_list

def add_new_symptom_input(user_id, input_text) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO symptom_inputs (user_id, input_text) VALUES (?, ?)",
            (user_id, input_text)
            )
        conn.commit()
        conn.close()
        get_all_symptom_inputs()
        return True
    except Exception as e:
        print(f"Error creating symptom input: {e}")
        conn.rollback()
        conn.close()
        return False

def get_all_symptom_inputs_cache(refresh_cache:bool = False)-> SymptomInputs:
    global cache_all_symptom_inputs
    if cache_all_symptom_inputs is None or cache_all_symptom_inputs == [] or refresh_cache:
        get_all_symptom_inputs()
    return cache_all_symptom_inputs
