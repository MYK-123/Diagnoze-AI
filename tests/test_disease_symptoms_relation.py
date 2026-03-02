#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.disease_symptoms_relation import (
    DiseaseSymptomRelation, DiseaseSymptomRelations, 
    load_all_relations, add_new_diseases_symptom_relation,
    set_diseases_symptom_relation_data, get_relations_cache
)


class TestDiseaseSymptomRelation(unittest.TestCase):
    """Test the DiseaseSymptomRelation entity class"""

    def setUp(self):
        self.relation = DiseaseSymptomRelation(1, 1, 2, 0.85)

    def test_relation_init(self):
        """Test relation initialization"""
        self.assertEqual(self.relation.get_relation_id(), 1)
        self.assertEqual(self.relation.get_disease_id(), 1)
        self.assertEqual(self.relation.get_symptom_id(), 2)
        self.assertEqual(self.relation.get_strength(), 0.85)

    def test_relation_getters(self):
        """Test all relation getters"""
        self.assertEqual(self.relation.get_relation_id(), 1)
        self.assertEqual(self.relation.get_disease_id(), 1)
        self.assertEqual(self.relation.get_symptom_id(), 2)
        self.assertEqual(self.relation.get_strength(), 0.85)

    def test_relation_update(self):
        """Test relation update"""
        self.relation.update(2, 3, 0.5)
        self.assertEqual(self.relation.get_disease_id(), 2)
        self.assertEqual(self.relation.get_symptom_id(), 3)
        self.assertEqual(self.relation.get_strength(), 0.5)

    def test_relation_equality(self):
        """Test relation equality by ID"""
        relation2 = DiseaseSymptomRelation(1, 5, 6, 0.5)
        relation3 = DiseaseSymptomRelation(2, 1, 2, 0.85)
        self.assertEqual(self.relation, relation2)
        self.assertNotEqual(self.relation, relation3)

    def test_relation_hash(self):
        """Test relation hashing"""
        relation2 = DiseaseSymptomRelation(1, 5, 6, 0.5)
        self.assertEqual(hash(self.relation), hash(relation2))

    def test_relation_equality_non_relation(self):
        """Test equality with non-relation objects"""
        self.assertNotEqual(self.relation, "Not a relation")
        self.assertNotEqual(self.relation, 1)


class TestDiseaseSymptomRelations(unittest.TestCase):
    """Test the DiseaseSymptomRelations collection class"""

    def setUp(self):
        self.relations = DiseaseSymptomRelations()
        self.rel1 = DiseaseSymptomRelation(1, 1, 2, 0.85)
        self.rel2 = DiseaseSymptomRelation(2, 1, 3, 0.6)
        self.rel3 = DiseaseSymptomRelation(3, 2, 2, 0.75)

    def test_relations_init(self):
        """Test relations collection initialization"""
        self.assertEqual(len(self.relations.get_all_relation_list()), 0)

    def test_relations_add(self):
        """Test adding relations"""
        self.relations.add(self.rel1)
        self.assertEqual(len(self.relations.get_all_relation_list()), 1)

    def test_relations_add_duplicate(self):
        """Test that duplicate relations are not added"""
        self.relations.add(self.rel1)
        self.relations.add(self.rel1)
        self.assertEqual(len(self.relations.get_all_relation_list()), 1)

    def test_relations_add_none(self):
        """Test that None is not added"""
        self.relations.add(None)
        self.assertEqual(len(self.relations.get_all_relation_list()), 0)

    def test_relations_filter_by_symptom_id(self):
        """Test filtering relations by symptom ID"""
        self.relations.add(self.rel1)
        self.relations.add(self.rel2)
        self.relations.add(self.rel3)
        filtered = self.relations.filter_by_symptom_id(2)
        self.assertEqual(len(filtered.get_all_relation_list()), 2)

    def test_relations_filter_by_disease_id(self):
        """Test filtering relations by disease ID"""
        self.relations.add(self.rel1)
        self.relations.add(self.rel2)
        self.relations.add(self.rel3)
        filtered = self.relations.filter_by_disease_id(1)
        self.assertEqual(len(filtered.get_all_relation_list()), 2)

    def test_relations_filter_by_strength(self):
        """Test filtering relations by strength"""
        self.relations.add(self.rel1)
        self.relations.add(self.rel2)
        filtered = self.relations.filter_by_strength(0.85)
        self.assertEqual(len(filtered.get_all_relation_list()), 1)

    def test_get_strengths_by_disease_and_symptom(self):
        """Test getting strength by disease and symptom ID"""
        self.relations.add(self.rel1)
        strength = self.relations.get_strengths_by_disease_id_and_symptom_id(1, 2)
        self.assertEqual(strength, 0.85)

    def test_get_strengths_not_found(self):
        """Test getting strength when not found"""
        self.relations.add(self.rel1)
        strength = self.relations.get_strengths_by_disease_id_and_symptom_id(5, 5, 0.001)
        self.assertEqual(strength, 0.001)

    def test_get_strengths_custom_not_found(self):
        """Test getting strength with custom not_found value"""
        self.relations.add(self.rel1)
        strength = self.relations.get_strengths_by_disease_id_and_symptom_id(5, 5, 0.5)
        self.assertEqual(strength, 0.5)


class TestDiseaseSymptomRelationsDatabase(unittest.TestCase):
    """Test disease-symptom relations database operations"""

    @patch('core.disease_symptoms_relation.coredb.getDBObject')
    def test_load_all_relations(self, mock_get_db):
        """Test loading all relations from database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 1, 2, 0.85),
            (2, 1, 3, 0.6),
            (3, 2, 2, 0.75)
        ]

        relations = load_all_relations()
        self.assertEqual(len(relations.get_all_relation_list()), 3)
        mock_conn.close.assert_called_once()

    @patch('core.disease_symptoms_relation.coredb.getDBObject')
    def test_load_all_relations_empty(self, mock_get_db):
        """Test loading relations when database is empty"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        relations = load_all_relations()
        self.assertEqual(len(relations.get_all_relation_list()), 0)

    @patch('core.disease_symptoms_relation.coredb.getDBObject')
    def test_load_all_relations_exception(self, mock_get_db):
        """Test loading relations with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            relations = load_all_relations()
        self.assertEqual(len(relations.get_all_relation_list()), 0)

    @patch('core.disease_symptoms_relation.coredb.getDBObject')
    def test_add_new_relation_success(self, mock_get_db):
        """Test adding a new relation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        import core.disease_symptoms_relation
        core.disease_symptoms_relation.cache_all_diseases_symptom_relation = None

        success, rel_id = add_new_diseases_symptom_relation(1, 2, 0.85)
        self.assertTrue(success)
        self.assertEqual(rel_id, 1)
        mock_conn.commit.assert_called_once()

    @patch('core.disease_symptoms_relation.coredb.getDBObject')
    def test_add_new_relation_exception(self, mock_get_db):
        """Test adding a relation with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success, rel_id = add_new_diseases_symptom_relation(1, 2, 0.85)
        self.assertFalse(success)
        self.assertEqual(rel_id, -1)

    @patch('core.disease_symptoms_relation.coredb.getDBObject')
    def test_set_relation_data_success(self, mock_get_db):
        """Test updating relation data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        import core.disease_symptoms_relation
        core.disease_symptoms_relation.cache_all_diseases_symptom_relation = None

        success = set_diseases_symptom_relation_data(1, 2, 3, 0.5)
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.disease_symptoms_relation.coredb.getDBObject')
    def test_set_relation_data_exception(self, mock_get_db):
        """Test updating relation with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = set_diseases_symptom_relation_data(1, 2, 3, 0.5)
        self.assertFalse(success)

    @patch('core.disease_symptoms_relation.load_all_relations')
    def test_get_relations_cache(self, mock_load):
        """Test getting relations cache"""
        mock_relations = DiseaseSymptomRelations()
        mock_relations.add(DiseaseSymptomRelation(1, 1, 2, 0.85))
        mock_load.return_value = mock_relations

        import core.disease_symptoms_relation
        core.disease_symptoms_relation.cache_all_diseases_symptom_relation = None

        result = get_relations_cache()
        self.assertEqual(len(result.get_all_relation_list()), 1)


if __name__ == '__main__':
    unittest.main()
