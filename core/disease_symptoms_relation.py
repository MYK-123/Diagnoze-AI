#!/bin/env python3

from db import __core_db__ as coredb

# -------------------------
# Disease-Symptom Relation
# -------------------------
class DiseaseSymptomRelation:
    def __init__(self, relation_id: int, disease_id: int, symptom_id: int, strength: float):
        self.__relation_id = relation_id
        self.__disease_id = disease_id
        self.__symptom_id = symptom_id
        self.__strength = strength

    # --- Getters ---
    def get_relation_id(self) -> int:
        return self.__relation_id

    def get_disease_id(self) -> int:
        return self.__disease_id

    def get_symptom_id(self) -> int:
        return self.__symptom_id

    def get_strength(self) -> float:
        return self.__strength

    # --- In-place update ---
    def update(self, disease_id: int, symptom_id: int, strength: float):
        self.__disease_id = disease_id
        self.__symptom_id = symptom_id
        self.__strength = strength

    # --- Equality & hashing by ID ---
    def __eq__(self, other):
        if not isinstance(other, DiseaseSymptomRelation):
            return False
        return self.__relation_id == other.__relation_id

    def __hash__(self):
        return hash(self.__relation_id)


# -------------------------
# Collection of Relations
# -------------------------
class DiseaseSymptomRelations:
    def __init__(self):
        self.__contents: list[DiseaseSymptomRelation] = []

    # --- Access all ---
    def get_all_relation_list(self) -> list[DiseaseSymptomRelation]:
        return self.__contents.copy()

    # --- Add new ---
    def add(self, content: DiseaseSymptomRelation):
        if content is not None and content not in self.__contents:
            self.__contents.append(content)

    # --- Filters ---
    def filter_by_symptom_id(self, symptom_id: int) -> 'DiseaseSymptomRelations':
        results = DiseaseSymptomRelations()
        for rel in self.__contents:
            if rel.get_symptom_id() == symptom_id:
                results.add(rel)
        return results

    def filter_by_disease_id(self, disease_id: int) -> 'DiseaseSymptomRelations':
        results = DiseaseSymptomRelations()
        for rel in self.__contents:
            if rel.get_disease_id() == disease_id:
                results.add(rel)
        return results

    def filter_by_strength(self, strength: float) -> 'DiseaseSymptomRelations':
        results = DiseaseSymptomRelations()
        for rel in self.__contents:
            if rel.get_strength() == strength:
                results.add(rel)
        return results


# -------------------------
# Global Cache
# -------------------------
cache_all_diseases_symptom_relation: DiseaseSymptomRelations | None = None


# -------------------------
# Load all relations from DB (pure function)
# -------------------------
def load_all_relations() -> DiseaseSymptomRelations:
    content_list = DiseaseSymptomRelations()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, disease_id, symptom_id, strength FROM disease_symptoms;")
        rows = cursor.fetchall()
        for row in rows:
            relation = DiseaseSymptomRelation(row[0], row[1], row[2], row[3])
            content_list.add(relation)
    except Exception as e:
        print(f"Error retrieving disease-symptom relations: {e}")
    finally:
        conn.close()
    return content_list


# -------------------------
# Add new relation
# -------------------------
def add_new_diseases_symptom_relation(disease_id: int, symptom_id: int, strength: float) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO disease_symptoms (disease_id, symptom_id, strength) VALUES (?, ?, ?)",
            (disease_id, symptom_id, strength)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_diseases_symptom_relation
        if cache_all_diseases_symptom_relation is not None and cursor.lastrowid is not None:
            new_relation = DiseaseSymptomRelation(cursor.lastrowid, disease_id, symptom_id, strength)
            cache_all_diseases_symptom_relation.add(new_relation)
        else:
            # Full reload if cache not initialized
            cache_all_diseases_symptom_relation = load_all_relations()

        return True
    except Exception as e:
        print(f"Error creating disease-symptom relation: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Update existing relation
# -------------------------
def set_diseases_symptom_relation_data(relation_id: int, disease_id: int, symptom_id: int, strength: float) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE disease_symptoms SET disease_id=?, symptom_id=?, strength=? WHERE id=?",
            (disease_id, symptom_id, strength, relation_id)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_diseases_symptom_relation
        if cache_all_diseases_symptom_relation is not None:
            for rel in cache_all_diseases_symptom_relation.get_all_relation_list():
                if rel.get_relation_id() == relation_id:
                    rel.update(disease_id, symptom_id, strength)
                    break

        return True
    except Exception as e:
        print(f"Error updating disease-symptom relation: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Get cache (refresh optional)
# -------------------------
def get_relations_cache(refresh_cache: bool = False) -> DiseaseSymptomRelations:
    global cache_all_diseases_symptom_relation
    if cache_all_diseases_symptom_relation is None or refresh_cache:
        cache_all_diseases_symptom_relation = load_all_relations()
    return cache_all_diseases_symptom_relation
