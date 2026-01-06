#!/bin/env python3

from db import __core_db__ as coredb

# -------------------------
# Prediction Entity
# -------------------------
class Prediction:
    def __init__(self, prediction_id: int, input_id: int, disease_id: int, confidence_score: float):
        self.__prediction_id = prediction_id
        self.__input_id = input_id
        self.__disease_id = disease_id
        self.__confidence_score = confidence_score

    # --- Getters ---
    def get_prediction_id(self) -> int:
        return self.__prediction_id

    def get_input_id(self) -> int:
        return self.__input_id

    def get_disease_id(self) -> int:
        return self.__disease_id

    def get_confidence_score(self) -> float:
        return self.__confidence_score

    # --- In-place update ---
    def update(self, input_id: int, disease_id: int, confidence_score: float):
        self.__input_id = input_id
        self.__disease_id = disease_id
        self.__confidence_score = confidence_score

    # --- Equality & hashing by ID ---
    def __eq__(self, other):
        if not isinstance(other, Prediction):
            return False
        return self.__prediction_id == other.__prediction_id

    def __hash__(self):
        return hash(self.__prediction_id)


# -------------------------
# Collection of Predictions
# -------------------------
class Predictions:
    def __init__(self):
        self.__contents: list[Prediction] = []

    # --- Access all ---
    def get_all_list(self) -> list[Prediction]:
        return self.__contents.copy()

    # --- Add new ---
    def add(self, pred: Prediction):
        if pred is not None and pred not in self.__contents:
            self.__contents.append(pred)

    # --- Filters ---
    def filter_by_prediction_id(self, prediction_id: int) -> 'Predictions':
        results = Predictions()
        for p in self.__contents:
            if p.get_prediction_id() == prediction_id:
                results.add(p)
        return results

    def filter_by_input_id(self, input_id: int) -> 'Predictions':
        results = Predictions()
        for p in self.__contents:
            if p.get_input_id() == input_id:
                results.add(p)
        return results

    def filter_by_disease_id(self, disease_id: int) -> 'Predictions':
        results = Predictions()
        for p in self.__contents:
            if p.get_disease_id() == disease_id:
                results.add(p)
        return results

    def filter_by_confidence_score(self, score: float) -> 'Predictions':
        results = Predictions()
        for p in self.__contents:
            if p.get_confidence_score() == score:
                results.add(p)
        return results

    # --- Threshold Filters ---
    def filter_by_confidence_min(self, min_score: float) -> 'Predictions':
        results = Predictions()
        for p in self.__contents:
            if p.get_confidence_score() >= min_score:
                results.add(p)
        return results

    def filter_by_confidence_max(self, max_score: float) -> 'Predictions':
        results = Predictions()
        for p in self.__contents:
            if p.get_confidence_score() <= max_score:
                results.add(p)
        return results

    def filter_by_confidence_range(self, min_score: float, max_score: float) -> 'Predictions':
        results = Predictions()
        for p in self.__contents:
            if min_score <= p.get_confidence_score() <= max_score:
                results.add(p)
        return results


# -------------------------
# Global Cache
# -------------------------
cache_all_predictions: Predictions | None = None


# -------------------------
# Load all predictions from DB
# -------------------------
def load_all_predictions() -> Predictions:
    predictions = Predictions()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT prediction_id, input_id, disease_id, confidance_score FROM predictions;")
        rows = cursor.fetchall()
        for row in rows:
            pred = Prediction(row[0], row[1], row[2], row[3])
            predictions.add(pred)
    except Exception as e:
        print(f"Error retrieving predictions: {e}")
    finally:
        conn.close()
    return predictions


# -------------------------
# Add new prediction
# -------------------------
def add_new_prediction(input_id: int, disease_id: int, confidence_score: float) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (input_id, disease_id, confidance_score) VALUES (?, ?, ?);",
            (input_id, disease_id, confidence_score)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_predictions
        if cache_all_predictions is not None and cursor.lastrowid is not None:
            new_pred = Prediction(cursor.lastrowid, input_id, disease_id, confidence_score)
            cache_all_predictions.add(new_pred)
        else:
            cache_all_predictions = load_all_predictions()

        return True
    except Exception as e:
        print(f"Error creating prediction: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Update existing prediction
# -------------------------
def set_prediction_data(prediction_id: int, input_id: int, disease_id: int, confidence_score: float) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE predictions SET input_id=?, disease_id=?, confidance_score=? WHERE prediction_id=?;",
            (input_id, disease_id, confidence_score, prediction_id)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_predictions
        if cache_all_predictions is not None:
            for p in cache_all_predictions.get_all_list():
                if p.get_prediction_id() == prediction_id:
                    p.update(input_id, disease_id, confidence_score)
                    break

        return True
    except Exception as e:
        print(f"Error updating prediction: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Get cache (refresh optional)
# -------------------------
def get_all_predictions_cache(refresh_cache: bool = False) -> Predictions:
    global cache_all_predictions
    if cache_all_predictions is None or refresh_cache:
        cache_all_predictions = load_all_predictions()
    return cache_all_predictions
