#!/bin/env python3

import os
from transformers import AutoTokenizer, T5ForConditionalGeneration, T5Tokenizer

MODEL_NAME = "t5-base"
SAVE_DIR = "./models/"
OUTPUT_DIR = SAVE_DIR + MODEL_NAME

def download_model(model_name:str = MODEL_NAME):
    toknizer:T5Tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    toknizer.save_pretrained(SAVE_DIR + model_name)
    model.save_pretrained(SAVE_DIR + model_name)

def download_model_if_needed(model_name:str = MODEL_NAME):
    if not os.path.exists(model_name):
        download_model(model_name)

def get_model_and_toeknizer(model_name:str = MODEL_NAME)-> tuple[T5ForConditionalGeneration, T5Tokenizer]:
    download_model_if_needed()
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    return model, tokenizer

def save_trained_model(output_dir:str = OUTPUT_DIR, model: T5ForConditionalGeneration|None = None, tokenizer: T5Tokenizer|None = None):
    if tokenizer:
        tokenizer.save_pretrained(output_dir)
    if model:
        model.save_pretrained(output_dir)

