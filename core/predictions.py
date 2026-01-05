#!/bin/env python3

from db import __core_db__ as coredb

class Prediction:

    def __init__(self, prediction_id, input_id, disease_id, confidance_score):
        self.__prediction_id = prediction_id
        self.__input_id = input_id
        self.__disease_id = disease_id
        self.__confidance_score = confidance_score
    
    def get_input_id(self):
        return self.__input_id
    
    def get_prediction_id(self):
        return self.__prediction_id
    
    def get_disease_id(self):
        return self.__disease_id
    
    def get_confidance_score(self):
        return self.__confidance_score

class Predictions:

    def __init__(self):
        self.__pred: list[Prediction] = []
    
    def add(self, prediction: Prediction):
        if prediction is not None and  prediction not in self.__pred:
            self.__pred.append(prediction)
    
    def get_predictions_by_id(self, id):
        l = Predictions()
        for i in self.__pred:
            if id == i.get_prediction_id():
                l.add(i)
        return l
    
    def get_predictions_by_input_id(self, id):
        l = Predictions()
        for i in self.__pred:
            if id == i.get_input_id():
                l.add(i)
        return l
    
    def get_predictions_by_disease_id(self, id):
        l = Predictions()
        for i in self.__pred:
            if id == i.get_disease_id():
                l.add(i)
        return l
    
    def get_predictions_by_confidance_score(self, score):
        l = Predictions()
        for i in self.__pred:
            if score == i.get_confidance_score():
                l.add(i)
        return l
    
    def get_predictions_list(self):
        return self.__pred


cache_all_predictions : Predictions | None = None

def get_predictions_by_id(pred_id: int) -> Predictions:
    if cache_all_predictions is None:
        get_all_predictions()
    return cache_all_predictions.get_predictions_by_id(pred_id)

def get_predictions_by_input_id(input_id: int) -> Predictions:
    if cache_all_predictions is None:
        get_all_predictions()
    return cache_all_predictions.get_predictions_by_input_id(input_id)

def get_predictions_by_disease_id(disease_id: int) -> Predictions:
    if cache_all_predictions is None:
        get_all_predictions()
    return cache_all_predictions.get_predictions_by_disease_id(disease_id)

def get_predictions_by_confidance_score(score) -> Predictions:
    if cache_all_predictions is None:
        get_all_predictions()
    return cache_all_predictions.get_predictions_by_confidance_score(score)


def get_all_predictions() -> Predictions:
    predictions = Predictions()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT prediction_id, input_id, disease_id, confidance_score FROM predictions;")
        dat = cursor.fetchall()
        if dat:
            for dataOne in dat:
                if dataOne:
                    pred = Prediction(dataOne[0], dataOne[1], dataOne[2], dataOne[3])
                    predictions.add(symptom=pred)
    except Exception as e:
        print(f"Error retrieving all prediction from predictions table: {e}")
    conn.close()
    global cache_all_predictions
    cache_all_predictions = predictions
    return predictions

def add_new_prediction(input_id, disease_id, confidance_score) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (input_id, disease_id, confidance_score) VALUES (?, ?, ?)",
            (input_id, disease_id, confidance_score)
            )
        conn.commit()
        conn.close()
        get_all_predictions()
        return True
    except Exception as e:
        print(f"Error creating prediction: {e}")
        conn.rollback()
        conn.close()
        return False

def get_all_predictions_cache(refresh_cache:bool = False)-> Predictions:
    global cache_all_predictions
    if cache_all_predictions is None or cache_all_predictions == [] or refresh_cache:
        get_all_predictions()
    return cache_all_predictions

