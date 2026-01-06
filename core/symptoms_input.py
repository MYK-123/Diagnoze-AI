#!/bin/env python3

from db import __core_db__ as coredb
from datetime import datetime

# -------------------------
# Symptom Input Entity
# -------------------------
class SymptomInput:
    def __init__(self, input_id: int, user_id: str, input_text: str, created_at: str):
        self.__input_id = input_id
        self.__user_id = user_id
        self.__input_text = input_text
        self.__created_at = created_at  # store as string or datetime

    # --- Getters ---
    def get_input_id(self) -> int:
        return self.__input_id

    def get_user_id(self) -> str:
        return self.__user_id

    def get_input_text(self) -> str:
        return self.__input_text

    def get_created_at(self) -> str:
        return self.__created_at

    # --- In-place update ---
    def update(self, user_id: str, input_text: str, created_at: str):
        self.__user_id = user_id
        self.__input_text = input_text
        self.__created_at = created_at

    # --- Equality & hashing by ID ---
    def __eq__(self, other):
        if not isinstance(other, SymptomInput):
            return False
        return self.__input_id == other.__input_id

    def __hash__(self):
        return hash(self.__input_id)


# -------------------------
# Collection of Symptom Inputs
# -------------------------
class SymptomInputs:
    def __init__(self):
        self.__contents: list[SymptomInput] = []

    # --- Access all ---
    def get_all_list(self) -> list[SymptomInput]:
        return self.__contents.copy()

    # --- Add new ---
    def add(self, symptom: SymptomInput):
        if symptom is not None and symptom not in self.__contents:
            self.__contents.append(symptom)

    # --- Filters ---
    def filter_by_input_id(self, input_id: int) -> 'SymptomInputs':
        results = SymptomInputs()
        for s in self.__contents:
            if s.get_input_id() == input_id:
                results.add(s)
        return results

    def filter_by_user_id(self, user_id: str) -> 'SymptomInputs':
        results = SymptomInputs()
        for s in self.__contents:
            if user_id in s.get_user_id():
                results.add(s)
        return results

    def filter_by_created_at(self, created_at: str) -> 'SymptomInputs':
        results = SymptomInputs()
        for s in self.__contents:
            if s.get_created_at() == created_at:
                results.add(s)
        return results


# -------------------------
# Global Cache
# -------------------------
cache_all_symptom_inputs: SymptomInputs | None = None


# -------------------------
# Load all inputs from DB
# -------------------------
def load_all_symptom_inputs() -> SymptomInputs:
    inputs_list = SymptomInputs()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT input_id, user_id, input_text, created_at FROM symptom_inputs;")
        rows = cursor.fetchall()
        for row in rows:
            s_input = SymptomInput(row[0], row[1], row[2], row[3])
            inputs_list.add(s_input)
    except Exception as e:
        print(f"Error retrieving symptom inputs: {e}")
    finally:
        conn.close()
    return inputs_list


# -------------------------
# Add new symptom input
# -------------------------
def add_new_symptom_input(user_id: str, input_text: str) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO symptom_inputs (user_id, input_text) VALUES (?, ?);",
            (user_id, input_text)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_symptom_inputs
        if cache_all_symptom_inputs is not None and cursor.lastrowid is not None:
            new_input = SymptomInput(cursor.lastrowid, user_id, input_text, datetime.now().isoformat())
            cache_all_symptom_inputs.add(new_input)
        else:
            cache_all_symptom_inputs = load_all_symptom_inputs()

        return True
    except Exception as e:
        print(f"Error creating symptom input: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Update existing symptom input
# -------------------------
def set_symptom_input_data(input_id: int, user_id: str, input_text: str, created_at: str) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE symptom_inputs SET user_id=?, input_text=?, created_at=? WHERE input_id=?;",
            (user_id, input_text, created_at, input_id)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_symptom_inputs
        if cache_all_symptom_inputs is not None:
            for s in cache_all_symptom_inputs.get_all_list():
                if s.get_input_id() == input_id:
                    s.update(user_id, input_text, created_at)
                    break

        return True
    except Exception as e:
        print(f"Error updating symptom input: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Get cache (refresh optional)
# -------------------------
def get_all_symptom_inputs_cache(refresh_cache: bool = False) -> SymptomInputs:
    global cache_all_symptom_inputs
    if cache_all_symptom_inputs is None or refresh_cache:
        cache_all_symptom_inputs = load_all_symptom_inputs()
    return cache_all_symptom_inputs
