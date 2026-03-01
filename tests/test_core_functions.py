#!/usr/env python3

import pytest

from db.core import reset_database

from core.core import predict_internal
from core.core import predict
from core.core import get_symptom_list_from_disease
from core.core import get_top_k_diseases_from_diseases_list
from core.core import get_top_k_diseases_from_prediction_with_probablities
from core.core import get_education_content_for_disease
from core.core import get_education_content_for_diseases
from core.core import get_symptoms_string_from_symptom_list
from core.core import get_symptom_list_from_symptom_string
from core.disease_symptoms_relation import add_new_diseases_symptom_relation
from core.disease import add_new_disease, get_all_diseases_cache
from core.symptoms import Symptom, add_new_symptom, get_all_symptoms_cache
from content.educational_content import add_new_educational_content


@pytest.fixture(scope="module", autouse=True)
def db_init_for_core_testing():
    reset_database(populate_default=True)
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

TEST_SYMPTOM_OBJS = [Symptom(idx, *name) for idx, name in enumerate(TEST_SYMPTOM, start=1)]

def populate_database_for_core_function_testing():
    for disease in TEST_DISEASE:
        add_new_disease(*disease)
    for symptom in TEST_SYMPTOM:
        add_new_symptom(*symptom)
    for rel in TEST_DISEASE_SYMPTOM_RELATION:
        add_new_diseases_symptom_relation(*rel, 0.5)
    for cont in TEST_DISEASE_EDUCATION:
        add_new_educational_content(*cont, "TEST CONTEST", True)


def test_get_symptoms_string_from_symptom_list():
    x = get_symptoms_string_from_symptom_list(TEST_SYMPTOM_OBJS).split(", ")
    assert(len(x) == len(TEST_SYMPTOM_OBJS))
    for i in range(0, len(x)):
        assert(x[i] == TEST_SYMPTOM_OBJS[i].get_name())

def test_get_symptom_list_from_symptom_string():
    x = get_symptom_list_from_symptom_string("symptom 1, symptom 2, symptom 3")
    assert(len(x) == 3)
    for v in x:
        assert(v.get_name() in [y for y in "symptom 1, symptom 2, symptom 3".split(", ")])


def test_get_top_k_diseases_from_diseases_list():
    sample = [x for x in get_all_diseases_cache().get_all_diseases_list() if x.get_category() in [1,2,3,4,5]]
    top_2 = get_top_k_diseases_from_diseases_list(sample, 2)
    for t in top_2:
        assert(t.get_disease_id() in [3, 4])

def test_get_education_content_for_diseases__except_4():
    sample = [x for x in get_all_diseases_cache().get_all_diseases_list() if x.get_category() in [1,2,3,5]]
    res = get_education_content_for_diseases(sample)
    for sample in res:
        assert(sample.get_disease_id() == int(sample.get_title().split(" ")[1]))

def test_get_education_content_for_diseases():
    sample = get_all_diseases_cache().get_all_diseases_list()
    res = get_education_content_for_diseases(sample)
    for sample in res:
        assert(sample.get_disease_id() == sample.get_disease_id())


def test_get_education_content_for_disease():
    sample = get_all_diseases_cache().get_all_diseases_list()
    res = get_education_content_for_disease(sample[0])
    assert(res is not None)
    assert(sample[0].get_disease_id() == res.get_disease_id())


