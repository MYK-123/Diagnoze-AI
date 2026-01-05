#!/bin/env python3

from db import __core_db__ as coredb

class EducationContent:

    def __init__(self, content_id, disease_id, title, content_text, is_verified):
        self.__content_id = content_id
        self.__disease_id = disease_id
        self.__title = title
        self.__content_text = content_text
        self.__is_verified = is_verified
    
    def get_content_id(self):
        return self.__content_id
    
    def get_disease_id(self):
        return self.__disease_id
    
    def get_title(self):
        return self.__title
    
    def get_content_text(self):
        return self.__content_text
    
    def get_is_verified(self):
        return self.__is_verified


class EducationContents():

    def __init__(self):
        self.__contents : list[EducationContent] = []
    
    def get_all_content_list(self):
        return self.__contents
    
    def add(self, content: EducationContent):
        if content is not None and content not in self.__contents:
            self.__contents.append(content)
    
    def get_contents_by_content_id(self, content_id: int):
        contents = EducationContents()
        for i in self.__contents:
            if i.get_content_id() == content_id:
                contents.add(i)
        return contents
    
    def get_contents_by_disease_id(self, disease_id: int):
        contents = EducationContents()
        for i in self.__contents:
            if i.get_disease_id() == disease_id:
                contents.add(i)
        return contents
    
    def get_contents_by_title(self, title: str):
        contents = EducationContents()
        for i in self.__contents:
            if title in i.get_title():
                contents.add(i)
        return contents


cache_all_education_content : EducationContents | None = None

def get_all_education_content() -> EducationContents:
    contetn_list = EducationContents()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT content_id, disease_id, title, content_text, is_verified FROM educational_content;")
        dat = cursor.fetchall()
        if dat:
            for dataOne in dat:
                if dataOne:
                    content_1 = EducationContent(dataOne[0], dataOne[1], dataOne[2], dataOne[3], dataOne[4])
                    contetn_list.add(content_1)
    except Exception as e:
        print(f"Error retrieving all contents from educational_content table: {e}")
    conn.close()
    global cache_all_education_content
    cache_all_education_content = contetn_list
    return contetn_list

def add_new_educational_content(disease_id, title, content_text, is_verified) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO educational_content (disease_id, title, content_text, is_verified) VALUES (?, ?, ?, ?)",
            (disease_id, title, content_text, is_verified)
            )
        conn.commit()
        conn.close()
        get_all_education_content()
        return True
    except Exception as e:
        print(f"Error creating educational_content: {e}")
        conn.rollback()
        conn.close()
        return False

def set_educational_content_verification(content_id: int, is_verified: bool) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE educational_content SET  is_verified={is_verified} WHERE content_id={content_id};")
        conn.commit()
        conn.close()
        get_all_education_content()
        return True
    except Exception as e:
        print(f"Error updating educational_content: {e}")
        conn.rollback()
        conn.close()
        return False

def get_all_education_content_cache(refresh_cache:bool = False)-> EducationContents:
    global cache_all_education_content
    if cache_all_education_content is None or cache_all_education_content == [] or refresh_cache:
        get_all_education_content()
    return cache_all_education_content

