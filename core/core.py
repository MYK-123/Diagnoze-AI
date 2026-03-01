#!/bin/env python3

import torch
import numpy as np
import heapq
from transformers import T5Tokenizer, T5ForConditionalGeneration
from typing import List, Tuple
from auth.users import User
from content.educational_content import EducationContent, get_all_education_content_cache
from core.disease import Disease, Diseases, get_all_diseases_cache
from core.disease_symptoms_relation import get_relations_cache
from core.predictions import add_new_prediction
from core.symptoms import Symptom, Symptoms, get_all_symptoms_cache
from core.symptoms_input import SymptomInputs, add_new_symptom_input


def predict_internal(include_symptoms: Symptoms|list[Symptom]|None, exclude_symptoms: Symptoms|list[Symptom]|None = None)-> List[Tuple[Disease, float]]:

    if not include_symptoms:
        return []

    # Get Diseases
    diseases = get_all_diseases_cache()

    # Get Conditional Probablities
    cond = get_relations_cache()
    
    # Uniform Prior
    prior = 1 / len(diseases)

    results: List[Tuple[Disease, float]] = []
    for disease in diseases:
        log_prob: float = np.log(prior)
        for symptom in include_symptoms:
            p = cond.get_strengths_by_disease_id_and_symptom_id(disease.get_disease_id(), symptom.get_id(), 0.001)
            p = np.clip(p, 0.001, 0.999)
            log_prob += np.log(p)
        if exclude_symptoms:
            for symptom in exclude_symptoms:
                p = cond.get_strengths_by_disease_id_and_symptom_id(disease.get_disease_id(), symptom.get_id(), 0.001)
                p = np.clip(p, 0.001, 0.999)
                log_prob -= np.log(p)
        results.append((disease, np.exp(log_prob)))
    
    total = sum(x[1] for x in results)
    normalized = [(name, prob / total) for name, prob in results]

    return sorted(normalized, key=lambda x: x[1], reverse=True)

def get_symptom_list_from_disease(disease: Disease|None)->list[Symptom]:
    if not disease:
        return []
    
    disease_id = disease.get_disease_id()
    relations = get_relations_cache().get_all_relation_list()
    related_symptom_ids = {rel.get_symptom_id() for rel in relations if rel.get_disease_id() == disease_id}
    
    return [s for s in get_all_symptoms_cache().get_all_list() if s.get_id() in related_symptom_ids]

def get_top_k_diseases_from_diseases_list(diseases: list[Disease]|None, k: int) -> list[Disease]:
    """
    Return the top K diseases ranked by severity level.
    
    Severity ranking: high > medium > low.
    """
    
    if diseases is None or len(diseases) == 0 or k <= 0:
        return []
    
    return heapq.nlargest(k, diseases, key=lambda d: d.get_severity_level())

def get_top_k_diseases_from_prediction_with_probablities(include_symptoms: Symptoms|list[Symptom]|None, exclude_symptoms: Symptoms|list[Symptom]|None = None, top_k: int = 3) -> List[Tuple[Disease, float]]:
    return predict_internal(include_symptoms, exclude_symptoms)[:top_k]

def get_education_content_for_disease(disease : Disease|None = None) -> EducationContent|None:
    """	
    Given a Disease objects,
    return a list EducationContent objects
    """
    if not disease:
        return None
    for content in get_all_education_content_cache():
        if content.get_disease_id() == disease.get_disease_id():
            return content
    return None

def get_education_content_for_diseases(diseases : Diseases | list[Disease] | None) -> list[EducationContent]:
    """	
    Given a Diseases object or a list of Disease objects,
    return a list of EducationContent objects
    """
    if diseases is None or len(diseases) < 1:
        return []
    disease_ids = {d.get_disease_id() for d in diseases}
    return [content for content in get_all_education_content_cache() if content.get_disease_id() in disease_ids]

def predict(input_id: int, symptoms: Symptoms, top_n: int=3)-> List[Disease]:
    results: List[Disease] = []
    for disease, score in get_top_k_diseases_from_prediction_with_probablities(symptoms, top_k=top_n):
        add_new_prediction(input_id, disease.get_disease_id(), score)
        results.append(disease)
    return results


def get_symptoms_string_from_symptom_list(symptoms_list: list[Symptom]|None) -> str:
    if not symptoms_list:
        return ""
    return ", ".join([symptom.get_name() for symptom in symptoms_list])

def get_symptom_list_from_symptom_string(symptom_string: str|None) -> list[Symptom]:
    if not symptom_string:
        return []
    return [symptom for symptom in get_all_symptoms_cache().get_all_list() if symptom.get_name().lower() in symptom_string.lower()]


def build_prompt(chat_text, symptom_list):
    chat_text = chat_text or ""
    symptom_list = symptom_list or []
    symptom_str = ",".join(symptom_list) if symptom_list else ""
    
    return (
        "Task: Extract patient symptoms.\n"
        "Rules:\n"
        "- Use ONLY symptoms from provided list\n"
        "- Output a comma-seperated list\n"
        "- Do not add explanations\n\n"
        f"Symptom List: {symptom_str}\n\n"
        f"Patient chat: {chat_text}\n\n"
        "Symptoms:"
    )

def extracted_symptoms(chat_text, SYMPTOM_LIST):
    MODEL_NAME = "t5-base"
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.eval()

    prompt = build_prompt
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=64,
            num_beams=4,
            temperature=0.0,
            early_stopping=True
        )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    symptoms = [
        s.strip().lower()
        for s in decoded.split(",") if s.strip().lower() in SYMPTOM_LIST
    ]
    return sorted(set(symptoms))

# TODO: Later using T5-base or T5-small or FLAN-T5, and train via nltk or spacy
# TODO: Text input to List of Symptoms or List of include and exclude Symptom

def symptom_list_from_input(from_input :str, user: User) -> SymptomInputs:
    # use NLP to identify list of symptoms from from_input
    # also save the query in database
    add_new_symptom_input(user.user_id, from_input)

    

    return SymptomInputs()
