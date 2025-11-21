"""Document and receipt management."""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


class DocumentRequirement(Enum):
    """Requirement level for transaction documentation."""

    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class DocumentStatus(Enum):
    """Status of transaction documentation."""

    MISSING = "missing"
    ATTACHED = "attached"
    VERIFIED = "verified"


@dataclass
class TransactionDocument:
    """Represents documentation status for a transaction."""

    transaction_id: int
    amount: float
    category: str
    requirement: DocumentRequirement
    status: DocumentStatus
    date: datetime
    attachment_url: Optional[str] = None
    attached_at: Optional[datetime] = None
    notes: Optional[str] = None

    def attach_document(self, url: str, notes: Optional[str] = None) -> None:
        """Attach a document to this transaction.

        Args:
            url: URL of the attached document
            notes: Optional notes about the document
        """
        self.attachment_url = url
        self.status = DocumentStatus.ATTACHED
        self.attached_at = datetime.now()
        if notes:
            self.notes = notes


class DocumentManager:
    """Manages transaction documentation requirements."""

    # ATO threshold for substantiation
    ATO_SUBSTANTIATION_THRESHOLD = 300.00

    # Categories that commonly need documentation
    DEDUCTIBLE_CATEGORIES = {
        "Work Expenses",
        "Office Supplies",
        "Professional Development",
        "Business Travel",
        "Home Office",
        "Vehicle Expenses",
    }

    def __init__(self) -> None:
        """Initialize document manager."""
        self.documents: Dict[int, TransactionDocument] = {}

    def determine_requirement(self, amount: float, category: str) -> DocumentRequirement:
        """Determine documentation requirement for a transaction.

        Args:
            amount: Transaction amount
            category: Transaction category

        Returns:
            Required documentation level
        """
        # ATO requires substantiation for work expenses > $300
        if amount > self.ATO_SUBSTANTIATION_THRESHOLD:
            return DocumentRequirement.REQUIRED

        # Recommended for deductible categories > $100
        if category in self.DEDUCTIBLE_CATEGORIES and amount > 100.00:
            return DocumentRequirement.RECOMMENDED

        return DocumentRequirement.OPTIONAL

    def track_transaction(
        self,
        transaction_id: int,
        amount: float,
        category: str,
        date: datetime,
    ) -> TransactionDocument:
        """Start tracking a transaction's documentation status.

        Args:
            transaction_id: PocketSmith transaction ID
            amount: Transaction amount
            category: Transaction category
            date: Transaction date

        Returns:
            Created TransactionDocument
        """
        requirement = self.determine_requirement(amount, category)

        doc = TransactionDocument(
            transaction_id=transaction_id,
            amount=amount,
            category=category,
            requirement=requirement,
            status=DocumentStatus.MISSING,
            date=date,
        )

        self.documents[transaction_id] = doc
        return doc

    def get_missing_documents(self, required_only: bool = True) -> List[TransactionDocument]:
        """Get list of transactions with missing documentation.

        Args:
            required_only: Only return REQUIRED documents

        Returns:
            List of TransactionDocument with MISSING status
        """
        results = [doc for doc in self.documents.values() if doc.status == DocumentStatus.MISSING]

        if required_only:
            results = [doc for doc in results if doc.requirement == DocumentRequirement.REQUIRED]

        # Sort by date (oldest first)
        results.sort(key=lambda d: d.date)
        return results
