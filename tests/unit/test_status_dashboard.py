"""Tests for the status dashboard script."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestGetStatusSummary:
    """Tests for get_status_summary function."""

    @patch("scripts.status.dashboard._get_client")
    def test_returns_required_fields(self, mock_get_client):
        """Status summary should include all required fields."""
        from scripts.status.dashboard import get_status_summary

        # Setup mock
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_user.return_value = {"id": 12345}
        mock_client.get_transactions.return_value = []

        status = get_status_summary()

        assert "health_score" in status
        assert "uncategorized_count" in status
        assert "conflict_count" in status
        assert "tax_alerts" in status
        assert "suggestions" in status

    @patch("scripts.status.dashboard._get_client")
    def test_counts_uncategorized_transactions(self, mock_get_client):
        """Should correctly count transactions without category."""
        from scripts.status.dashboard import get_status_summary

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_user.return_value = {"id": 12345}
        mock_client.get_transactions.return_value = [
            {"id": 1, "category": None},
            {"id": 2, "category": None},
            {"id": 3, "category": {"id": 100, "title": "Food"}},
        ]

        status = get_status_summary()

        assert status["uncategorized_count"] == 2

    @patch("scripts.status.dashboard._get_client")
    def test_counts_conflict_transactions(self, mock_get_client):
        """Should count transactions with Review labels as conflicts."""
        from scripts.status.dashboard import get_status_summary

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_user.return_value = {"id": 12345}
        mock_client.get_transactions.return_value = [
            {"id": 1, "labels": ["Review: Category Conflict"]},
            {"id": 2, "labels": ["Review: Generic PayPal"]},
            {"id": 3, "labels": ["Tax Deductible"]},
            {"id": 4, "labels": None},
        ]

        status = get_status_summary()

        assert status["conflict_count"] == 2


class TestCheckTaxDeadlines:
    """Tests for _check_tax_deadlines function."""

    def test_alerts_when_eofy_within_180_days(self):
        """Should alert when EOFY is within 180 days."""
        from scripts.status.dashboard import _check_tax_deadlines

        alerts = _check_tax_deadlines()

        # Calculate expected days to EOFY
        today = datetime.now()
        eofy = datetime(today.year if today.month <= 6 else today.year + 1, 6, 30)
        days_to_eofy = (eofy - today).days

        if days_to_eofy <= 180:
            assert len(alerts) >= 1
            assert alerts[0]["type"] == "eofy"
            assert "EOFY" in alerts[0]["message"]
        else:
            assert len(alerts) == 0


class TestGenerateSuggestions:
    """Tests for _generate_suggestions function."""

    def test_suggests_categorization_when_uncategorized(self):
        """Should suggest categorization when uncategorized transactions exist."""
        from scripts.status.dashboard import _generate_suggestions

        suggestions = _generate_suggestions(
            uncategorized_count=5,
            conflict_count=0,
            health_score={"score": 80, "status": "Good"},
            tax_alerts=[],
        )

        assert len(suggestions) >= 1
        assert suggestions[0]["command"] == "/smith:categorize"
        assert "5" in suggestions[0]["title"]

    def test_suggests_review_when_conflicts(self):
        """Should suggest review when conflicts exist."""
        from scripts.status.dashboard import _generate_suggestions

        suggestions = _generate_suggestions(
            uncategorized_count=0,
            conflict_count=3,
            health_score={"score": 80, "status": "Good"},
            tax_alerts=[],
        )

        assert any(s["command"] == "/smith:review-conflicts" for s in suggestions)

    def test_suggests_health_check_when_not_run(self):
        """Should suggest health check when score is unknown."""
        from scripts.status.dashboard import _generate_suggestions

        suggestions = _generate_suggestions(
            uncategorized_count=0,
            conflict_count=0,
            health_score={"score": None, "status": "unknown"},
            tax_alerts=[],
        )

        assert any(s["command"] == "/smith:health" for s in suggestions)

    def test_limits_suggestions_to_three(self):
        """Should return at most 3 suggestions."""
        from scripts.status.dashboard import _generate_suggestions

        suggestions = _generate_suggestions(
            uncategorized_count=10,
            conflict_count=5,
            health_score={"score": None, "status": "unknown"},
            tax_alerts=[{"type": "eofy", "message": "EOFY soon", "priority": "high"}],
        )

        assert len(suggestions) <= 3


class TestPrintFormatted:
    """Tests for _print_formatted function."""

    def test_prints_header(self, capsys):
        """Should print Agent Smith header."""
        from scripts.status.dashboard import _print_formatted

        status = {
            "health_score": {"score": 85, "status": "Good"},
            "uncategorized_count": 0,
            "uncategorized_days": 7,
            "conflict_count": 0,
            "tax_alerts": [],
            "suggestions": [],
            "last_activity": {"action": None, "date": None},
        }

        _print_formatted(status)
        captured = capsys.readouterr()

        assert "AGENT SMITH" in captured.out
        assert "Financial Intelligence" in captured.out

    def test_shows_health_score_with_emoji(self, capsys):
        """Should show health score with appropriate emoji."""
        from scripts.status.dashboard import _print_formatted

        status = {
            "health_score": {"score": 85, "status": "Good"},
            "uncategorized_count": 0,
            "uncategorized_days": 7,
            "conflict_count": 0,
            "tax_alerts": [],
            "suggestions": [],
            "last_activity": {"action": None, "date": None},
        }

        _print_formatted(status)
        captured = capsys.readouterr()

        assert "85/100" in captured.out

    def test_shows_suggestions(self, capsys):
        """Should show suggested next steps."""
        from scripts.status.dashboard import _print_formatted

        status = {
            "health_score": {"score": None, "status": "unknown"},
            "uncategorized_count": 5,
            "uncategorized_days": 7,
            "conflict_count": 0,
            "tax_alerts": [],
            "suggestions": [
                {
                    "priority": 1,
                    "title": "Categorize 5 new transactions",
                    "natural": "categorize my transactions",
                    "command": "/smith:categorize",
                }
            ],
            "last_activity": {"action": None, "date": None},
        }

        _print_formatted(status)
        captured = capsys.readouterr()

        assert "SUGGESTED NEXT STEPS" in captured.out
        assert "Categorize 5" in captured.out
        assert "/smith:categorize" in captured.out


class TestMain:
    """Tests for main function."""

    @patch("scripts.status.dashboard.get_status_summary")
    def test_json_output_mode(self, mock_get_status, capsys):
        """Should output valid JSON in json mode."""
        from scripts.status.dashboard import main

        mock_get_status.return_value = {
            "health_score": {"score": 80, "status": "Good"},
            "uncategorized_count": 0,
            "conflict_count": 0,
            "tax_alerts": [],
            "suggestions": [],
        }

        with patch("sys.argv", ["dashboard.py", "--output", "json"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert "health_score" in parsed

    @patch("scripts.status.dashboard.get_status_summary")
    def test_formatted_output_mode(self, mock_get_status, capsys):
        """Should output formatted text in formatted mode."""
        from scripts.status.dashboard import main

        mock_get_status.return_value = {
            "health_score": {"score": 80, "status": "Good"},
            "uncategorized_count": 0,
            "uncategorized_days": 7,
            "conflict_count": 0,
            "tax_alerts": [],
            "suggestions": [],
            "last_activity": {"action": None, "date": None},
        }

        with patch("sys.argv", ["dashboard.py", "--output", "formatted"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "AGENT SMITH" in captured.out
