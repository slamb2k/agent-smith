"""Backup and restore utilities for Agent Smith."""
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


logger = logging.getLogger(__name__)


class BackupManager:
    """Manages backups of PocketSmith data before mutations.

    Features:
    - Timestamped backup directories
    - Metadata tracking
    - List and restore operations
    - Automatic cleanup based on retention policy
    """

    def __init__(self, backup_root: Optional[Path] = None):
        """Initialize BackupManager.

        Args:
            backup_root: Root directory for backups.
                        Defaults to ./backups relative to project root.
        """
        if backup_root is None:
            # Default to ./backups in project root
            project_root = Path(__file__).parent.parent.parent
            backup_root = project_root / "backups"

        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)

        logger.info(f"BackupManager initialized (root: {self.backup_root})")

    def create_backup(
        self,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Create a new timestamped backup directory.

        Args:
            description: Human-readable backup description
            metadata: Additional metadata to store

        Returns:
            Path to created backup directory
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_path = self.backup_root / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)

        # Create metadata file
        metadata_dict = metadata or {}
        metadata_dict.update({
            "timestamp": timestamp,
            "description": description,
            "created_at": datetime.now().isoformat()
        })

        metadata_file = backup_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)

        logger.info(f"Created backup: {backup_path} - {description}")
        return backup_path

    def save_backup_data(
        self,
        backup_path: Path,
        filename: str,
        data: Any
    ):
        """Save data to backup directory.

        Args:
            backup_path: Backup directory path
            filename: Filename to save
            data: Data to save (will be JSON serialized)
        """
        filepath = backup_path / filename

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.debug(f"Saved backup data: {filepath}")

    def list_backups(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all backups sorted by timestamp (newest first).

        Args:
            limit: Maximum number of backups to return

        Returns:
            List of backup info dictionaries
        """
        backups = []

        for backup_dir in self.backup_root.iterdir():
            if not backup_dir.is_dir():
                continue

            metadata_file = backup_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            with open(metadata_file) as f:
                metadata = json.load(f)

            backups.append({
                "path": backup_dir,
                "timestamp": metadata.get("timestamp"),
                "description": metadata.get("description"),
                "metadata": metadata
            })

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)

        if limit:
            backups = backups[:limit]

        logger.debug(f"Listed {len(backups)} backups")
        return backups

    def restore_backup(self, backup_path: Path, target_dir: Path):
        """Restore a backup to target directory.

        Args:
            backup_path: Backup directory to restore from
            target_dir: Target directory to restore to
        """
        logger.warning(f"Restoring backup from {backup_path} to {target_dir}")

        # Copy all files except metadata.json
        for item in backup_path.iterdir():
            if item.name == "metadata.json":
                continue

            target_path = target_dir / item.name
            if item.is_file():
                shutil.copy2(item, target_path)
            elif item.is_dir():
                shutil.copytree(item, target_path, dirs_exist_ok=True)

        logger.info(f"Backup restored successfully")

    def delete_backup(self, backup_path: Path):
        """Delete a backup directory.

        Args:
            backup_path: Backup directory to delete
        """
        if not backup_path.exists():
            logger.warning(f"Backup does not exist: {backup_path}")
            return

        shutil.rmtree(backup_path)
        logger.info(f"Deleted backup: {backup_path}")
