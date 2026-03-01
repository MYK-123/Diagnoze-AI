#!/bin/env python3

from db import core as coredb

# -------------------------
# Disease Severity Mapping
# -------------------------
DISEASE_SEVERITY_RANK = {
    'low': 1,
    'medium': 2,
    'high': 3
}


# -------------------------
# Disease Entity
# -------------------------
class Disease:
    def __init__(self, disease_id: int, disease_name: str, category: str, severity_level: str):
        self.__disease_id = disease_id
        self.__disease_name = disease_name
        self.__category = category
        self.__severity_level = DISEASE_SEVERITY_RANK.get(severity_level, 0)

    # --- Getters ---
    def get_disease_id(self) -> int:
        return self.__disease_id

    def get_disease_name(self) -> str:
        return self.__disease_name

    def get_category(self) -> str:
        return self.__category

    def get_severity_level(self) -> int:
        return self.__severity_level
    
    def get_severity_level_str(self) -> str:
        for k, v in DISEASE_SEVERITY_RANK.items():
            if v == self.__severity_level:
                return k
        return ""
    

    # --- In-place update ---
    def update(self, disease_name: str, category: str, severity_level: str):
        self.__disease_name = disease_name
        self.__category = category
        self.__severity_level = DISEASE_SEVERITY_RANK.get(severity_level, 0)

    # --- Equality & hashing by ID ---
    def __eq__(self, other):
        if not isinstance(other, Disease):
            return False
        return self.__disease_id == other.__disease_id

    def __hash__(self):
        return hash(self.__disease_id)


# -------------------------
# Collection of Diseases
# -------------------------
class Diseases:
    def __init__(self):
        self.__contents: list[Disease] = []
    
    def __iter__(self):
        return iter(self.__contents)
    
    def __len__(self):
        return len(self.__contents)

    # --- Access all ---
    def get_all_diseases_list(self) -> list[Disease]:
        return self.__contents.copy()

    # --- Add new ---
    def add(self, disease: Disease):
        if disease is not None and disease not in self.__contents:
            self.__contents.append(disease)

    # --- Filters ---
    def filter_by_id(self, disease_id: int) -> 'Diseases':
        results = Diseases()
        for disease in self.__contents:
            if disease.get_disease_id() == disease_id:
                results.add(disease)
        return results

    def filter_by_name(self, disease_name: str) -> 'Diseases':
        results = Diseases()
        for disease in self.__contents:
            if disease_name.lower() in disease.get_disease_name().lower():
                results.add(disease)
        return results

    def filter_by_category(self, category: str) -> 'Diseases':
        results = Diseases()
        for disease in self.__contents:
            if category == disease.get_category():
                results.add(disease)
        return results

    def filter_by_severity_level(self, severity_level: str) -> 'Diseases':
        results = Diseases()
        rank = DISEASE_SEVERITY_RANK.get(severity_level, 0)
        for disease in self.__contents:
            if disease.get_severity_level() == rank:
                results.add(disease)
        return results


# -------------------------
# Global Cache
# -------------------------
cache_all_diseases: Diseases | None = None


# -------------------------
# Load all diseases from DB
# -------------------------
def load_all_diseases() -> Diseases:
    content_list = Diseases()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT disease_id, disease_name, category, severity_level FROM disease;")
        rows = cursor.fetchall()
        for row in rows:
            disease = Disease(row[0], row[1], row[2], row[3])
            content_list.add(disease)
    except Exception as e:
        print(f"Error retrieving diseases: {e}")
    finally:
        conn.close()

    return content_list


def get_severity_level_str(sever: int) -> str:
        for k, v in DISEASE_SEVERITY_RANK.items():
            if v == sever:
                return k
        return ""

# -------------------------
# Add new disease
# -------------------------
def add_new_disease(disease_name: str, category: str, severity_level: int | str) -> tuple[bool, int]:
    conn = coredb.getDBObject()
    
    severity_level_str = get_severity_level_str(severity_level) if isinstance(severity_level, int) else severity_level
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO disease (disease_name, category, severity_level) VALUES (?, ?, ?);",
            (disease_name, category, severity_level_str)
        )
        conn.commit()
        
        # Incremental cache update
        global cache_all_diseases
        if cache_all_diseases is not None and cursor.lastrowid is not None:
            new_disease = Disease(cursor.lastrowid, disease_name, category, severity_level_str)
            cache_all_diseases.add(new_disease)
        else:
            cache_all_diseases = load_all_diseases()

        return True, cursor.lastrowid if cursor.lastrowid is not None else -1
    except Exception as e:
        print(f"Error creating disease: {e}")
        conn.rollback()
        return False, -1
    finally:
        conn.close()


# -------------------------
# Update existing disease
# -------------------------
def set_disease_data(disease_id: int, disease_name: str, category: str, severity_level: str) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE disease SET disease_name=?, category=?, severity_level=? WHERE disease_id=?;",
            (disease_name, category, severity_level, disease_id)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_diseases
        if cache_all_diseases is not None:
            for disease in cache_all_diseases.get_all_diseases_list():
                if disease.get_disease_id() == disease_id:
                    disease.update(disease_name, category, severity_level)
                    break

        return True
    except Exception as e:
        print(f"Error updating disease: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Get cache (refresh optional)
# -------------------------
def get_all_diseases_cache(refresh_cache: bool = False) -> Diseases:
    global cache_all_diseases
    if cache_all_diseases is None or refresh_cache:
        cache_all_diseases = load_all_diseases()
    return cache_all_diseases
