"""Onboarding state tracking."""

import json
from pathlib import Path
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from scripts.utils.plugin_paths import get_data_path


class OnboardingStage(Enum):
    """Onboarding workflow stages."""

    NOT_STARTED = "not_started"
    PREREQUISITES = "prerequisites"
    DISCOVERY = "discovery"
    TEMPLATE_SELECTION = "template_selection"
    CUSTOMIZATION = "customization"
    INTELLIGENCE_CONFIG = "intelligence_config"
    CATEGORIZATION = "categorization"
    HEALTH_CHECK = "health_check"
    COMPLETE = "complete"


@dataclass
class OnboardingState:
    """Tracks progress through onboarding workflow."""

    current_stage: OnboardingStage = OnboardingStage.NOT_STARTED
    completed_stages: List[OnboardingStage] = field(default_factory=list)
    discovery_report: Optional[Dict[str, Any]] = None
    template_selected: Optional[str] = None
    intelligence_mode: Optional[str] = None
    tax_level: Optional[str] = None
    baseline_health_score: Optional[int] = None
    current_health_score: Optional[int] = None
    categorization_batches: List[Dict[str, Any]] = field(default_factory=list)
    state_file: Optional[Path] = None

    def __post_init__(self) -> None:
        """Initialize state file path if not provided."""
        if self.state_file is None:
            self.state_file = get_data_path("onboarding_state.json")

    def advance_stage(self, next_stage: OnboardingStage) -> None:
        """Advance to next stage.

        Args:
            next_stage: The stage to advance to
        """
        if self.current_stage not in self.completed_stages:
            self.completed_stages.append(self.current_stage)
        self.current_stage = next_stage

    def save(self) -> None:
        """Save state to JSON file."""
        assert self.state_file is not None, "state_file must be initialized"

        data = {
            "current_stage": self.current_stage.value,
            "completed_stages": [stage.value for stage in self.completed_stages],
            "discovery_report": self.discovery_report,
            "template_selected": self.template_selected,
            "intelligence_mode": self.intelligence_mode,
            "tax_level": self.tax_level,
            "baseline_health_score": self.baseline_health_score,
            "current_health_score": self.current_health_score,
            "categorization_batches": self.categorization_batches,
        }

        # Ensure parent directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Load state from JSON file."""
        assert self.state_file is not None, "state_file must be initialized"

        if not self.state_file.exists():
            return

        with open(self.state_file, "r") as f:
            data = json.load(f)

        self.current_stage = OnboardingStage(data.get("current_stage", "not_started"))
        self.completed_stages = [
            OnboardingStage(stage) for stage in data.get("completed_stages", [])
        ]
        self.discovery_report = data.get("discovery_report")
        self.template_selected = data.get("template_selected")
        self.intelligence_mode = data.get("intelligence_mode")
        self.tax_level = data.get("tax_level")
        self.baseline_health_score = data.get("baseline_health_score")
        self.current_health_score = data.get("current_health_score")
        self.categorization_batches = data.get("categorization_batches", [])

    def reset(self) -> None:
        """Reset onboarding state."""
        assert self.state_file is not None, "state_file must be initialized"

        self.current_stage = OnboardingStage.NOT_STARTED
        self.completed_stages = []
        self.discovery_report = None
        self.template_selected = None
        self.intelligence_mode = None
        self.tax_level = None
        self.baseline_health_score = None
        self.current_health_score = None
        self.categorization_batches = []

        if self.state_file.exists():
            self.state_file.unlink()
