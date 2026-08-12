"""Tests for the AI recommendation service's response validation.

These test the defensive parsing logic (_validate_response) directly with crafted
dicts — no real LLM call — since that logic must hold up against whatever a model
might return, including malformed or incomplete shapes. See test_ai_route.py for
the endpoint wiring (with the AI call mocked) and README for how to manually verify
against the real provider.
"""
import pytest

from app.services.ai_service import AIServiceError
from app.services.recommendation_service import _validate_response

VALID_RESPONSE = {
    "section_scores": {
        "summary": {"score": 8, "strengths": ["Clear"], "problems": [], "recommendations": []},
        "skills": {"score": 9, "strengths": ["Broad"], "problems": [], "recommendations": ["Add cloud"]},
    },
    "strengths": ["Strong technical skills"],
    "weaknesses": ["Limited leadership experience"],
    "priority_improvements": ["Add measurable results"],
    "recommended_roles": [
        {"role": "Backend Developer", "match_percentage": 85, "reason": "Strong Python/API experience"},
    ],
}


def test_validate_response_accepts_well_formed_data():
    result = _validate_response(VALID_RESPONSE)
    assert result["section_scores"]["summary"]["score"] == 8
    assert result["strengths"] == ["Strong technical skills"]
    assert result["recommended_roles"][0]["role"] == "Backend Developer"


def test_validate_response_clamps_out_of_range_scores():
    data = {
        **VALID_RESPONSE,
        "section_scores": {
            "summary": {"score": 15, "strengths": [], "problems": [], "recommendations": []},
        },
    }
    result = _validate_response(data)
    assert result["section_scores"]["summary"]["score"] == 10


def test_validate_response_clamps_out_of_range_match_percentage():
    data = {
        **VALID_RESPONSE,
        "recommended_roles": [{"role": "X", "match_percentage": 150, "reason": "y"}],
    }
    result = _validate_response(data)
    assert result["recommended_roles"][0]["match_percentage"] == 100


def test_validate_response_rejects_missing_top_level_keys():
    with pytest.raises(AIServiceError):
        _validate_response({"strengths": []})


def test_validate_response_rejects_non_dict_input():
    with pytest.raises(AIServiceError):
        _validate_response("not a dict")


def test_validate_response_rejects_non_dict_section_scores():
    data = {**VALID_RESPONSE, "section_scores": "not a dict"}
    with pytest.raises(AIServiceError):
        _validate_response(data)


def test_validate_response_skips_malformed_recommended_role_entries():
    data = {
        **VALID_RESPONSE,
        "recommended_roles": [
            {"role": "Valid Role", "match_percentage": 70, "reason": "ok"},
            {"role": "Missing percentage"},  # dropped
            "not even a dict",  # dropped
        ],
    }
    result = _validate_response(data)
    assert len(result["recommended_roles"]) == 1
    assert result["recommended_roles"][0]["role"] == "Valid Role"


def test_validate_response_ignores_non_string_items_in_lists():
    data = {**VALID_RESPONSE, "strengths": ["ok", 123, None, "also ok"]}
    result = _validate_response(data)
    assert result["strengths"] == ["ok", "also ok"]


def test_validate_response_only_includes_known_section_keys():
    data = {
        **VALID_RESPONSE,
        "section_scores": {
            "summary": {"score": 5, "strengths": [], "problems": [], "recommendations": []},
            "not_a_real_section": {"score": 10, "strengths": [], "problems": [], "recommendations": []},
        },
    }
    result = _validate_response(data)
    assert "summary" in result["section_scores"]
    assert "not_a_real_section" not in result["section_scores"]
