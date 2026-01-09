#!/usr/env python3

import pytest

from db.core import reset_database

from core.core import get_disease_list_from_symptom_list
from core.core import get_disease_list_from_symptom_list_incude_exclude
from core.core import get_top_bottom_k_diseases_from_diseases_list
from core.core import get_top_k_diseases_from_diseases_list
from core.core import get_bottom_k_diseases_from_diseases_list
from core.core import get_education_content_for_diseases
from core.disease_symptoms_relation import add_new_diseases_symptom_relation
from core.disease import add_new_disease, get_all_diseases_cache
from core.symptoms import add_new_symptom, get_all_symptoms_cache
from content.educational_content import add_new_educational_content


@pytest.fixture(scope="module", autouse=True)
def db_init_for_core_testing():
    reset_database()
    populate_database_for_core_function_testing()
    yield
    reset_database()


TEST_DISEASE = [ ("disease 1", "dis category 1", "low"), ("disease 2", "dis category 2", "low"), ("disease 3", "dis category 3", "high"), ("disease 4", "dis category 4", "medium"), ("disease 5", "dis category 5", "low")]
TEST_SYMPTOM = [("symptom 1", "sym category 1"), ("symptom 2", "sym category 2"), ("symptom 3", "sym category 3"), ("symptom 4", "sym category 4"), ("symptom 5", "sym category 5"), ("symptom 6", "sym category 6"), ("symptom 7", "sym category 7"), ("symptom 8", "sym category 8"), ("symptom 9", "sym category 9"), ("symptom 10", "sym category 10")]
TEST_DISEASE_SYMPTOM_RELATION = [(1, 1), (1, 2), (2, 3), (2, 4), (2, 10), (3, 1), (3, 3), (3, 4), (4, 5), (4, 6), (4, 7), (4, 8), (5, 1), (5, 8), (5, 9), (5, 10)]
TEST_DISEASE_EDUCATION = [(1, "disease 1"), (2, "disease 2"), (3, "disease 3"), (4, "disease 4"), (5, "disease 5")]

TEST_INCLUDE_SYMPTOM = [1, 2, 3, 4, 10]
TEST_EXCLUDE_SYMPTOM = [3, 4, 5, 6, 7]
TEST_INCLUDE_SYMPTOM_RESULT_DISEASE = [1, 2, 3, 5]
TEST_INCLUDE_EXCLUDE_SYMPTOM_RESULT_DISEASE = [1, 5]

def populate_database_for_core_function_testing():
    for disease in TEST_DISEASE:
        add_new_disease(disease[0], disease[1], disease[2])
    for symptom in TEST_SYMPTOM:
        add_new_symptom(symptom[0], symptom[1])
    for rel in TEST_DISEASE_SYMPTOM_RELATION:
        add_new_diseases_symptom_relation(rel[0], rel[1], 0.5)
    for cont in TEST_DISEASE_EDUCATION:
        add_new_educational_content(cont[0], cont[1], "TEST CONTEST", True)

def test_get_disease_list_from_symptom_list__None():
    include_list = None
    res = get_disease_list_from_symptom_list(include_list)
    assert(len(res) == 0)

def test_get_disease_list_from_symptom_list__some():
    include_list = []
    res = get_disease_list_from_symptom_list(include_list)
    assert(len(res) == 0)

def test_get_disease_list_from_symptom_list():
    include_list = [x for x in get_all_symptoms_cache().get_all_list() if x.get_id() in TEST_INCLUDE_SYMPTOM]
    res = get_disease_list_from_symptom_list(include_list)
    for d in res:
        assert(d in TEST_INCLUDE_SYMPTOM_RESULT_DISEASE)

def test_get_disease_list_from_symptom_list_incude_exclude_None_include_some_exclude():
    include_list = None
    exclude_list = [x for x in get_all_symptoms_cache().get_all_list() if x.get_id() in TEST_EXCLUDE_SYMPTOM]
    res = get_disease_list_from_symptom_list_incude_exclude(include_list, exclude_list)
    assert(len(res) == 0)

def test_get_disease_list_from_symptom_list_incude_exclude_empty_include_some_exclude():
    include_list = []
    exclude_list = [x for x in get_all_symptoms_cache().get_all_list() if x.get_id() in TEST_EXCLUDE_SYMPTOM]
    res = get_disease_list_from_symptom_list_incude_exclude(include_list, exclude_list)
    assert(len(res) == 0)

def test_get_disease_list_from_symptom_list_incude_exclude_only_include_None_exclude():
    include_list = [x for x in get_all_symptoms_cache().get_all_list() if x.get_id() in TEST_INCLUDE_SYMPTOM]
    exclude_list = None
    res = get_disease_list_from_symptom_list_incude_exclude(include_list, exclude_list)
    for d in res:
        assert(d in TEST_INCLUDE_SYMPTOM_RESULT_DISEASE)

def test_get_disease_list_from_symptom_list_incude_exclude_only_include_empty_exclude():
    include_list = [x for x in get_all_symptoms_cache().get_all_list() if x.get_id() in TEST_INCLUDE_SYMPTOM]
    exclude_list = []
    res = get_disease_list_from_symptom_list_incude_exclude(include_list, exclude_list)
    for d in res:
        assert(d in TEST_INCLUDE_SYMPTOM_RESULT_DISEASE)

def test_get_disease_list_from_symptom_list_incude_exclude():
    include_list = [x for x in get_all_symptoms_cache().get_all_list() if x.get_id() in TEST_INCLUDE_SYMPTOM]
    exclude_list = [x for x in get_all_symptoms_cache().get_all_list() if x.get_id() in TEST_EXCLUDE_SYMPTOM]
    res = get_disease_list_from_symptom_list_incude_exclude(include_list, exclude_list)
    for d in res:
        assert(d in TEST_INCLUDE_EXCLUDE_SYMPTOM_RESULT_DISEASE)

def test_get_top_bottom_k_diseases_from_diseases_list():
    sample = [x for x in get_all_diseases_cache().get_all_diseases_list() if x.get_category() in [1,2,3,4,5]]
    top_2, bottom_2 = get_top_bottom_k_diseases_from_diseases_list(sample, 2)
    for t in top_2:
        assert(t.get_disease_id() in [3, 4])
    for t in bottom_2:
        assert(t.get_disease_id() in [1, 2, 5])

def test_get_top_k_diseases_from_diseases_list():
    sample = [x for x in get_all_diseases_cache().get_all_diseases_list() if x.get_category() in [1,2,3,4,5]]
    top_2 = get_top_k_diseases_from_diseases_list(sample, 2)
    for t in top_2:
        assert(t.get_disease_id() in [3, 4])

def test_get_bottom_k_diseases_from_diseases_list():
    sample = [x for x in get_all_diseases_cache().get_all_diseases_list() if x.get_category() in [1,2,3,4,5]]
    top_2 = get_bottom_k_diseases_from_diseases_list(sample, 3)
    for t in top_2:
        assert(t.get_disease_id() in [1, 2, 5])

def test_get_education_content_for_diseases__except_4():
    sample = [x for x in get_all_diseases_cache().get_all_diseases_list() if x.get_category() in [1,2,3,5]]
    res = get_education_content_for_diseases(sample)
    for sample in res:
        assert(sample.get_disease_id() == int(sample.get_title().split(" ")[1]))

def test_get_education_content_for_diseases():
    sample = get_all_diseases_cache().get_all_diseases_list()
    res = get_education_content_for_diseases(sample)
    for sample in res:
        assert(sample.get_disease_id() == int(sample.get_title().split(" ")[1]))


