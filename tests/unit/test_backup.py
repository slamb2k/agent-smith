"""Tests for backup utility."""
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pytest
from scripts.utils.backup import BackupManager


@pytest.fixture
def temp_backup_dir():
    """Create temporary backup directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


def test_backup_manager_initialization(temp_backup_dir):
    """Test BackupManager initialization."""
    manager = BackupManager(backup_root=temp_backup_dir)
    assert manager.backup_root == temp_backup_dir
    assert temp_backup_dir.exists()


def test_create_backup_creates_timestamped_directory(temp_backup_dir):
    """Test that create_backup creates timestamped directory."""
    manager = BackupManager(backup_root=temp_backup_dir)
    backup_path = manager.create_backup(description="test backup")

    assert backup_path.exists()
    assert backup_path.is_dir()
    # Check timestamp format YYYY-MM-DD_HHMMSS
    dir_name = backup_path.name
    assert len(dir_name.split('_')) == 2


def test_backup_saves_data_as_json(temp_backup_dir):
    """Test that backup can save data as JSON."""
    manager = BackupManager(backup_root=temp_backup_dir)

    test_data = {"transactions": [{"id": 1, "amount": "50.00"}]}
    backup_path = manager.create_backup(description="test")

    manager.save_backup_data(
        backup_path=backup_path,
        filename="transactions.json",
        data=test_data
    )

    saved_file = backup_path / "transactions.json"
    assert saved_file.exists()

    with open(saved_file) as f:
        loaded_data = json.load(f)

    assert loaded_data == test_data


def test_backup_creates_metadata_file(temp_backup_dir):
    """Test that backup creates metadata.json."""
    manager = BackupManager(backup_root=temp_backup_dir)
    backup_path = manager.create_backup(
        description="Test backup",
        metadata={"user_id": 217031, "operation": "categorize"}
    )

    metadata_file = backup_path / "metadata.json"
    assert metadata_file.exists()

    with open(metadata_file) as f:
        metadata = json.load(f)

    assert metadata["description"] == "Test backup"
    assert metadata["user_id"] == 217031
    assert "timestamp" in metadata


def test_list_backups_returns_sorted_list(temp_backup_dir):
    """Test list_backups returns backups sorted by timestamp."""
    manager = BackupManager(backup_root=temp_backup_dir)

    # Create multiple backups with sufficient delay to get different timestamps
    import time
    backup1 = manager.create_backup(description="First")
    time.sleep(1.1)  # Sleep more than 1 second to ensure different timestamp
    backup2 = manager.create_backup(description="Second")
    time.sleep(1.1)
    backup3 = manager.create_backup(description="Third")

    backups = manager.list_backups()

    assert len(backups) == 3
    # Should be sorted newest first
    assert backups[0]["path"] == backup3
    assert backups[1]["path"] == backup2
    assert backups[2]["path"] == backup1
    # Verify descriptions are correct
    assert backups[0]["description"] == "Third"
    assert backups[1]["description"] == "Second"
    assert backups[2]["description"] == "First"
