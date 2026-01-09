#!/bin/env python3


import json

from core.core import get_education_content_for_disease, get_symptom_list_from_disease
from core.disease import Disease

class DiseaseInfo:

    def __init__(self):
        self.disease_name = ""
        self.disease_category = ""
        self.disease_severity = 0
        self.symptoms = set()
        self.education_content = {}
        self.education_content['title'] = ""
        self.education_content['content'] = ""
        self.education_content['verified'] = ""
    
    def set_disease_name(self, name):
        self.disease_name = name
    
    def set_disease_catrgory(self, cat):
        self.disease_name = cat
    
    def set_disease_severity(self, sev):
        self.disease_name = sev
    
    def add_symptom(self, symp:str):
        self.symptoms.add(symp)
    
    def set_education_content(self, title, content, is_verified):
        self.education_content['title'] = title
        self.education_content['content'] = content
        self.education_content['verified'] = is_verified


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

