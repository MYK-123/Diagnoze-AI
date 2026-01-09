#!/bin/env python3

from db import core as coredb

# -------------------------
# EducationContent Entity
# -------------------------
class EducationContent:
    def __init__(self, content_id: int, disease_id: int, title: str, content_text: str, is_verified: bool):
        self.__content_id = content_id
        self.__disease_id = disease_id
        self.__title = title
        self.__content_text = content_text
        self.__is_verified = is_verified

    # --- Getters ---
    def get_content_id(self) -> int:
        return self.__content_id

    def get_disease_id(self) -> int:
        return self.__disease_id

    def get_title(self) -> str:
        return self.__title

    def get_content_text(self) -> str:
        return self.__content_text

    def get_is_verified(self) -> bool:
        return self.__is_verified

    # --- In-place update ---
    def set_verification(self, is_verified: bool):
        self.__is_verified = is_verified

    # --- Equality & hashing by ID ---
    def __eq__(self, other):
        return isinstance(other, EducationContent) and self.__content_id == other.__content_id

    def __hash__(self):
        return hash(self.__content_id)


# -------------------------
# Collection of EducationContents
# -------------------------
class EducationContents:
    def __init__(self):
        self.__contents: list[EducationContent] = []

    # --- Access all ---
    def get_all_list(self) -> list[EducationContent]:
        return self.__contents.copy()

    # --- Add new ---
    def add(self, content: EducationContent):
        if content is not None and content not in self.__contents:
            self.__contents.append(content)

    # --- Filters ---
    def filter_by_content_id(self, content_id: int) -> 'EducationContents':
        results = EducationContents()
        for c in self.__contents:
            if c.get_content_id() == content_id:
                results.add(c)
        return results

    def filter_by_disease_id(self, disease_id: int) -> 'EducationContents':
        results = EducationContents()
        for c in self.__contents:
            if c.get_disease_id() == disease_id:
                results.add(c)
        return results

    def filter_by_title(self, title: str) -> 'EducationContents':
        results = EducationContents()
        for c in self.__contents:
            if title.lower() in c.get_title().lower():
                results.add(c)
        return results


# -------------------------
# Global Cache
# -------------------------
cache_all_education_content: EducationContents | None = None


# -------------------------
# Load all contents from DB
# -------------------------
def load_all_education_content() -> EducationContents:
    content_list = EducationContents()
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content_id, disease_id, title, content_text, is_verified FROM educational_content;"
        )
        rows = cursor.fetchall()
        for row in rows:
            content = EducationContent(row[0], row[1], row[2], row[3], row[4])
            content_list.add(content)
    except Exception as e:
        print(f"Error retrieving educational contents: {e}")
    finally:
        conn.close()
    return content_list


# -------------------------
# Add new content
# -------------------------
def add_new_educational_content(disease_id: int, title: str, content_text: str, is_verified: bool) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO educational_content (disease_id, title, content_text, is_verified) VALUES (?, ?, ?, ?);",
            (disease_id, title, content_text, is_verified)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_education_content
        if cache_all_education_content is not None and cursor.lastrowid is not None:
            new_content = EducationContent(cursor.lastrowid, disease_id, title, content_text, is_verified)
            cache_all_education_content.add(new_content)
        else:
            cache_all_education_content = load_all_education_content()

        return True
    except Exception as e:
        print(f"Error creating educational content: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Update content verification
# -------------------------
def set_educational_content_verification(content_id: int, is_verified: bool) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE educational_content SET is_verified=? WHERE content_id=?;",
            (is_verified, content_id)
        )
        conn.commit()

        # Incremental cache update
        global cache_all_education_content
        if cache_all_education_content is not None:
            for c in cache_all_education_content.get_all_list():
                if c.get_content_id() == content_id:
                    c.set_verification(is_verified)
                    break

        return True
    except Exception as e:
        print(f"Error updating educational content: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# -------------------------
# Get cache (refresh optional)
# -------------------------
def get_all_education_content_cache(refresh_cache: bool = False) -> EducationContents:
    global cache_all_education_content
    if cache_all_education_content is None or refresh_cache:
        cache_all_education_content = load_all_education_content()
    return cache_all_education_content
