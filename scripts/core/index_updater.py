"""INDEX.md file updater for efficient LLM discovery."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


logger = logging.getLogger(__name__)


@dataclass
class IndexEntry:
    """Represents an entry in an INDEX.md file."""

    filename: str
    description: str
    tags: List[str] = field(default_factory=list)
    size: Optional[int] = None
    modified: Optional[str] = None


class IndexUpdater:
    """Manages INDEX.md files for efficient directory discovery.

    INDEX.md files enable LLMs to quickly scan directory contents
    without reading all files. Each entry contains:
    - Filename
    - Description
    - Size
    - Last modified date
    - Tags for categorization
    """

    def __init__(self, directory: Path):
        """Initialize IndexUpdater for a directory.

        Args:
            directory: Directory containing files to index
        """
        self.directory = Path(directory)
        self.index_file = self.directory / "INDEX.md"
        logger.debug(f"IndexUpdater initialized for {directory}")

    def add_entry(self, entry: IndexEntry, auto_detect_metadata: bool = True) -> None:
        """Add or update an entry in INDEX.md.

        Args:
            entry: IndexEntry to add
            auto_detect_metadata: Auto-detect size and modified time
        """
        file_path = self.directory / entry.filename

        # Auto-detect metadata if requested
        if auto_detect_metadata and file_path.exists():
            stat = file_path.stat()
            entry.size = stat.st_size
            entry.modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")

        # Read existing entries
        entries = self._read_index()

        # Remove existing entry with same filename
        entries = [e for e in entries if e.filename != entry.filename]

        # Add new entry
        entries.append(entry)

        # Write updated index
        self._write_index(entries)

        logger.debug(f"Added index entry: {entry.filename}")

    def remove_entry(self, filename: str) -> None:
        """Remove an entry from INDEX.md.

        Args:
            filename: Filename to remove
        """
        entries = self._read_index()
        entries = [e for e in entries if e.filename != filename]
        self._write_index(entries)

        logger.debug(f"Removed index entry: {filename}")

    def scan_directory(self, exclude_patterns: Optional[List[str]] = None) -> List[IndexEntry]:
        """Scan directory and create index entries for all files.

        Args:
            exclude_patterns: Patterns to exclude (e.g., ["*.pyc", "__pycache__"])

        Returns:
            List of discovered entries
        """
        if exclude_patterns is None:
            exclude_patterns = ["INDEX.md", "__pycache__", "*.pyc"]

        entries = []

        for item in self.directory.iterdir():
            # Skip directories
            if item.is_dir():
                continue

            # Skip excluded patterns
            if any(item.match(pattern) for pattern in exclude_patterns):
                continue

            stat = item.stat()
            entry = IndexEntry(
                filename=item.name,
                description=f"{item.suffix} file",
                size=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
            )
            entries.append(entry)

        logger.info(f"Scanned {self.directory}: found {len(entries)} files")
        return entries

    def _read_index(self) -> List[IndexEntry]:
        """Read existing INDEX.md and parse entries.

        Returns:
            List of existing entries
        """
        if not self.index_file.exists():
            return []

        entries = []
        content = self.index_file.read_text()

        # Simple parsing - look for lines starting with "- "
        for line in content.split("\n"):
            if line.startswith("- **"):
                # Extract filename from **filename**
                try:
                    filename = line.split("**")[1]
                    # Try to extract description
                    parts = line.split(" - ", 1)
                    description = parts[1] if len(parts) > 1 else ""
                    description = description.split("(")[0].strip()

                    entries.append(IndexEntry(filename=filename, description=description))
                except (IndexError, ValueError):
                    continue

        return entries

    def _write_index(self, entries: List[IndexEntry]) -> None:
        """Write entries to INDEX.md.

        Args:
            entries: Entries to write
        """
        # Sort entries alphabetically
        entries.sort(key=lambda e: e.filename)

        # Generate markdown content
        lines = [
            f"# {self.directory.name} - Index",
            "",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            "## Files",
            "",
        ]

        for entry in entries:
            line = f"- **{entry.filename}** - {entry.description}"

            metadata = []
            if entry.size:
                # Format size
                if entry.size < 1024:
                    size_str = f"{entry.size}B"
                elif entry.size < 1024 * 1024:
                    size_str = f"{entry.size / 1024:.1f}KB"
                else:
                    size_str = f"{entry.size / (1024 * 1024):.1f}MB"
                metadata.append(size_str)

            if entry.modified:
                metadata.append(entry.modified)

            if entry.tags:
                metadata.append(f"Tags: {', '.join(entry.tags)}")

            if metadata:
                line += f" ({', '.join(metadata)})"

            lines.append(line)

        lines.extend(["", "---", ""])

        # Write to file
        self.index_file.write_text("\n".join(lines))
        logger.debug(f"Wrote {len(entries)} entries to {self.index_file}")
