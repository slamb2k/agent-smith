"""Tests for onboarding state tracking."""

import json
from pathlib import Path
from scripts.onboarding.state import OnboardingState, OnboardingStage


def test_onboarding_state_creation():
    """Test OnboardingState initialization."""
    state = OnboardingState()

    assert state.current_stage == OnboardingStage.NOT_STARTED
    assert state.completed_stages == []
    assert state.discovery_report is None
    assert state.template_selected is None


def test_onboarding_state_advance_stage():
    """Test advancing to next stage."""
    state = OnboardingState()

    state.advance_stage(OnboardingStage.DISCOVERY)
    assert state.current_stage == OnboardingStage.DISCOVERY
    assert OnboardingStage.NOT_STARTED in state.completed_stages

    state.advance_stage(OnboardingStage.TEMPLATE_SELECTION)
    assert state.current_stage == OnboardingStage.TEMPLATE_SELECTION
    assert OnboardingStage.DISCOVERY in state.completed_stages


def test_onboarding_state_save_load(tmp_path):
    """Test saving and loading state."""
    state_file = tmp_path / "onboarding_state.json"

    # Create and save state
    state = OnboardingState(state_file=state_file)
    state.advance_stage(OnboardingStage.DISCOVERY)
    state.discovery_report = {"user_id": 12345, "recommendation": "simple"}
    state.save()

    # Load state
    loaded_state = OnboardingState(state_file=state_file)
    loaded_state.load()

    assert loaded_state.current_stage == OnboardingStage.DISCOVERY
    assert loaded_state.discovery_report["user_id"] == 12345
    assert OnboardingStage.NOT_STARTED in loaded_state.completed_stages
