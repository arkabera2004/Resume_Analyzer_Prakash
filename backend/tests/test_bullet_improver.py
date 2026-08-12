"""Tests for the AI bullet-improver's response validation.

Like test_recommendation_service.py, these exercise _validate_response with
crafted dicts — no real LLM call. See README for manual live-provider verification.
"""
import pytest

from app.services.ai_service import AIServiceError
from app.services.bullet_improver import _validate_response

ORIGINAL = "Created an e-commerce website using React."


def test_validate_response_accepts_well_formed_data():
    data = {
        "improved": "Developed a responsive e-commerce platform using React.",
        "why_better": ["Stronger action verb", "More technical detail"],
    }
    result = _validate_response(data, original=ORIGINAL)
    assert result["original"] == ORIGINAL
    assert result["improved"] == "Developed a responsive e-commerce platform using React."
    assert result["why_better"] == ["Stronger action verb", "More technical detail"]


def test_validate_response_rejects_missing_improved_key():
    with pytest.raises(AIServiceError):
        _validate_response({"why_better": ["ok"]}, original=ORIGINAL)


def test_validate_response_rejects_missing_why_better_key():
    with pytest.raises(AIServiceError):
        _validate_response({"improved": "x"}, original=ORIGINAL)


def test_validate_response_rejects_non_dict_input():
    with pytest.raises(AIServiceError):
        _validate_response("not a dict", original=ORIGINAL)


def test_validate_response_rejects_empty_improved_text():
    with pytest.raises(AIServiceError):
        _validate_response({"improved": "   ", "why_better": []}, original=ORIGINAL)


def test_validate_response_rejects_non_string_improved():
    with pytest.raises(AIServiceError):
        _validate_response({"improved": 123, "why_better": []}, original=ORIGINAL)


def test_validate_response_ignores_non_string_why_better_items():
    data = {"improved": "Better bullet.", "why_better": ["ok", 42, None, "also ok"]}
    result = _validate_response(data, original=ORIGINAL)
    assert result["why_better"] == ["ok", "also ok"]


def test_validate_response_strips_whitespace_from_improved():
    data = {"improved": "  Better bullet.  ", "why_better": []}
    result = _validate_response(data, original=ORIGINAL)
    assert result["improved"] == "Better bullet."
