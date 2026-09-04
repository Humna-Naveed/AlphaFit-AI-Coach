import pytest

from context import build_context


def test_context_allowlists_fields_and_redacts_secrets():
    result = build_context(
        {
            "user_profile": {"fitness_level": "beginner", "api_key": "hidden"},
            "calorie_prediction": {"predicted_calories": 420},
            "unknown_database_dump": {"password": "hidden"},
        }
    )

    assert "fitness_level" in result
    assert "predicted_calories" in result
    assert "unknown_database_dump" not in result
    assert "hidden" not in result


def test_missing_context_is_explicit():
    assert build_context(None) == "No user-specific context was supplied."
    assert build_context({}) == "No user-specific context was supplied."


def test_context_rejects_unsupported_values():
    with pytest.raises(ValueError, match="cannot be serialized"):
        build_context({"user_profile": {"unsupported": object()}})


def test_context_supports_pose_data_and_redacts_nested_credentials():
    result = build_context(
        {
            "pose_exercise": {
                "exercise": "squat",
                "access_token": "hidden",
            }
        }
    )

    assert '"exercise":"squat"' in result
    assert "hidden" not in result
