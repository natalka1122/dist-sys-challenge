from typing import Any, cast

from const import DictWithStrKeys
from exceptions import BadMessageError


def get_str(raw_json: dict[Any, Any], key: str) -> str:
    result = raw_json.get(key)
    if not isinstance(result, str):
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} raw_json = {raw_json}")
    return result


def get_int_or_none(raw_json: dict[Any, Any], key: str) -> int | None:
    result = raw_json.get(key)
    if result is not None and not isinstance(result, int):
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} raw_json = {raw_json}")
    return result


def get_int(raw_json: dict[Any, Any], key: str) -> int:
    result = raw_json.get(key)
    if not isinstance(result, int):
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} raw_json = {raw_json}")
    return result


def get_dict_with_str_keys(raw_json: dict[Any, Any], key: str) -> DictWithStrKeys:
    result = raw_json.get(key)
    if not isinstance(result, dict):
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} result = {raw_json}")
    result = cast(DictWithStrKeys, result)
    if not all(isinstance(k, str) for k in result):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} result = {raw_json}")
    return result


def get_list_with_int(raw_json: dict[Any, Any], key: str) -> list[int]:
    result = raw_json.get(key)
    if not isinstance(result, list):
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} result = {raw_json}")
    result = cast(list[int], result)
    if not all(isinstance(k, int) for k in result):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} result = {raw_json}")
    return result
