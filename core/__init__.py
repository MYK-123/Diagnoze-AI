#!/bin/env python3

import json

from content.educational_content import add_new_educational_content
from core.core import get_education_content_for_disease, get_symptom_list_from_disease
from core.disease import Disease, add_new_disease
from core.disease_symptoms_relation import add_new_diseases_symptom_relation
from core.symptoms import add_new_symptom

class DiseaseInfo:

    def __init__(self):
        self.disease_name = ""
        self.disease_category = ""
        self.disease_severity = 0
        self.symptoms:set[str] = set()
        self.education_content:dict[str,str] = {}
        self.education_content['title'] = ""
        self.education_content['content'] = ""
        self.education_content['verified'] = ""
    
    def get_disease_name(self):
        return self.disease_name
    
    def get_disaease_category(self):
        return self.disease_category
    
    def get_disease_severity(self):
        return self.disease_severity
    
    def get_list_of_symptoms(self):
        return list(self.symptoms)
    
    def get_education_content_title(self):
        return self.education_content.get('title', '')
    
    def get_education_content_content(self):
        return self.education_content.get('content', '')
    
    def get_education_content_is_verified(self):
        return self.education_content.get('verified', 'NOT VERIFIED').startswith('V')
    
    def get_education_content(self):
        return self.education_content
    
    def set_disease_name(self, name):
        self.disease_name = name
    
    def set_disease_catrgory(self, cat):
        self.disease_name = cat
    
    def set_disease_severity(self, sev):
        self.disease_name = sev
    
    def add_symptom(self, symp:str):
        self.symptoms.add(symp)
    
    def get_verification_str(self, is_verified:bool):
        return "VERIFIED" if is_verified else "NOT VERIFIED"
    
    def set_education_content(self, title, content, is_verified:str|bool):
        self.education_content['title'] = title
        self.education_content['content'] = content
        verified_str = is_verified if isinstance(is_verified, str) else self.get_verification_str(is_verified)
        self.education_content['verified'] = verified_str


def get_DiseaseInfo_JSON_result(info: DiseaseInfo | list[DiseaseInfo]):
    return json.dumps(info)

def get_DiseaseInfo_from_disease(disease:Disease) -> DiseaseInfo:
    info = DiseaseInfo()
    info.set_disease_name(disease.get_disease_name())
    info.set_disease_catrgory(disease.get_category())
    info.set_disease_severity(disease.get_severity_level_str())
    for s in get_symptom_list_from_disease(disease):
        info.add_symptom(s.get_name())
    content = get_education_content_for_disease(disease)
    if content:
        info.set_education_content(content.get_title(), content.get_content_text(), content.get_is_verified())
    return info

def get_DiseaseInfos_from_diseases(diseases:list[Disease]) -> list[DiseaseInfo]:
    return [get_DiseaseInfo_from_disease(disease) for disease in diseases]

def add_new_disease_info(info: DiseaseInfo) -> bool:
    if not info:
        return False
    status, disease_id = add_new_disease(info.get_disease_name(), info.get_disaease_category(), info.get_disease_severity())
    if not status:
        return False
    for sympt in info.get_list_of_symptoms():
        status, symptom_id = add_new_symptom(sympt)
        if not status:
            return False
        status, relation_id = add_new_diseases_symptom_relation(disease_id, symptom_id)
        if not status:
            return False
    status = add_new_educational_content(disease_id, info.get_education_content_title(), info.get_education_content_content(), info.get_education_content_is_verified())
    if not status:
            return False
    return True

