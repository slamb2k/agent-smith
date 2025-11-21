"""Audit trail for activity logging and undo capability."""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import uuid


class AuditAction(Enum):
    """Types of auditable actions."""

    TRANSACTION_MODIFY = "transaction_modify"
    TRANSACTION_DELETE = "transaction_delete"
    CATEGORY_CREATE = "category_create"
    CATEGORY_MODIFY = "category_modify"
    CATEGORY_DELETE = "category_delete"
    RULE_CREATE = "rule_create"
    RULE_MODIFY = "rule_modify"
    RULE_DELETE = "rule_delete"
    BULK_OPERATION = "bulk_operation"
    REPORT_GENERATE = "report_generate"


@dataclass
class AuditEntry:
    """Represents a single audit log entry."""

    entry_id: str
    action: AuditAction
    timestamp: datetime
    user_id: str
    description: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    affected_ids: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage.

        Returns:
            Dictionary representation
        """
        return {
            "entry_id": self.entry_id,
            "action": self.action.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "description": self.description,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "affected_ids": self.affected_ids,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        """Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            AuditEntry instance
        """
        return cls(
            entry_id=data["entry_id"],
            action=AuditAction(data["action"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_id=data["user_id"],
            description=data["description"],
            before_state=data.get("before_state"),
            after_state=data.get("after_state"),
            affected_ids=data.get("affected_ids"),
            metadata=data.get("metadata"),
        )


class AuditLogger:
    """Manages audit trail logging and queries."""

    def __init__(self, user_id: str):
        """Initialize audit logger for a user.

        Args:
            user_id: User ID for audit entries
        """
        self.user_id = user_id
        self.entries: List[AuditEntry] = []

    def log_action(
        self,
        action: AuditAction,
        description: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        affected_ids: Optional[List[int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """Log an auditable action.

        Args:
            action: Type of action
            description: Human-readable description
            before_state: State before action
            after_state: State after action
            affected_ids: IDs of affected resources
            metadata: Additional metadata

        Returns:
            Created AuditEntry
        """
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            action=action,
            timestamp=datetime.now(),
            user_id=self.user_id,
            description=description,
            before_state=before_state,
            after_state=after_state,
            affected_ids=affected_ids,
            metadata=metadata,
        )

        self.entries.append(entry)
        return entry

    def get_entries(
        self,
        action: Optional[AuditAction] = None,
        affected_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[AuditEntry]:
        """Get audit entries with optional filtering.

        Args:
            action: Filter by action type
            affected_id: Filter by affected resource ID
            start_date: Filter by start timestamp
            end_date: Filter by end timestamp

        Returns:
            List of matching AuditEntry objects
        """
        results = self.entries

        if action:
            results = [e for e in results if e.action == action]

        if affected_id is not None:
            results = [e for e in results if e.affected_ids and affected_id in e.affected_ids]

        if start_date:
            results = [e for e in results if e.timestamp >= start_date]

        if end_date:
            results = [e for e in results if e.timestamp <= end_date]

        # Sort by timestamp (newest first)
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results

    def can_undo(self, entry_id: str) -> bool:
        """Check if an action can be undone.

        Args:
            entry_id: Audit entry ID

        Returns:
            True if action has before_state for undo
        """
        entry = next((e for e in self.entries if e.entry_id == entry_id), None)
        if not entry:
            return False

        return entry.before_state is not None
