import pytest
from unittest.mock import Mock, MagicMock, patch
import sys

# Mock modules before importing
sys.modules['db'] = MagicMock()
sys.modules['db.core'] = MagicMock()

from core.disease import (
    Disease,
    Diseases,
    load_all_diseases,
    add_new_disease,
    set_disease_data,
    get_all_diseases_cache,
    DISEASE_SEVERITY_RANK
)


class TestDiseaseClass:
    """Tests for Disease class"""
    
    def test_disease_creation(self):
        """Test creating a disease object"""
        disease = Disease(
            disease_id=1,
            disease_name="Common Cold",
            category="Viral",
            severity_level="low"
        )
        
        assert disease.get_disease_id() == 1
        assert disease.get_disease_name() == "Common Cold"
        assert disease.get_category() == "Viral"
        assert disease.get_severity_level() == DISEASE_SEVERITY_RANK["low"]

    def test_disease_severity_mapping(self):
        """Test disease severity level mapping"""
        disease_low = Disease(1, "Low", "Cat", "low")
        disease_medium = Disease(2, "Medium", "Cat", "medium")
        disease_high = Disease(3, "High", "Cat", "high")
        
        assert disease_low.get_severity_level() < disease_medium.get_severity_level()
        assert disease_medium.get_severity_level() < disease_high.get_severity_level()

    def test_disease_update(self):
        """Test updating disease information"""
        disease = Disease(1, "Original", "Cat1", "low")
        disease.update("Updated", "Cat2", "high")
        
        assert disease.get_disease_name() == "Updated"
        assert disease.get_category() == "Cat2"
        assert disease.get_severity_level() == DISEASE_SEVERITY_RANK["high"]

    def test_disease_equality(self):
        """Test disease equality comparison"""
        disease1 = Disease(1, "Cold", "Viral", "low")
        disease2 = Disease(1, "Common Cold", "Viral", "medium")
        disease3 = Disease(2, "Cold", "Viral", "low")
        
        assert disease1 == disease2  # Same ID
        assert disease1 != disease3  # Different ID

    def test_disease_hashing(self):
        """Test disease hashing"""
        disease1 = Disease(1, "Cold", "Viral", "low")
        disease2 = Disease(1, "Cold", "Viral", "low")
        
        disease_set = {disease1, disease2}
        assert len(disease_set) == 1  # Should be same hash

    def test_disease_invalid_severity(self):
        """Test disease with invalid severity level"""
        disease = Disease(1, "Test", "Cat", "invalid_severity")
        
        # Should default to 0
        assert disease.get_severity_level() == 0


class TestDiseasesCollection:
    """Tests for Diseases collection class"""
    
    def test_diseases_creation(self):
        """Test creating Diseases collection"""
        diseases = Diseases()
        
        assert len(diseases) == 0

    def test_diseases_add(self):
        """Test adding disease to collection"""
        diseases = Diseases()
        disease = Disease(1, "Cold", "Viral", "low")
        
        diseases.add(disease)
        
        assert len(diseases) == 1

    def test_diseases_add_duplicate(self):
        """Test that duplicate diseases are not added"""
        diseases = Diseases()
        disease = Disease(1, "Cold", "Viral", "low")
        
        diseases.add(disease)
        diseases.add(disease)
        
        assert len(diseases) == 1

    def test_diseases_add_none(self):
        """Test adding None disease"""
        diseases = Diseases()
        
        diseases.add(None)
        
        assert len(diseases) == 0

    def test_diseases_iteration(self):
        """Test iterating over diseases"""
        diseases = Diseases()
        disease1 = Disease(1, "Cold", "Viral", "low")
        disease2 = Disease(2, "Flu", "Viral", "medium")
        
        diseases.add(disease1)
        diseases.add(disease2)
        
        disease_list = list(diseases)
        assert len(disease_list) == 2

    def test_diseases_get_all(self):
        """Test getting all diseases"""
        diseases = Diseases()
        disease1 = Disease(1, "Cold", "Viral", "low")
        disease2 = Disease(2, "Flu", "Viral", "medium")
        
        diseases.add(disease1)
        diseases.add(disease2)
        
        all_diseases = diseases.get_all_diseases_list()
        
        assert len(all_diseases) == 2
        assert disease1 in all_diseases

    def test_diseases_filter_by_id(self):
        """Test filtering diseases by ID"""
        diseases = Diseases()
        disease1 = Disease(1, "Cold", "Viral", "low")
        disease2 = Disease(2, "Flu", "Viral", "medium")
        
        diseases.add(disease1)
        diseases.add(disease2)
        
        filtered = diseases.filter_by_id(1)
        
        assert len(filtered) == 1
        assert filtered.get_all_diseases_list()[0].get_disease_id() == 1

    def test_diseases_filter_by_name(self):
        """Test filtering diseases by name"""
        diseases = Diseases()
        disease1 = Disease(1, "Common Cold", "Viral", "low")
        disease2 = Disease(2, "Flu", "Viral", "medium")
        
        diseases.add(disease1)
        diseases.add(disease2)
        
        filtered = diseases.filter_by_name("Cold")
        
        assert len(filtered) == 1

    def test_diseases_filter_by_category(self):
        """Test filtering diseases by category"""
        diseases = Diseases()
        disease1 = Disease(1, "Cold", "Viral", "low")
        disease2 = Disease(2, "Bacterial", "Bacterial", "medium")
        
        diseases.add(disease1)
        diseases.add(disease2)
        
        filtered = diseases.filter_by_category("Viral")
        
        assert len(filtered) == 1

    def test_diseases_filter_by_severity(self):
        """Test filtering diseases by severity"""
        diseases = Diseases()
        disease1 = Disease(1, "Cold", "Viral", "low")
        disease2 = Disease(2, "Flu", "Viral", "high")
        
        diseases.add(disease1)
        diseases.add(disease2)
        
        filtered = diseases.filter_by_severity_level("high")
        
        assert len(filtered) == 1


class TestAddNewDisease:
    """Tests for add_new_disease function"""
    
    @patch('core.disease.coredb.getDBObject')
    def test_add_new_disease_success(self, mock_get_db):
        """Test successful disease addition"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        
        success, disease_id = add_new_disease("Test Disease", "Category", "low")
        
        assert success is True
        assert disease_id == 1

    @patch('core.disease.coredb.getDBObject')
    def test_add_new_disease_with_int_severity(self, mock_get_db):
        """Test adding disease with integer severity"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        
        success, disease_id = add_new_disease("Test", "Cat", 2)
        
        assert success is True

    @patch('core.disease.coredb.getDBObject')
    def test_add_new_disease_exception(self, mock_get_db):
        """Test disease addition with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")
        
        success, disease_id = add_new_disease("Test", "Cat", "low")
        
        assert success is False
        assert disease_id == -1


class TestSetDiseaseData:
    """Tests for set_disease_data function"""
    
    @patch('core.disease.coredb.getDBObject')
    def test_set_disease_data_success(self, mock_get_db):
        """Test successful disease data update"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        success = set_disease_data(1, "Updated", "NewCat", "high")
        
        assert success is True
        assert mock_conn.commit.called

    @patch('core.disease.coredb.getDBObject')
    def test_set_disease_data_exception(self, mock_get_db):
        """Test disease data update with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")
        
        success = set_disease_data(1, "Updated", "Cat", "high")
        
        assert success is False


class TestGetAllDiseasesCache:
    """Tests for get_all_diseases_cache function"""
    
    @patch('core.disease.load_all_diseases')
    def test_get_cache_loads_once(self, mock_load):
        """Test that cache is loaded once"""
        mock_diseases = Diseases()
        mock_load.return_value = mock_diseases
        
        # Reset cache
        import core.disease
        core.disease.cache_all_diseases = None
        
        result1 = get_all_diseases_cache()
        result2 = get_all_diseases_cache()
        
        # load_all_diseases should be called only once
        assert mock_load.call_count == 1
        assert result1 is result2

    @patch('core.disease.load_all_diseases')
    def test_get_cache_refresh(self, mock_load):
        """Test cache refresh"""
        mock_diseases = Diseases()
        mock_load.return_value = mock_diseases
        
        import core.disease
        core.disease.cache_all_diseases = None
        
        result1 = get_all_diseases_cache()
        result2 = get_all_diseases_cache(refresh_cache=True)
        
        # load_all_diseases should be called twice
        assert mock_load.call_count == 2


class TestDiseaseConstants:
    """Tests for disease severity constants"""
    
    def test_severity_rank_values(self):
        """Test severity rank mapping"""
        assert DISEASE_SEVERITY_RANK["low"] == 1
        assert DISEASE_SEVERITY_RANK["medium"] == 2
        assert DISEASE_SEVERITY_RANK["high"] == 3

    def test_severity_rank_keys(self):
        """Test severity rank keys"""
        assert "low" in DISEASE_SEVERITY_RANK
        assert "medium" in DISEASE_SEVERITY_RANK
        assert "high" in DISEASE_SEVERITY_RANK
