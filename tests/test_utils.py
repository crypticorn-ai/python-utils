import datetime

import pytest

from crypticorn_utils.utils import gen_random_id, optional_import, datetime_to_timestamp


class TestGenRandomId:
    """Test the gen_random_id function."""

    def test_gen_random_id_default_length(self):
        """Test gen_random_id with default length."""
        result = gen_random_id()
        assert len(result) == 20
        assert result.isalnum()  # Only letters and digits

    def test_gen_random_id_custom_length(self):
        """Test gen_random_id with custom length."""
        result = gen_random_id(10)
        assert len(result) == 10
        assert result.isalnum()

    def test_gen_random_id_different_lengths(self):
        """Test gen_random_id with various lengths."""
        for length in [1, 5, 15, 40]:
            result = gen_random_id(length)
            assert len(result) == length
            assert result.isalnum()

    def test_gen_random_id_uniqueness(self):
        """Test that gen_random_id generates different values."""
        results = [gen_random_id(10) for _ in range(50)]
        assert len(set(results)) > 45  # High uniqueness


class TestOptionalImport:
    """Test the optional_import function."""

    def test_optional_import_success(self):
        """Test optional_import with a valid module."""
        # Test with a module that should exist
        result = optional_import("datetime", "test")
        assert result is not None
        assert hasattr(result, "datetime")

    def test_optional_import_failure(self):
        """Test optional_import with an invalid module."""
        with pytest.raises(ImportError) as exc_info:
            optional_import("nonexistent_module_12345", "test_extra")
        
        error_msg = str(exc_info.value)
        assert "Optional dependency 'nonexistent_module_12345' is required" in error_msg
        assert "pip install crypticorn[test_extra]" in error_msg

    def test_optional_import_preserves_original_error(self):
        """Test that optional_import preserves the original ImportError."""
        with pytest.raises(ImportError) as exc_info:
            optional_import("nonexistent_module_12345", "test_extra")
        assert exc_info.value.__cause__ is not None


class TestDatetimeToTimestamp:
    """Test the datetime_to_timestamp function."""

    def test_datetime_to_timestamp_single_datetime(self):
        """Test datetime_to_timestamp with a single datetime."""
        dt = datetime.datetime(2023, 1, 1, 12, 0, 0)
        result = datetime_to_timestamp(dt)
        expected = int(dt.timestamp())
        assert result == expected
        assert isinstance(result, int)

    def test_datetime_to_timestamp_list_of_datetimes(self):
        """Test datetime_to_timestamp with a list of datetimes."""
        dt1 = datetime.datetime(2023, 1, 1, 12, 0, 0)
        dt2 = datetime.datetime(2023, 1, 2, 12, 0, 0)
        result = datetime_to_timestamp([dt1, dt2])
        expected = [int(dt1.timestamp()), int(dt2.timestamp())]
        assert result == expected
        assert all(isinstance(x, int) for x in result)

    def test_datetime_to_timestamp_mixed_list(self):
        """Test datetime_to_timestamp with mixed list (datetime and non-datetime)."""
        dt = datetime.datetime(2023, 1, 1, 12, 0, 0)
        result = datetime_to_timestamp([dt, "string", 123])
        expected = [int(dt.timestamp()), "string", 123]
        assert result == expected

    def test_datetime_to_timestamp_non_datetime(self):
        """Test datetime_to_timestamp with non-datetime values."""
        assert datetime_to_timestamp("test") == "test"
        assert datetime_to_timestamp(123) == 123
        assert datetime_to_timestamp(None) is None
        assert datetime_to_timestamp([]) == []
