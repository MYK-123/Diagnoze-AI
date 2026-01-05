#!/bin/env python3

from db import __core_db__ as coredb

class Disease:

    def __init__(self, disease_id, disease_name, category, severity_level):
        self.__disease_id = disease_id
        self.__disease_name = disease_name
        self.__category = category
        self.__severity_level = severity_level
    
    def get_disease_id(self):
        return self.__disease_id
    
    def get_disease_name(self):
        return self.__disease_name
    
    def get_category(self):
        return self.__category
    
    def get_severity_level(self):
        return self.__severity_level


class Diseases():

    def __init__(self):
        self.__contents : list[Disease] = []
    
    def get_all_content_list(self):
        return self.__contents
    
    def add(self, content: Disease):
        if content is not None and content not in self.__contents:
            self.__contents.append(content)
    
    def get_diseases_by_id(self, disease_id: int):
        contents = Diseases()
        for i in self.__contents:
            if i.get_disease_id() == disease_id:
                contents.add(i)
        return contents
    
    def get_disease_by_name(self, disease_name: str):
        contents = Diseases()
        for i in self.__contents:
            if disease_name in i.get_disease_name():
                contents.add(i)
        return contents
    
    def get_disease_by_category(self, category: str):
        contents = Diseases()
        for i in self.__contents:
            if category == i.get_category():
                contents.add(i)
        return contents
    
    def get_disease_by_severity_level(self, severity_level: str):
        contents = Diseases()
        for i in self.__contents:
            if severity_level == i.get_severity_level():
                contents.add(i)
        return contents


cache_all_diseases : Diseases | None = None

def get_all_diseases() -> Diseases:
    contetn_list = Diseases()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT disease_id, disease_name, category, severity_level FROM disease;")
        dat = cursor.fetchall()
        if dat:
            for dataOne in dat:
                if dataOne:
                    content_1 = Disease(dataOne[0], dataOne[1], dataOne[2], dataOne[3])
                    contetn_list.add(content_1)
    except Exception as e:
        print(f"Error retrieving all diseases from disease table: {e}")
    conn.close()
    global cache_all_diseases
    cache_all_diseases = contetn_list
    return contetn_list

def add_new_disease(disease_name, category, severity_level) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO disease (disease_name, category, severity_level) VALUES (?, ?, ?)",
            (disease_name, category, severity_level)
            )
        conn.commit()
        conn.close()
        get_all_diseases()
        return True
    except Exception as e:
        print(f"Error creating disease: {e}")
        conn.rollback()
        conn.close()
        return False

def set_disease_data(disease_id, disease_name, category, severity_level) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE disease SET disease_name={disease_name}, category={category}, severity_level={severity_level} WHERE disease_id={disease_id};")
        conn.commit()
        conn.close()
        get_all_diseases()
        return True
    except Exception as e:
        print(f"Error updating disease: {e}")
        conn.rollback()
        conn.close()
        return False


def get_all_diseases_cache(refresh_cache:bool = False)-> Diseases:
    global cache_all_diseases
    if cache_all_diseases is None or cache_all_diseases == [] or refresh_cache:
        get_all_diseases()
    return cache_all_diseases

