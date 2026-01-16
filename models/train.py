#!/bin/env python3

from models import get_model_and_toeknizer, save_trained_model

def build_training_prompt(symptom_list:list, chat_text:str) -> str:
    return (
        "Task: Extract patient symptoms.\n"
        "Rules:\n"
        "- Use ONLY symptoms from provided list\n"
        "- Output a comma-seperated list\n"
        "- Do not add explanations\n\n"
        f"Symptom List: {','.join(symptom_list)}\n\n"
        f"Patient chat: {chat_text}\n\n"
        "Symptoms:"
    )

def get_training_data(input_data:str, output_data:str)->dict[str,str]:
    return {
        "input":input_data,
        "target":output_data
    }

