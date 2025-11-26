"""Tests for the welcome screen script (local-only status checks)."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest


class TestCheckApiKey:
    """Tests for check_api_key function."""

    def test_returns_false_when_env_missing(self, tmp_path):
        """Should return present=False when .env doesn't exist."""
        from scripts.status.welcome import check_api_key

        with patch("scripts.status.welcome.get_env_path") as mock_path:
            mock_path.return_value = tmp_path / ".env"

            result = check_api_key()

            assert result["present"] is False
            assert result["valid_format"] is False

    def test_returns_false_when_key_is_placeholder(self, tmp_path):
        """Should return present=False when key is a placeholder."""
        from scripts.status.welcome import check_api_key

        env_file = tmp_path / ".env"
        env_file.write_text("POCKETSMITH_API_KEY=<Your Developer API Key>")

        with patch("scripts.status.welcome.get_env_path") as mock_path:
            mock_path.return_value = env_file

            result = check_api_key()

            assert result["present"] is False

    def test_returns_valid_for_128_char_hex(self, tmp_path):
        """Should return valid_format=True for 128-char hex string."""
        from scripts.status.welcome import check_api_key

        env_file = tmp_path / ".env"
        valid_key = "a" * 128
        env_file.write_text(f"POCKETSMITH_API_KEY={valid_key}")

        with patch("scripts.status.welcome.get_env_path") as mock_path:
            mock_path.return_value = env_file

            result = check_api_key()

            assert result["present"] is True
            assert result["valid_format"] is True

    def test_returns_invalid_for_short_key(self, tmp_path):
        """Should return valid_format=False for non-128-char key."""
        from scripts.status.welcome import check_api_key

        env_file = tmp_path / ".env"
        env_file.write_text("POCKETSMITH_API_KEY=short_key")

        with patch("scripts.status.welcome.get_env_path") as mock_path:
            mock_path.return_value = env_file

            result = check_api_key()

            assert result["present"] is True
            assert result["valid_format"] is False


class TestCheckOnboarding:
    """Tests for check_onboarding function."""

    def test_returns_not_started_when_data_dir_missing(self, tmp_path):
        """Should return not_started when data/ doesn't exist."""
        from scripts.status.welcome import check_onboarding

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = tmp_path / "data"

            result = check_onboarding()

            assert result["status"] == "not_started"
            assert result["current_stage"] is None

    def test_returns_not_started_when_state_file_missing(self, tmp_path):
        """Should return not_started when onboarding_state.json doesn't exist."""
        from scripts.status.welcome import check_onboarding

        data_dir = tmp_path / "data"
        data_dir.mkdir()

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = data_dir

            result = check_onboarding()

            assert result["status"] == "not_started"

    def test_returns_complete_when_onboarding_completed(self, tmp_path):
        """Should return complete when onboarding_completed is true."""
        from scripts.status.welcome import check_onboarding

        data_dir = tmp_path / "data"
        data_dir.mkdir()
        state_file = data_dir / "onboarding_state.json"
        state_file.write_text(json.dumps({"onboarding_completed": True}))

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = data_dir

            result = check_onboarding()

            assert result["status"] == "complete"

    def test_returns_in_progress_with_stage(self, tmp_path):
        """Should return in_progress with current stage info."""
        from scripts.status.welcome import check_onboarding

        data_dir = tmp_path / "data"
        data_dir.mkdir()
        state_file = data_dir / "onboarding_state.json"
        state_file.write_text(
            json.dumps(
                {
                    "onboarding_completed": False,
                    "current_stage": 3,
                }
            )
        )

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = data_dir

            result = check_onboarding()

            assert result["status"] == "in_progress"
            assert result["current_stage"] == 3
            assert result["stage_name"] == "Template Selection"


class TestCheckRules:
    """Tests for check_rules function."""

    def test_returns_zero_when_file_missing(self, tmp_path):
        """Should return count=0 when rules.yaml doesn't exist."""
        from scripts.status.welcome import check_rules

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = tmp_path / "data"

            result = check_rules()

            assert result["count"] == 0
            assert result["file_exists"] is False

    def test_counts_rules_in_list_format(self, tmp_path):
        """Should count rules when file is a list."""
        from scripts.status.welcome import check_rules

        data_dir = tmp_path / "data"
        data_dir.mkdir()
        rules_file = data_dir / "rules.yaml"
        rules_file.write_text(
            """
- payee: Woolworths
  category: Groceries
- payee: Coles
  category: Groceries
- payee: Shell
  category: Transport
"""
        )

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = data_dir

            result = check_rules()

            assert result["count"] == 3
            assert result["file_exists"] is True

    def test_counts_rules_in_dict_format(self, tmp_path):
        """Should count rules when file has 'rules' key."""
        from scripts.status.welcome import check_rules

        data_dir = tmp_path / "data"
        data_dir.mkdir()
        rules_file = data_dir / "rules.yaml"
        rules_file.write_text(
            """
rules:
  - payee: Woolworths
    category: Groceries
  - payee: Coles
    category: Groceries
"""
        )

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = data_dir

            result = check_rules()

            assert result["count"] == 2


class TestCheckHealthCache:
    """Tests for check_health_cache function."""

    def test_returns_none_when_cache_missing(self, tmp_path):
        """Should return score=None when health_cache.json doesn't exist."""
        from scripts.status.welcome import check_health_cache

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = tmp_path / "data"

            result = check_health_cache()

            assert result["score"] is None
            assert result["days_ago"] is None

    def test_returns_cached_score(self, tmp_path):
        """Should return cached score and calculate days_ago."""
        from scripts.status.welcome import check_health_cache

        data_dir = tmp_path / "data"
        data_dir.mkdir()
        cache_file = data_dir / "health_cache.json"

        # Set timestamp to 3 days ago
        three_days_ago = datetime.now() - timedelta(days=3)
        cache_file.write_text(
            json.dumps(
                {
                    "score": 75,
                    "status": "Good",
                    "timestamp": three_days_ago.isoformat(),
                }
            )
        )

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = data_dir

            result = check_health_cache()

            assert result["score"] == 75
            assert result["status"] == "Good"
            assert result["days_ago"] == 3


class TestCheckLastActivity:
    """Tests for check_last_activity function."""

    def test_returns_none_when_log_missing(self, tmp_path):
        """Should return action=None when activity_log.json doesn't exist."""
        from scripts.status.welcome import check_last_activity

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = tmp_path / "data"

            result = check_last_activity()

            assert result["action"] is None

    def test_returns_last_activity(self, tmp_path):
        """Should return the last logged activity."""
        from scripts.status.welcome import check_last_activity

        data_dir = tmp_path / "data"
        data_dir.mkdir()
        log_file = data_dir / "activity_log.json"

        yesterday = datetime.now() - timedelta(days=1)
        log_file.write_text(
            json.dumps({"action": "First action", "timestamp": "2025-01-01T00:00:00"})
            + "\n"
            + json.dumps(
                {"action": "Categorized 12 transactions", "timestamp": yesterday.isoformat()}
            )
        )

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = data_dir

            result = check_last_activity()

            assert result["action"] == "Categorized 12 transactions"
            assert result["days_ago"] == 1


class TestCheckTemplates:
    """Tests for check_templates function."""

    def test_returns_none_when_config_missing(self, tmp_path):
        """Should return primary=None when no config files exist."""
        from scripts.status.welcome import check_templates

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = tmp_path / "data"

            result = check_templates()

            assert result["primary"] is None
            assert result["living"] == []
            assert result["additional"] == []

    def test_reads_from_template_config(self, tmp_path):
        """Should read templates from template_config.json."""
        from scripts.status.welcome import check_templates

        data_dir = tmp_path / "data"
        data_dir.mkdir()
        config_file = data_dir / "template_config.json"
        config_file.write_text(
            json.dumps(
                {
                    "primary_template": "payg-employee",
                    "living_templates": ["shared-hybrid"],
                    "additional_templates": ["property-investor"],
                }
            )
        )

        with patch("scripts.status.welcome.get_data_dir") as mock_path:
            mock_path.return_value = data_dir

            result = check_templates()

            assert result["primary"] == "payg-employee"
            assert result["living"] == ["shared-hybrid"]
            assert result["additional"] == ["property-investor"]


class TestGetRecommendedActions:
    """Tests for get_recommended_actions function."""

    def test_prioritizes_missing_api_key(self):
        """Should recommend adding API key as highest priority."""
        from scripts.status.welcome import get_recommended_actions

        actions = get_recommended_actions(
            api_key={"present": False, "valid_format": False},
            onboarding={"status": "not_started", "current_stage": None, "stage_name": None},
            rules={"count": 0, "file_exists": False},
            health={"score": None, "status": "unknown", "days_ago": None},
        )

        assert len(actions) >= 1
        assert actions[0]["priority"] == 1
        assert "API key" in actions[0]["message"]

    def test_prioritizes_onboarding_not_started(self):
        """Should recommend install when API key present but onboarding not started."""
        from scripts.status.welcome import get_recommended_actions

        actions = get_recommended_actions(
            api_key={"present": True, "valid_format": True},
            onboarding={"status": "not_started", "current_stage": None, "stage_name": None},
            rules={"count": 0, "file_exists": False},
            health={"score": None, "status": "unknown", "days_ago": None},
        )

        assert any(a["command"] == "/smith:install" for a in actions)

    def test_prioritizes_onboarding_in_progress(self):
        """Should recommend continuing onboarding when in progress."""
        from scripts.status.welcome import get_recommended_actions

        actions = get_recommended_actions(
            api_key={"present": True, "valid_format": True},
            onboarding={
                "status": "in_progress",
                "current_stage": 3,
                "stage_name": "Template Selection",
            },
            rules={"count": 0, "file_exists": False},
            health={"score": None, "status": "unknown", "days_ago": None},
        )

        assert any("Stage 3" in a["message"] for a in actions)

    def test_recommends_health_check_when_never_run(self):
        """Should recommend health check when score is None and onboarding complete."""
        from scripts.status.welcome import get_recommended_actions

        actions = get_recommended_actions(
            api_key={"present": True, "valid_format": True},
            onboarding={"status": "complete", "current_stage": None, "stage_name": None},
            rules={"count": 10, "file_exists": True},
            health={"score": None, "status": "unknown", "days_ago": None},
        )

        assert any(a["command"] == "/smith:health" for a in actions)

    def test_recommends_categorize_when_all_good(self):
        """Should recommend categorize as default action when all good."""
        from scripts.status.welcome import get_recommended_actions

        actions = get_recommended_actions(
            api_key={"present": True, "valid_format": True},
            onboarding={"status": "complete", "current_stage": None, "stage_name": None},
            rules={"count": 10, "file_exists": True},
            health={"score": 85, "status": "Good", "days_ago": 2},
        )

        assert any(a["command"] == "/smith:categorize" for a in actions)

    def test_returns_max_two_actions(self):
        """Should return at most 2 recommended actions."""
        from scripts.status.welcome import get_recommended_actions

        actions = get_recommended_actions(
            api_key={"present": False, "valid_format": False},
            onboarding={"status": "not_started", "current_stage": None, "stage_name": None},
            rules={"count": 0, "file_exists": False},
            health={"score": None, "status": "unknown", "days_ago": None},
        )

        assert len(actions) <= 2


class TestFormatOutput:
    """Tests for format_output function."""

    def test_includes_logo(self):
        """Should include ASCII art logo in output."""
        from scripts.status.welcome import format_output

        status = {
            "api_key": {"present": True, "valid_format": True},
            "onboarding": {"status": "complete", "current_stage": None, "stage_name": None},
            "rules": {"count": 10, "file_exists": True},
            "health": {"score": 85, "status": "Good", "days_ago": 2},
            "activity": {"action": None, "date": None, "days_ago": None},
            "templates": {"primary": "payg-employee", "living": [], "additional": []},
            "recommendations": [
                {"priority": 9, "message": "Process transactions", "command": "/smith:categorize"}
            ],
        }

        output = format_output(status)

        assert "WELCOME TO AGENT SMITH" in output
        assert "Good Morning Mr. Anderson" in output

    def test_shows_api_key_status(self):
        """Should show API key status with appropriate indicator."""
        from scripts.status.welcome import format_output

        status = {
            "api_key": {"present": True, "valid_format": True},
            "onboarding": {"status": "not_started", "current_stage": None, "stage_name": None},
            "rules": {"count": 0, "file_exists": False},
            "health": {"score": None, "status": "unknown", "days_ago": None},
            "activity": {"action": None, "date": None, "days_ago": None},
            "templates": {"primary": None, "living": [], "additional": []},
            "recommendations": [],
        }

        output = format_output(status)

        assert "API Key configured" in output

    def test_shows_health_score(self):
        """Should show health score when available."""
        from scripts.status.welcome import format_output

        status = {
            "api_key": {"present": True, "valid_format": True},
            "onboarding": {"status": "complete", "current_stage": None, "stage_name": None},
            "rules": {"count": 10, "file_exists": True},
            "health": {"score": 75, "status": "Good", "days_ago": 5},
            "activity": {"action": None, "date": None, "days_ago": None},
            "templates": {"primary": "payg-employee", "living": [], "additional": []},
            "recommendations": [],
        }

        output = format_output(status)

        assert "75/100" in output
        assert "5 days ago" in output

    def test_shows_recommendations(self):
        """Should show recommended actions."""
        from scripts.status.welcome import format_output

        status = {
            "api_key": {"present": True, "valid_format": True},
            "onboarding": {"status": "complete", "current_stage": None, "stage_name": None},
            "rules": {"count": 10, "file_exists": True},
            "health": {"score": 85, "status": "Good", "days_ago": 2},
            "activity": {"action": None, "date": None, "days_ago": None},
            "templates": {"primary": "payg-employee", "living": [], "additional": []},
            "recommendations": [
                {"priority": 9, "message": "Process transactions", "command": "/smith:categorize"},
            ],
        }

        output = format_output(status)

        assert "NEXT STEPS" in output
        assert "/smith:categorize" in output


class TestGetStatusSummary:
    """Tests for get_status_summary function."""

    def test_returns_all_required_fields(self, tmp_path):
        """Should return all required status fields."""
        from scripts.status.welcome import get_status_summary

        with patch("scripts.status.welcome.get_data_dir") as mock_data:
            with patch("scripts.status.welcome.get_env_path") as mock_env:
                mock_data.return_value = tmp_path / "data"
                mock_env.return_value = tmp_path / ".env"

                status = get_status_summary()

                assert "api_key" in status
                assert "onboarding" in status
                assert "rules" in status
                assert "health" in status
                assert "activity" in status
                assert "templates" in status
                assert "recommendations" in status


class TestMain:
    """Tests for main function."""

    def test_json_output_mode(self, tmp_path, capsys):
        """Should output valid JSON in json mode."""
        from scripts.status.welcome import main

        with patch("scripts.status.welcome.get_data_dir") as mock_data:
            with patch("scripts.status.welcome.get_env_path") as mock_env:
                with patch("sys.argv", ["welcome.py", "--output", "json"]):
                    mock_data.return_value = tmp_path / "data"
                    mock_env.return_value = tmp_path / ".env"

                    result = main()

                    assert result == 0
                    captured = capsys.readouterr()
                    parsed = json.loads(captured.out)
                    assert "api_key" in parsed

    def test_formatted_output_mode(self, tmp_path, capsys):
        """Should output formatted text in formatted mode."""
        from scripts.status.welcome import main

        with patch("scripts.status.welcome.get_data_dir") as mock_data:
            with patch("scripts.status.welcome.get_env_path") as mock_env:
                with patch("sys.argv", ["welcome.py", "--output", "formatted"]):
                    mock_data.return_value = tmp_path / "data"
                    mock_env.return_value = tmp_path / ".env"

                    result = main()

                    assert result == 0
                    captured = capsys.readouterr()
                    assert "AGENT SMITH" in captured.out
