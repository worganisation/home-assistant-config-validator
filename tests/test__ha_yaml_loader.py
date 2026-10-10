"""Regression coverage for entity dependency field names."""

# ruff: noqa: S101

from __future__ import annotations

from typing import cast

import pytest
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from wg_utilities.helpers.processor import JProc

from home_assistant_config_validator.models.config import validation
from home_assistant_config_validator.models.config.validation import (
    _validate_script_consumption_inner,
)
from home_assistant_config_validator.utils.exception import (
    InvalidConfigurationError,
    MissingScriptFieldError,
)
from home_assistant_config_validator.utils.ha_yaml_loader import (
    Entity,
    HAYamlLoader,
    entity_id_check_callback,
)


@pytest.mark.parametrize("mapping_type", [dict, CommentedMap])
def test_mapping_dependency_matches_inline_suppression(
    mapping_type: type[dict[str, object]],
) -> None:
    """Mapping fields retain the key used by inline suppressions."""
    field = cast(
        "CommentedMap",
        HAYamlLoader.load(
            "example: automation.do_something  # hacv disable: InvalidEntityConsumed\n",
        ),
    )
    suppressions = Entity.get_suppressions(field)
    dependencies: set[tuple[str, str]] = set()
    processor = JProc({str: entity_id_check_callback})

    processor.process(mapping_type(field), entity_ids=dependencies)

    assert dependencies == {("example", "automation.do_something")}
    assert all("invalidentityconsumed" in suppressions[key] for key, _ in dependencies)


@pytest.mark.parametrize("sequence_type", [list, CommentedSeq])
def test_sequence_dependency_has_no_field_key(
    sequence_type: type[list[object]],
) -> None:
    """Sequence indices are not treated as suppression field names."""
    dependencies: set[tuple[str, str]] = set()
    processor = JProc({str: entity_id_check_callback})

    processor.process(sequence_type(["automation.do_something"]), entity_ids=dependencies)

    assert dependencies == {("", "automation.do_something")}


@pytest.mark.parametrize("field", ["service", "action"])
def test_script_call_validates_required_fields(
    field: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Both supported script-call keys enforce required fields."""
    monkeypatch.setattr(
        validation,
        "_get_script_fields",
        lambda: {"example": {"message": {"required": True}}},
    )
    issues: list[InvalidConfigurationError] = []

    _validate_script_consumption_inner({field: "script.example"}, issues)

    assert len(issues) == 1
    assert isinstance(issues[0], MissingScriptFieldError)


@pytest.mark.parametrize("field", ["service", "action"])
@pytest.mark.parametrize("indirect", [False, True])
def test_templated_script_data_has_no_static_field_errors(
    field: str,
    *,
    indirect: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Runtime data mappings cannot be checked as literal field names."""
    monkeypatch.setattr(
        validation,
        "_get_script_fields",
        lambda: {"example": {"message": {"required": True}}},
    )
    issues: list[InvalidConfigurationError] = []
    call = (
        {
            field: "script.turn_on",
            "target": {"entity_id": "script.example"},
            "data": {"variables": "{{ notification }}"},
        }
        if indirect
        else {field: "script.example", "data": "{{ notification }}"}
    )

    _validate_script_consumption_inner(call, issues)

    assert issues == []
