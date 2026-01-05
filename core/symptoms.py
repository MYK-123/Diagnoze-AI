#!/bin/env python3

from db import __core_db__ as coredb

class Symptom:

    def __init__(self, symptomId, symptomName, symptomCategrory):
        self.__symptom_id = symptomId
        self.__sympname = symptomName
        self.__category = symptomCategrory
    
    def getName(self):
        return self.__sympname
    
    def getId(self):
        return self.__symptom_id
    
    def get_category(self):
        return self.__category

class Symptoms:

    def __init__(self):
        self.__symptoms: list[Symptom] = []
    
    def add(self, symptom: Symptom):
        if symptom is not None and  symptom not in self.__symptoms:
            self.__symptoms.append(symptom)
    
    def get_symptoms_by_id(self, id):
        l = Symptoms()
        for i in self.__symptoms:
            if id == i.getId():
                l.add(i)
        return l
    
    def get_symptoms_by_name(self, name):
        l = Symptoms()
        for i in self.__symptoms:
            if name in i.getName():
                l.add(i)
        return l
    
    def get_symptoms_by_category(self, category):
        l = Symptoms()
        for i in self.__symptoms:
            if category == i.get_category():
                l.add(i)
        return l
    
    def get_symptoms_list(self):
        return self.__symptoms



cache_all_symptoms : Symptoms | None = None

def get_symptom_by_id(symptom_id: int) -> Symptoms:
    if cache_all_symptoms is None:
        get_all_symptoms()
    return cache_all_symptoms.get_symptoms_by_name(symptom_id)

def get_symptoms_by_name(name:str) -> Symptoms:
    if cache_all_symptoms is None:
        get_all_symptoms()
    return cache_all_symptoms.get_symptoms_by_name(name)

def get_all_symptoms() -> Symptoms:
    symptoms_list = Symptoms()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT symptom_id, symptom_name, category FROM symptoms;")
        dat = cursor.fetchall()
        if dat:
            for dataOne in dat:
                if dataOne:
                    symptom_1 = Symptom(dataOne[0], dataOne[1], dataOne[2])
                    symptoms_list.add(symptom=symptom_1)
    except Exception as e:
        print(f"Error retrieving all symptom from symptoms table: {e}")
    conn.close()
    global cache_all_symptoms
    cache_all_symptoms = symptoms_list
    return symptoms_list

def add_new_symptom(symptom_name, category) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO symptoms (symptom_name, category) VALUES (?, ?)",
            (symptom_name, category)
            )
        conn.commit()
        conn.close()
        get_all_symptoms()
        return True
    except Exception as e:
        print(f"Error creating symptom: {e}")
        conn.rollback()
        conn.close()
        return False

def get_all_symptoms_cache(refresh_cache:bool = False)-> Symptoms:
    global cache_all_symptoms
    if cache_all_symptoms is None or cache_all_symptoms == [] or refresh_cache:
        get_all_symptoms()
    return cache_all_symptoms
