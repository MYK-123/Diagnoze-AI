#!/bin/env python3

from db import core as coredb

# -------------------------
# Symptom Entity
# -------------------------
class Symptom:
    def __init__(self, symptom_id: int, symptom_name: str, category: str):
        self.__symptom_id = symptom_id
        self.__symptom_name = symptom_name
        self.__category = category

    # --- Getters ---
    def get_id(self) -> int:
        return self.__symptom_id

    def get_name(self) -> str:
        return self.__symptom_name

    def get_category(self) -> str:
        return self.__category

    # --- In-place update ---
    def update(self, symptom_name: str, category: str):
        self.__symptom_name = symptom_name
        self.__category = category

    # --- Equality & hashing by ID ---
    def __eq__(self, other):
        if not isinstance(other, Symptom):
            return False
        return self.__symptom_id == other.__symptom_id

    def __hash__(self):
        return hash(self.__symptom_id)


# -------------------------
# Collection of Symptoms
# -------------------------
class Symptoms:
    def __init__(self):
        self.__contents: list[Symptom] = []

    # --- Access all ---
    def get_all_list(self) -> list[Symptom]:
        return self.__contents.copy()

    # --- Add new ---
    def add(self, symptom: Symptom):
        if symptom is not None and symptom not in self.__contents:
            self.__contents.append(symptom)

    # --- Filters ---
    def filter_by_id(self, symptom_id: int) -> 'Symptoms':
        results = Symptoms()
        for s in self.__contents:
            if s.get_id() == symptom_id:
                results.add(s)
        return results

    def filter_by_name(self, name: str) -> 'Symptoms':
        results = Symptoms()
        for s in self.__contents:
            if name.lower() in s.get_name().lower():
                results.add(s)
        return results

    def filter_by_category(self, category: str) -> 'Symptoms':
        results = Symptoms()
        for s in self.__contents:
            if category.lower() == s.get_category().lower():
                results.add(s)
        return results


# -------------------------
# Global Cache
# -------------------------
cache_all_symptoms: Symptoms | None = None


# -------------------------
# Load all symptoms from DB
# -------------------------
def load_all_symptoms() -> Symptoms:
    symptoms_list = Symptoms()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT symptom_id, symptom_name, category FROM symptoms;")
        rows = cursor.fetchall()
        for row in rows:
            symptom = Symptom(row[0], row[1], row[2])
            symptoms_list.add(symptom)
    except Exception as e:
        print(f"Error retrieving symptoms: {e}")
    finally:
        conn.close()
    return symptoms_list


# -------------------------
# Add new symptom
# -------------------------
def add_new_symptom(symptom_name: str, category: str) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO symptoms (symptom_name, category) VALUES (?, ?);",
            (symptom_name, category)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_symptoms
        if cache_all_symptoms is not None and cursor.lastrowid is not None:
            new_symptom = Symptom(cursor.lastrowid, symptom_name, category)
            cache_all_symptoms.add(new_symptom)
        else:
            cache_all_symptoms = load_all_symptoms()

        return True
    except Exception as e:
        print(f"Error creating symptom: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Update existing symptom
# -------------------------
def set_symptom_data(symptom_id: int, symptom_name: str, category: str) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE symptoms SET symptom_name=?, category=? WHERE symptom_id=?;",
            (symptom_name, category, symptom_id)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_symptoms
        if cache_all_symptoms is not None:
            for s in cache_all_symptoms.get_all_list():
                if s.get_id() == symptom_id:
                    s.update(symptom_name, category)
                    break

        return True
    except Exception as e:
        print(f"Error updating symptom: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Get cache (refresh optional)
# -------------------------
def get_all_symptoms_cache(refresh_cache: bool = False) -> Symptoms:
    global cache_all_symptoms
    if cache_all_symptoms is None or refresh_cache:
        cache_all_symptoms = load_all_symptoms()
    return cache_all_symptoms
