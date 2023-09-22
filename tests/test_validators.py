import datetime

import pytest
import repackage

repackage.up()
from src.utilities.validators import Google, NewsHandlerValidator, stringify_date_param


def test_is_valid_bucket_name_valid():
    bucket_name = r"cdr56-7uj_h"
    assert Google.is_valid_bucket_name(bucket_name) is True


def test_is_valid_bucket_name_too_short():
    bucket_name = r"cd"
    assert Google.is_valid_bucket_name(bucket_name) is False


def test_is_valid_bucket_name_too_long():
    bucket_name = r"cdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_hcdr56-7uj_h"
    assert Google.is_valid_bucket_name(bucket_name) is False


def test_is_valid_bucket_name_invalid_strings():
    bucket_name = r"go0gle"
    assert Google.is_valid_bucket_name(bucket_name) is False


def test_is_valid_uri_valid():
    uri = r"gs://this-is-a-sample/uri"
    assert Google.is_valid_uri(uri) is True


def test_is_valid_uri_invalid():
    uri = r"this-is-a-sample/uri"
    assert Google.is_valid_uri(uri) is False


def test_is_valid_string_string():
    var = "string"
    assert NewsHandlerValidator.is_valid_string(var) is True


def test_is_valid_string_number():
    var = 111
    assert NewsHandlerValidator.is_valid_string(var) is False


def test_is_valid_string_bool():
    var = True
    assert NewsHandlerValidator.is_valid_string(var) is False


def test_validate_date_str_valid():
    datestr = "2023-01-01"
    assert NewsHandlerValidator.validate_date_str(datestr) is None


def test_validate_date_str_invalid():
    datestr = "01-01-2023"
    with pytest.raises(ValueError, match="Date input should be in format of YYYY-MM-DD"):
        NewsHandlerValidator.validate_date_str(datestr)


def test_validate_datetime_str_valid():
    datetimestr = "2023-01-01T23:23:23"
    assert NewsHandlerValidator.validate_datetime_str(datetimestr) is None


def test_validate_datetime_str_invalid():
    datetimestr = "01-01-2023"
    with pytest.raises(
        ValueError, match="Datetime input should be in format of YYYY-MM-DDTHH:MM:SS"
    ):
        NewsHandlerValidator.validate_datetime_str(datetimestr)


def test_is_valid_num_float():
    var = 1.1
    assert NewsHandlerValidator.is_valid_num(var) is True


def test_is_valid_num_int():
    var = 11
    assert NewsHandlerValidator.is_valid_num(var) is True


def test_is_valid_num_bool():
    var = True
    assert NewsHandlerValidator.is_valid_num(var) is False


def test_is_valid_num_string():
    var = "str"
    assert NewsHandlerValidator.is_valid_num(var) is False


def test_stringify_date_param_string_date():
    var = "2023-01-01"
    assert stringify_date_param(var) == "2023-01-01"


def test_stringify_date_param_string_datetime():
    var = "2023-01-01T23:23:23"
    assert stringify_date_param(var) == "2023-01-01T23:23:23"


def test_stringify_date_param_string_error():
    var = "string"
    with pytest.raises(
        ValueError,
        match="Date input should be in format of either YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS",
    ):
        stringify_date_param(var)


def test_stringify_date_param_date():
    var = datetime.date(2023, 1, 1)
    assert stringify_date_param(var) == "2023-01-01"


def test_stringify_date_param_datetime():
    var = datetime.datetime(2023, 1, 1, 23, 23, 23)
    assert stringify_date_param(var) == "2023-01-01T23:23:23"


def test_stringify_date_param_num():
    var = datetime.datetime.fromtimestamp(1672611803.0)
    assert stringify_date_param(var) == "2023-01-01T23:23:23"


def test_stringify_date_param_error():
    var = ("string",)
    with pytest.raises(
        TypeError,
        match="Date input must be one of: str, date, datetime, float, int, or None",
    ):
        stringify_date_param(var)
