#!/bin/env python3

from db import __core_db__ as coredb

class SymptomExtracted:

    def __init__(self, extracted_id, input_id, symptom_id, confidance_score):
        self.__extracted_id = extracted_id
        self.__input_id = input_id
        self.__symptom_id = symptom_id
        self.__confidance_score = confidance_score
    
    def get_input_id(self):
        return self.__input_id
    
    def get_extracted_id(self):
        return self.__extracted_id
    
    def get_symptom_id(self):
        return self.__symptom_id
    
    def get_confidance_score(self):
        return self.__confidance_score

class SymptomExtracteds:

    def __init__(self):
        self.__extracted: list[SymptomExtracted] = []
    
    def add(self, symptom: SymptomExtracted):
        if symptom is not None and  symptom not in self.__extracted:
            self.__symptoms.append(symptom)
    
    def get_symptom_extracted_by_id(self, id):
        l = SymptomExtracteds()
        for i in self.__extracted:
            if id == i.get_extracted_id():
                l.add(i)
        return l
    
    def get_symptom_extracted_by_input_id(self, id):
        l = SymptomExtracteds()
        for i in self.__extracted:
            if id == i.get_input_id():
                l.add(i)
        return l
    
    def get_symptom_extracted_by_symptom_id(self, id):
        l = SymptomExtracteds()
        for i in self.__extracted:
            if id == i.get_symptom_id():
                l.add(i)
        return l
    
    def get_symptom_extracted_by_confidance_score(self, score):
        l = SymptomExtracteds()
        for i in self.__extracted:
            if score == i.get_confidance_score():
                l.add(i)
        return l
    
    def get_symptom_extreacted_list(self):
        return self.__extracted


cache_all_symptom_extracted : SymptomExtracted | None = None

def get_symptom_extracted_by_id(extrac_id: int) -> SymptomExtracted:
    if cache_all_symptom_extracted is None:
        get_all_symptom_extracted()
    return cache_all_symptom_extracted.get_extracted_id(extrac_id)

def get_symptom_extracted_by_input_id(input_id: int) -> SymptomExtracted:
    if cache_all_symptom_extracted is None:
        get_all_symptom_extracted()
    return cache_all_symptom_extracted.get_input_id(input_id)

def get_symptom_extracted_by_symptom_id(symptom_id: int) -> SymptomExtracted:
    if cache_all_symptom_extracted is None:
        get_all_symptom_extracted()
    return cache_all_symptom_extracted.get_symptom_id(symptom_id)

def get_symptom_extracted_by_confidance_score(score: int) -> SymptomExtracted:
    if cache_all_symptom_extracted is None:
        get_all_symptom_extracted()
    return cache_all_symptom_extracted.get_confidance_score(score)


def get_all_symptom_extracted() -> SymptomExtracteds:
    symptoms_list = SymptomExtracteds()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT extracted_id, input_id, symptom_id, confidance_score FROM extracted_symptoms;")
        dat = cursor.fetchall()
        if dat:
            for dataOne in dat:
                if dataOne:
                    symptom_1 = SymptomExtracted(dataOne[0], dataOne[1], dataOne[2], dataOne[3])
                    symptoms_list.add(symptom=symptom_1)
    except Exception as e:
        print(f"Error retrieving all symptom_extract from extracted_symptoms table: {e}")
    conn.close()
    global cache_all_symptom_extracted
    cache_all_symptom_extracted = symptoms_list
    return symptoms_list

def add_new_symptom_extracted(input_id, symptom_id, confidance_score) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO extracted_symptoms (input_id, symptom_id, confidance_score) VALUES (?, ?, ?)",
            (input_id, symptom_id, confidance_score)
            )
        conn.commit()
        conn.close()
        get_all_symptom_extracted()
        return True
    except Exception as e:
        print(f"Error creating symptom extract: {e}")
        conn.rollback()
        conn.close()
        return False

def get_all_symptom_extracted_cache(refresh_cache:bool = False)-> SymptomExtracteds:
    global cache_all_symptom_extracted
    if cache_all_symptom_extracted is None or cache_all_symptom_extracted == [] or refresh_cache:
        get_all_symptom_extracted()
    return cache_all_symptom_extracted

