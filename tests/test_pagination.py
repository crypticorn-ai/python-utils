from typing import Literal, Optional

import pytest
from pydantic import BaseModel, ValidationError

from crypticorn_utils.pagination import (
    FilterParams,
    HeavyPageSortFilterParams,
    HeavyPaginationParams,
    PageFilterParams,
    PageSortFilterParams,
    PageSortParams,
    PaginatedResponse,
    PaginationParams,
    SortFilterParams,
    SortParams,
)


class Item(BaseModel):
    name: str
    value: int


@pytest.mark.asyncio
async def test_pagination_params():
    # Test default values
    params = PaginationParams[Item]()
    assert params.page == 1
    assert params.page_size == 10

    # Test custom values
    params = PaginationParams[Item](page=2, page_size=20)
    assert params.page == 2
    assert params.page_size == 20

    # Test page_size validation (should be between 1 and 100)
    with pytest.raises(ValidationError):
        PaginationParams[Item](page_size=0)

    with pytest.raises(ValidationError):
        PaginationParams[Item](page_size=101)


@pytest.mark.asyncio
async def test_heavy_pagination_params():
    # Test default values
    params = HeavyPaginationParams[Item]()
    assert params.page == 1
    assert params.page_size == 100

    # Test custom values
    params = HeavyPaginationParams[Item](page=2, page_size=200)
    assert params.page == 2
    assert params.page_size == 200

    # Test page_size validation (should be between 1 and 1000)
    with pytest.raises(ValidationError):
        HeavyPaginationParams[Item](page_size=0)

    with pytest.raises(ValidationError):
        HeavyPaginationParams[Item](page_size=1001)


@pytest.mark.asyncio
async def test_sort_params():
    # Test that SortParams requires BaseModel generic
    with pytest.raises(
        TypeError,
        match="SortParams must be used with a Pydantic BaseModel as a generic parameter",
    ):
        SortParams[int]()

    # Test invalid sort field
    with pytest.raises(
        ValueError,
        match="Invalid field: 'foo'. Must be one of: \\['name', 'value'\\]",
    ):
        SortParams[Item](sort_by="foo", sort_order="asc")

    # Test that sort_by and sort_order must be provided together
    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        SortParams[Item](sort_by="name")

    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        SortParams[Item](sort_order="asc")

    # Test valid combination
    params = SortParams[Item](sort_by="name", sort_order="asc")
    assert params.sort_by == "name"
    assert params.sort_order == "asc"

    # Test default values
    params = SortParams[Item]()
    assert params.sort_by is None
    assert params.sort_order is None


@pytest.mark.asyncio
async def test_sort_order_validation():
    # Test invalid order values - this should be caught by Pydantic's Literal validation
    with pytest.raises(ValidationError):
        SortParams[Item](sort_by="name", sort_order="invalid")  # type: ignore[arg-type]

    # Test valid order values
    params = SortParams[Item](sort_by="name", sort_order="asc")  # type: ignore[arg-type]
    assert params.sort_order == "asc"

    params = SortParams[Item](sort_by="name", sort_order="desc")  # type: ignore[arg-type]
    assert params.sort_order == "desc"


@pytest.mark.asyncio
async def test_filter_params():
    # Test that FilterParams requires BaseModel generic
    with pytest.raises(
        TypeError,
        match="FilterParams must be used with a Pydantic BaseModel as a generic parameter",
    ):
        FilterParams[int](filter_by="name", filter_value="test")

    # Test that filter_value must be provided when filter_by is set
    with pytest.raises(
        ValueError, match="filter_by and filter_value must be provided together"
    ):
        FilterParams[Item](filter_by="name")

    # Test invalid filter field
    with pytest.raises(
        ValueError,
        match="Invalid field: 'foo'. Must be one of: \\['name', 'value'\\]",
    ):
        FilterParams[Item](filter_by="foo", filter_value="test")

    # Test valid filter
    params = FilterParams[Item](filter_by="name", filter_value="test")
    assert params.filter_by == "name"
    assert params.filter_value == "test"


class Econ(BaseModel):
    impact: Optional[Literal["Low", "Medium", "High"]]
    previous: Optional[float]
    flag: Optional[bool]
    label: str


@pytest.mark.asyncio
async def test_filter_params_literal_optional_valid():
    params = FilterParams[Econ](filter_by="impact", filter_value="High")
    assert params.filter_value == "High"


@pytest.mark.asyncio
async def test_filter_params_literal_optional_none_text():
    params = FilterParams[Econ](filter_by="impact", filter_value="none")
    assert params.filter_value is None


@pytest.mark.asyncio
async def test_filter_params_literal_optional_invalid_raises_value_error():
    with pytest.raises(ValueError):
        FilterParams[Econ](filter_by="impact", filter_value="INVALID")


@pytest.mark.asyncio
async def test_filter_params_float_coercion():
    params = FilterParams[Econ](filter_by="previous", filter_value="1.23")
    assert params.filter_value == 1.23


@pytest.mark.asyncio
async def test_filter_params_bool_coercion_truthy():
    params = FilterParams[Econ](filter_by="flag", filter_value="true")
    assert params.filter_value is True


@pytest.mark.asyncio
async def test_filter_params_bool_coercion_falsy():
    params = FilterParams[Econ](filter_by="flag", filter_value="0")
    assert params.filter_value is False


@pytest.mark.asyncio
async def test_filter_params_string_passthrough():
    params1 = FilterParams[Econ](filter_by="label", filter_value="Hello")
    assert params1.filter_value == "Hello"

    # Test default values
    params2 = FilterParams[Item]()
    assert params2.filter_by is None
    assert params2.filter_value is None


@pytest.mark.asyncio
async def test_sort_filter_params():
    # Test combined functionality
    params1 = SortFilterParams[Item](
        sort_by="value",
        sort_order="desc",
        filter_by="name",
        filter_value="test",
    )
    assert params1.sort_by == "value"
    assert params1.sort_order == "desc"
    assert params1.filter_by == "name"
    assert params1.filter_value == "test"

    # Test default values
    params2 = SortFilterParams[Item]()
    assert params2.sort_by is None
    assert params2.sort_order is None
    assert params2.filter_by is None
    assert params2.filter_value is None

    # Test sort validation still works
    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        SortFilterParams[Item](sort_by="name")

    # Test filter validation still works
    with pytest.raises(
        ValueError, match="filter_by and filter_value must be provided together"
    ):
        SortFilterParams[Item](filter_by="name")


@pytest.mark.asyncio
async def test_page_filter_params():
    # Test combined functionality
    params = PageFilterParams[Item](
        page=2,
        page_size=20,
        filter_by="name",
        filter_value="test",
    )
    assert params.page == 2
    assert params.page_size == 20
    assert params.filter_by == "name"
    assert params.filter_value == "test"

    # Test default values
    params = PageFilterParams[Item]()
    assert params.page == 1
    assert params.page_size == 10
    assert params.filter_by is None
    assert params.filter_value is None

    # Test filter validation still works
    with pytest.raises(
        ValueError, match="filter_by and filter_value must be provided together"
    ):
        PageFilterParams[Item](filter_by="name")


@pytest.mark.asyncio
async def test_page_sort_params():
    # Test combined functionality
    params = PageSortParams[Item](
        page=2,
        page_size=20,
        sort_by="value",
        sort_order="desc",
    )
    assert params.page == 2
    assert params.page_size == 20
    assert params.sort_by == "value"
    assert params.sort_order == "desc"

    # Test default values
    params = PageSortParams[Item]()
    assert params.page == 1
    assert params.page_size == 10
    assert params.sort_by is None
    assert params.sort_order is None

    # Test sort validation still works
    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        PageSortParams[Item](sort_by="name")


@pytest.mark.asyncio
async def test_page_sort_filter_params():
    # Test combined functionality
    params = PageSortFilterParams[Item](
        page=2,
        page_size=20,
        sort_by="value",
        sort_order="desc",
        filter_by="name",
        filter_value="test",
    )
    assert params.page == 2
    assert params.page_size == 20
    assert params.sort_by == "value"
    assert params.sort_order == "desc"
    assert params.filter_by == "name"
    assert params.filter_value == "test"

    # Test default values
    params = PageSortFilterParams[Item]()
    assert params.page == 1
    assert params.page_size == 10
    assert params.sort_by is None
    assert params.sort_order is None
    assert params.filter_by is None
    assert params.filter_value is None

    # Test sort validation still works
    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        PageSortFilterParams[Item](sort_by="name")

    # Test filter validation still works
    with pytest.raises(
        ValueError, match="filter_by and filter_value must be provided together"
    ):
        PageSortFilterParams[Item](filter_by="name")


@pytest.mark.asyncio
async def test_heavy_page_sort_filter_params():
    # Test combined functionality
    params = HeavyPageSortFilterParams[Item](
        page=2,
        page_size=200,
        sort_by="value",
        sort_order="desc",
        filter_by="name",
        filter_value="test",
    )
    assert params.page == 2
    assert params.page_size == 200
    assert params.sort_by == "value"
    assert params.sort_order == "desc"
    assert params.filter_by == "name"
    assert params.filter_value == "test"

    # Test default values
    params = HeavyPageSortFilterParams[Item]()
    assert params.page == 1
    assert params.page_size == 100
    assert params.sort_by is None
    assert params.sort_order is None
    assert params.filter_by is None
    assert params.filter_value is None

    # Test page_size validation (should be between 1 and 1000)
    with pytest.raises(ValidationError):
        HeavyPageSortFilterParams[Item](page_size=0)

    with pytest.raises(ValidationError):
        HeavyPageSortFilterParams[Item](page_size=1001)


@pytest.mark.asyncio
async def test_field_type_validation():
    # Test that invalid type for filter_value raises error
    with pytest.raises(
        ValueError, match="Expected <class 'int'> for field value, got <class 'str'>"
    ):
        PageSortFilterParams[Item](
            filter_by="value", filter_value="not_a_number"
        )  # tries to coerce to int, but fails

    # Test that valid type works
    params = PageSortFilterParams[
        Item
    ](
        filter_by="value", filter_value="42"
    )  # in fact it should be an int but it comes as a string anyways from the request. the type is enforced by the model validator
    assert params.filter_value == 42

    # Test type coercion
    params = PageSortFilterParams[Item](filter_by="name", filter_value="1")
    assert (
        params.filter_value == "1"
    )  # since name is a str, it will be coerced to a string

    params = PageSortFilterParams[Item](filter_by="name", filter_value="test")
    assert params.filter_value == "test"


# MISSING BRANCH COVERAGE TESTS
@pytest.mark.asyncio
async def test_paginated_response_get_next_page():
    """Test get_next_page in various scenarios"""
    # Test when there is a next page
    result = PaginatedResponse.get_next_page(total=100, page_size=10, page=5)
    assert result == 6

    # Test when page is the last page
    result = PaginatedResponse.get_next_page(total=100, page_size=10, page=10)
    assert result is None

    # Test when page is beyond the last page
    result = PaginatedResponse.get_next_page(total=100, page_size=10, page=11)
    assert result is None


@pytest.mark.asyncio
async def test_paginated_response_get_prev_page():
    """Test get_prev_page in various scenarios"""
    # Test when there is a previous page
    result = PaginatedResponse.get_prev_page(page=5)
    assert result == 4

    # Test when page is 1
    result = PaginatedResponse.get_prev_page(page=1)
    assert result is None

    # Test when page is 0 or negative
    result = PaginatedResponse.get_prev_page(page=0)
    assert result is None


@pytest.mark.asyncio
async def test_paginated_response_get_last_page_zero_total():
    """Test get_last_page with zero total items"""
    result = PaginatedResponse.get_last_page(total=0, page_size=10)
    assert result == 1  # Should return max(1, 0) = 1


@pytest.mark.asyncio
async def test_sort_params_invalid_order_validation():
    """Test sort_order validation with invalid values"""
    # This should be caught by the _validate_sort method, not Pydantic's Literal validation
    # We need to test the internal validation logic
    from crypticorn_utils.pagination import SortParams

    # Create a SortParams instance and manually call _validate_sort
    params = SortParams[Item]()
    params.sort_by = "name"
    params.sort_order = "invalid_order"  # type: ignore[assignment]
    # This will pass Pydantic validation but fail internal validation

    with pytest.raises(
        ValueError,
        match="Invalid order: 'invalid_order' — must be one of: \\['asc', 'desc'\\]",
    ):
        params._validate_sort()


@pytest.mark.asyncio
async def test_enforce_field_type_none_annotation():
    """Test _enforce_field_type when expected_type is None"""
    from crypticorn_utils.pagination import _enforce_field_type
    from unittest.mock import MagicMock

    # Create a mock model with a field that has None annotation
    mock_model = MagicMock()
    mock_model.model_fields = {"test_field": MagicMock()}
    mock_model.model_fields["test_field"].annotation = None

    # Test that it returns the value as-is when annotation is None
    result = _enforce_field_type(mock_model, "test_field", "some_value")
    assert result == "some_value"
