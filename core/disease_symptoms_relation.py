#!/bin/env python3

from db import __core_db__ as coredb

class DiseaseSymptomRelation:

    def __init__(self, relation_id, disease_id, symptom_id, strength):
        self.__relation_id = relation_id
        self.__disease_id = disease_id
        self.__symptom_id = symptom_id
        self.__strength = strength
    
    def get_disease_symptom_relation_id(self):
        return self.__relation_id
    
    def get_disease_id(self):
        return self.__disease_id
    
    def get_symptom_id(self):
        return self.__symptom_id
    
    def get_strength(self):
        return self.__strength

class DiseaseSymptomRelations():

    def __init__(self):
        self.__contents : list[DiseaseSymptomRelation] = []
    
    def get_all_content_list(self):
        return self.__contents
    
    def add(self, content: DiseaseSymptomRelation):
        if content is not None and content not in self.__contents:
            self.__contents.append(content)
    
    def get_diseases_symptom_relation_by_symptom_id(self, symptom_id: int):
        contents = DiseaseSymptomRelation()
        for i in self.__contents:
            if i.get_symptom_id() == symptom_id:
                contents.add(i)
        return contents
    
    def get_diseases_symptom_relation_by_disease_id(self, disease_id: int):
        contents = DiseaseSymptomRelation()
        for i in self.__contents:
            if i.get_disease_id() == disease_id:
                contents.add(i)
        return contents
    
    def get_diseases_symptom_relation_by_strength(self, strength: float):
        contents = DiseaseSymptomRelation()
        for i in self.__contents:
            if i.get_strength() == strength:
                contents.add(i)
        return contents


cache_all_diseases_symptom_relation : DiseaseSymptomRelations | None = None

def get_all_diseases_symptom_relation() -> DiseaseSymptomRelations:
    contetn_list = DiseaseSymptomRelations()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT id, disease_id, symptom_id, strength FROM disease_symptoms;")
        dat = cursor.fetchall()
        if dat:
            for dataOne in dat:
                if dataOne:
                    content_1 = DiseaseSymptomRelation(dataOne[0], dataOne[1], dataOne[2], dataOne[3])
                    contetn_list.add(content_1)
    except Exception as e:
        print(f"Error retrieving all diseases symptom relation from disease_symptoms table: {e}")
    conn.close()
    global cache_all_diseases_symptom_relation
    cache_all_diseases_symptom_relation = contetn_list
    return contetn_list

def add_new_diseases_symptom_relation(disease_id, symptom_id, strength) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO disease_symptoms (disease_id, symptom_id, strength) VALUES (?, ?, ?)",
            (disease_id, symptom_id, strength)
            )
        conn.commit()
        conn.close()
        get_all_diseases_symptom_relation()
        return True
    except Exception as e:
        print(f"Error creating disease symptom relation: {e}")
        conn.rollback()
        conn.close()
        return False

def set_diseases_symptom_relation_data(relation_id, disease_id, symptom_id, strength) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE disease_symptoms SET disease_id={disease_id}, symptom_id={symptom_id}, strength={strength} WHERE id={relation_id};")
        conn.commit()
        conn.close()
        get_all_diseases_symptom_relation()
        return True
    except Exception as e:
        print(f"Error updating disease symptom relation: {e}")
        conn.rollback()
        conn.close()
        return False


def get_all_diseases_symptom_relation_cache(refresh_cache:bool = False)-> DiseaseSymptomRelations:
    global cache_all_diseases_symptom_relation
    if cache_all_diseases_symptom_relation is None or cache_all_diseases_symptom_relation == [] or refresh_cache:
        get_all_diseases_symptom_relation()
    return cache_all_diseases_symptom_relation

