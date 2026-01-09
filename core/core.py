#!/bin/env python3

import heapq
from auth.users import User
from content.educational_content import EducationContent, get_all_education_content_cache
from core.disease import Disease, Diseases, get_all_diseases_cache
from core.disease_symptoms_relation import get_relations_cache
from core.symptoms import Symptom, Symptoms, get_all_symptoms_cache
from core.symptoms_input import SymptomInputs, add_new_symptom_input


def get_symptom_list_from_disease(disease: Disease)->list[Symptom]:
    if not disease:
        return []
    return [s for rel in get_relations_cache().get_all_relation_list() for s in get_all_symptoms_cache().get_all_list() if s.get_id() == rel.get_symptom_id()]

def get_disease_list_from_symptom_list(symptom_list: Symptoms|list[Symptom]|None) -> list[Disease]:
    """
    Return the List of Disease by using List of Symptom

    Note: If symptom_list in empty returns []
    """
    if not symptom_list:
        return []
    relationships_all = get_relations_cache().get_all_relation_list()
    diseases_all = get_all_diseases_cache().get_all_diseases_list()
    disease_out = set()
    for symptom in symptom_list.get_all_list() if isinstance(symptom_list, Symptoms) else symptom_list:
        relationship_symp = [rel for rel in relationships_all if rel.get_symptom_id() == symptom.get_id()]
        for rel in relationship_symp:
            disease_find = {dis for dis in diseases_all if rel.get_disease_id() == dis.get_disease_id()}
            disease_out.union(disease_find)
    return list(disease_out)

def get_disease_list_from_symptom_list_incude_exclude(include_list: Symptoms|list[Symptom]|None, exclude_list: Symptoms|list[Symptom]|None) -> list[Disease]:
    """
    Return the List of Disease by using List of include Symptom and exclude Symptom
    
    Note: If include_list in empty returns []
    """
    A = get_disease_list_from_symptom_list(include_list)
    if not A:
        return []
    B = get_disease_list_from_symptom_list(include_list)
    return A if not B else list(set(A) - set(B))

def get_top_bottom_k_diseases_from_diseases_list(diseases: list[Disease], k: int) -> tuple[list[Disease], list[Disease]]:
    """
    Return the top and bottom K diseases ranked by severity level.
    
    Severity ranking: high > medium > low.
    """
    top_k = get_top_k_diseases_from_diseases_list(diseases, k)
    bottom_k = get_bottom_k_diseases_from_diseases_list(diseases, k)
    return top_k, bottom_k



def get_top_k_diseases_from_diseases_list(diseases: list[Disease], k: int) -> list[Disease]:
    """
    Return the top K diseases ranked by severity level.
    
    Severity ranking: high > medium > low.
    """
    
    if not diseases or k <= 0:
        return []
    
    return heapq.nlargest(k, diseases, key=lambda d: d.get_severity_level())

def get_bottom_k_diseases_from_diseases_list(diseases: list[Disease], k: int) -> list[Disease]:
    """
    Return the bottom K diseases ranked by severity level.
    
    Severity ranking: high > medium > low.
    """
    
    if not diseases or k <= 0:
        return []
    
    return heapq.nsmallest(k, diseases, key=lambda d: d.get_severity_level())

def get_education_content_for_disease(disease : Disease|None = None) -> EducationContent|None:
    """	
    Given a Disease objects,
    return a list EducationContent objects
    """
    if not disease:
        return None
    for content in get_all_education_content_cache().get_all_list():
        if content.get_disease_id() == disease.get_disease_id():
            return content
    return None

def get_education_content_for_diseases(diseases : Diseases | list[Disease]) -> list[EducationContent]:
    """	
    Given a Diseases object or a list of Disease objects,
    return a list of EducationContent objects
    """
    all_content : list[EducationContent] = get_all_education_content_cache().get_all_list()
    diseases_list :list[Disease] = diseases.get_all_diseases_list() if isinstance(diseases, Diseases) else diseases
    if not diseases_list:
        return []
    disease_ids = {d.get_disease_id() for d in diseases_list}
    return [content for content in all_content if content.get_disease_id() in disease_ids]

def get_disease_from_symptom_top_bottom_k(symptoms: list[Symptom], exclude_symptoms: list[Symptom]|None=None, k: int=3)->tuple[list[Disease], list[Disease]]:
    d = get_disease_list_from_symptom_list_incude_exclude(symptoms, exclude_symptoms)
    top_k, bottom_k = get_top_bottom_k_diseases_from_diseases_list(d, k)
    return top_k, bottom_k

def get_disease_from_symptom_top_k(symptoms: list[Symptom], exclude_symptoms: list[Symptom]|None=None, k: int=3)->list[Disease]:
    d = get_disease_list_from_symptom_list_incude_exclude(symptoms, exclude_symptoms)
    top_k = get_top_k_diseases_from_diseases_list(d, k)
    return top_k

def get_disease_from_symptom_bottem_k(symptoms: list[Symptom], exclude_symptoms: list[Symptom]|None=None, k: int=3)->list[Disease]:
    d = get_disease_list_from_symptom_list_incude_exclude(symptoms, exclude_symptoms)
    bottom_k = get_bottom_k_diseases_from_diseases_list(d, k)
    return bottom_k


# TODO: Later using T5-base or T5-small or FLAN-T5, and train via nltk or spacy
# TODO: Text input to List of Symptoms or List of include and exclude Symptom

def symptom_list_from_input(from_input :str, user: User) -> SymptomInputs:
    # use NLP to identify list of symptoms from from_input

    # also save the query in database
    add_new_symptom_input(user.user_id, from_input)

    
    return SymptomInputs()
