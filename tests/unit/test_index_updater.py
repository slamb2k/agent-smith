"""Tests for INDEX.md updater utility."""
import tempfile
import json
from pathlib import Path
from datetime import datetime
import pytest
from scripts.core.index_updater import IndexUpdater, IndexEntry


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


def test_index_updater_initialization(temp_dir):
    """Test IndexUpdater initialization."""
    updater = IndexUpdater(directory=temp_dir)
    assert updater.directory == temp_dir
    assert updater.index_file == temp_dir / "INDEX.md"


def test_create_index_entry():
    """Test creating an index entry."""
    entry = IndexEntry(
        filename="test.json",
        description="Test file",
        tags=["test", "data"]
    )

    assert entry.filename == "test.json"
    assert entry.description == "Test file"
    assert "test" in entry.tags


def test_add_entry_creates_index_file(temp_dir):
    """Test that adding entry creates INDEX.md if missing."""
    updater = IndexUpdater(directory=temp_dir)

    entry = IndexEntry(
        filename="data.json",
        description="Test data file"
    )

    updater.add_entry(entry)

    assert updater.index_file.exists()


def test_add_entry_updates_existing_index(temp_dir):
    """Test that adding entry updates existing INDEX.md."""
    updater = IndexUpdater(directory=temp_dir)

    # Add first entry
    entry1 = IndexEntry(filename="file1.json", description="First file")
    updater.add_entry(entry1)

    # Add second entry
    entry2 = IndexEntry(filename="file2.json", description="Second file")
    updater.add_entry(entry2)

    content = updater.index_file.read_text()
    assert "file1.json" in content
    assert "file2.json" in content


def test_remove_entry_removes_from_index(temp_dir):
    """Test removing entry from INDEX.md."""
    updater = IndexUpdater(directory=temp_dir)

    entry = IndexEntry(filename="temp.json", description="Temporary")
    updater.add_entry(entry)

    updater.remove_entry("temp.json")

    content = updater.index_file.read_text()
    assert "temp.json" not in content


def test_scan_directory_discovers_files(temp_dir):
    """Test scanning directory and auto-generating index."""
    # Create some test files
    (temp_dir / "file1.json").write_text('{"test": 1}')
    (temp_dir / "file2.txt").write_text("Test content")
    (temp_dir / "subdir").mkdir()

    updater = IndexUpdater(directory=temp_dir)
    entries = updater.scan_directory()

    # Should find 2 files (not subdirectories)
    filenames = [e.filename for e in entries]
    assert "file1.json" in filenames
    assert "file2.txt" in filenames
    assert len(filenames) == 2
