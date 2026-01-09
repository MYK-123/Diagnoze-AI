#!/bin/env python3

from db import core as coredb

# -------------------------
# Symptom Extracted Entity
# -------------------------
class SymptomExtracted:
    def __init__(self, extracted_id: int, input_id: int, symptom_id: int, confidence_score: float):
        self.__extracted_id = extracted_id
        self.__input_id = input_id
        self.__symptom_id = symptom_id
        self.__confidence_score = confidence_score

    # --- Getters ---
    def get_extracted_id(self) -> int:
        return self.__extracted_id

    def get_input_id(self) -> int:
        return self.__input_id

    def get_symptom_id(self) -> int:
        return self.__symptom_id

    def get_confidence_score(self) -> float:
        return self.__confidence_score

    # --- In-place update ---
    def update(self, input_id: int, symptom_id: int, confidence_score: float):
        self.__input_id = input_id
        self.__symptom_id = symptom_id
        self.__confidence_score = confidence_score

    # --- Equality & hashing by ID ---
    def __eq__(self, other):
        if not isinstance(other, SymptomExtracted):
            return False
        return self.__extracted_id == other.__extracted_id

    def __hash__(self):
        return hash(self.__extracted_id)


# -------------------------
# Collection of Symptom Extracted
# -------------------------
class SymptomExtracteds:
    def __init__(self):
        self.__contents: list[SymptomExtracted] = []

    # --- Access all ---
    def get_all_list(self) -> list[SymptomExtracted]:
        return self.__contents.copy()

    # --- Add new ---
    def add(self, symptom: SymptomExtracted):
        if symptom is not None and symptom not in self.__contents:
            self.__contents.append(symptom)

    # --- Filters ---
    def filter_by_extracted_id(self, extracted_id: int) -> 'SymptomExtracteds':
        results = SymptomExtracteds()
        for s in self.__contents:
            if s.get_extracted_id() == extracted_id:
                results.add(s)
        return results

    def filter_by_input_id(self, input_id: int) -> 'SymptomExtracteds':
        results = SymptomExtracteds()
        for s in self.__contents:
            if s.get_input_id() == input_id:
                results.add(s)
        return results

    def filter_by_symptom_id(self, symptom_id: int) -> 'SymptomExtracteds':
        results = SymptomExtracteds()
        for s in self.__contents:
            if s.get_symptom_id() == symptom_id:
                results.add(s)
        return results

    def filter_by_confidence_score(self, score: float) -> 'SymptomExtracteds':
        results = SymptomExtracteds()
        for s in self.__contents:
            if s.get_confidence_score() == score:
                results.add(s)
        return results

    # --- Threshold Filters ---
    def filter_by_confidence_min(self, min_score: float) -> 'SymptomExtracteds':
        results = SymptomExtracteds()
        for s in self.__contents:
            if s.get_confidence_score() >= min_score:
                results.add(s)
        return results

    def filter_by_confidence_max(self, max_score: float) -> 'SymptomExtracteds':
        results = SymptomExtracteds()
        for s in self.__contents:
            if s.get_confidence_score() <= max_score:
                results.add(s)
        return results

    # --- New: Filter by confidence range ---
    def filter_by_confidence_range(self, min_score: float, max_score: float) -> 'SymptomExtracteds':
        """Return all symptoms with confidence_score in [min_score, max_score]"""
        results = SymptomExtracteds()
        for s in self.__contents:
            if min_score <= s.get_confidence_score() <= max_score:
                results.add(s)
        return results


# -------------------------
# Global Cache
# -------------------------
cache_all_symptom_extracted: SymptomExtracteds | None = None


# -------------------------
# Load all from DB
# -------------------------
def load_all_symptom_extracted() -> SymptomExtracteds:
    symptoms_list = SymptomExtracteds()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT extracted_id, input_id, symptom_id, confidance_score FROM extracted_symptoms;"
        )
        rows = cursor.fetchall()
        for row in rows:
            symptom = SymptomExtracted(row[0], row[1], row[2], row[3])
            symptoms_list.add(symptom)
    except Exception as e:
        print(f"Error retrieving symptom extracts: {e}")
    finally:
        conn.close()
    return symptoms_list


# -------------------------
# Add new symptom extracted
# -------------------------
def add_new_symptom_extracted(input_id: int, symptom_id: int, confidence_score: float) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO extracted_symptoms (input_id, symptom_id, confidance_score) VALUES (?, ?, ?);",
            (input_id, symptom_id, confidence_score)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_symptom_extracted
        if cache_all_symptom_extracted is not None and cursor.lastrowid is not None:
            new_symptom = SymptomExtracted(cursor.lastrowid, input_id, symptom_id, confidence_score)
            cache_all_symptom_extracted.add(new_symptom)
        else:
            cache_all_symptom_extracted = load_all_symptom_extracted()

        return True
    except Exception as e:
        print(f"Error creating symptom extract: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Update existing symptom extracted
# -------------------------
def set_symptom_extracted_data(extracted_id: int, input_id: int, symptom_id: int, confidence_score: float) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE extracted_symptoms SET input_id=?, symptom_id=?, confidance_score=? WHERE extracted_id=?;",
            (input_id, symptom_id, confidence_score, extracted_id)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_symptom_extracted
        if cache_all_symptom_extracted is not None:
            for s in cache_all_symptom_extracted.get_all_list():
                if s.get_extracted_id() == extracted_id:
                    s.update(input_id, symptom_id, confidence_score)
                    break

        return True
    except Exception as e:
        print(f"Error updating symptom extract: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Get cache (refresh optional)
# -------------------------
def get_all_symptom_extracted_cache(refresh_cache: bool = False) -> SymptomExtracteds:
    global cache_all_symptom_extracted
    if cache_all_symptom_extracted is None or refresh_cache:
        cache_all_symptom_extracted = load_all_symptom_extracted()
    return cache_all_symptom_extracted
