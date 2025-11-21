import pytest
from datetime import datetime
from scripts.features.documents import (
    DocumentRequirement,
    DocumentStatus,
    TransactionDocument,
    DocumentManager,
)


def test_document_requirement_enum():
    """Test DocumentRequirement enum values."""
    assert DocumentRequirement.REQUIRED in list(DocumentRequirement)
    assert DocumentRequirement.RECOMMENDED in list(DocumentRequirement)
    assert DocumentRequirement.OPTIONAL in list(DocumentRequirement)


def test_document_status_enum():
    """Test DocumentStatus enum values."""
    assert DocumentStatus.MISSING in list(DocumentStatus)
    assert DocumentStatus.ATTACHED in list(DocumentStatus)
    assert DocumentStatus.VERIFIED in list(DocumentStatus)


def test_transaction_document_creation():
    """Test creating a transaction document record."""
    doc = TransactionDocument(
        transaction_id=12345,
        amount=350.00,
        category="Work Expenses",
        requirement=DocumentRequirement.REQUIRED,
        status=DocumentStatus.MISSING,
        date=datetime(2025, 11, 15),
    )

    assert doc.transaction_id == 12345
    assert doc.amount == 350.00
    assert doc.requirement == DocumentRequirement.REQUIRED
    assert doc.status == DocumentStatus.MISSING
    assert doc.attachment_url is None


def test_transaction_document_attach():
    """Test attaching a document to a transaction."""
    doc = TransactionDocument(
        transaction_id=12345,
        amount=350.00,
        category="Work Expenses",
        requirement=DocumentRequirement.REQUIRED,
        status=DocumentStatus.MISSING,
        date=datetime(2025, 11, 15),
    )

    doc.attach_document("https://pocketsmith.com/attachments/123")
    assert doc.status == DocumentStatus.ATTACHED
    assert doc.attachment_url == "https://pocketsmith.com/attachments/123"
    assert doc.attached_at is not None


def test_document_manager_initialization():
    """Test creating document manager."""
    manager = DocumentManager()
    assert manager is not None
    assert len(manager.documents) == 0


def test_document_manager_determine_requirement():
    """Test determining document requirement based on amount."""
    manager = DocumentManager()

    # Required: > $300 for work expenses
    assert manager.determine_requirement(350.00, "Work Expenses") == DocumentRequirement.REQUIRED

    # Recommended: > $100 for deductible categories
    assert (
        manager.determine_requirement(150.00, "Professional Development")
        == DocumentRequirement.RECOMMENDED
    )

    # Optional: < $100 or non-deductible
    assert manager.determine_requirement(50.00, "Groceries") == DocumentRequirement.OPTIONAL


def test_document_manager_track_transaction():
    """Test tracking a transaction's documentation status."""
    manager = DocumentManager()

    doc = manager.track_transaction(
        transaction_id=12345,
        amount=400.00,
        category="Office Supplies",
        date=datetime(2025, 11, 15),
    )

    assert doc.transaction_id == 12345
    assert doc.requirement == DocumentRequirement.REQUIRED
    assert doc.status == DocumentStatus.MISSING
    assert 12345 in manager.documents


def test_document_manager_get_missing_documents():
    """Test getting list of missing required documents."""
    manager = DocumentManager()

    # Add required document (missing)
    manager.track_transaction(
        transaction_id=1,
        amount=400.00,
        category="Work Expenses",
        date=datetime(2025, 11, 15),
    )

    # Add recommended document (missing)
    manager.track_transaction(
        transaction_id=2,
        amount=150.00,
        category="Professional Development",
        date=datetime(2025, 11, 16),
    )

    # Add required document (attached)
    doc3 = manager.track_transaction(
        transaction_id=3,
        amount=500.00,
        category="Work Expenses",
        date=datetime(2025, 11, 17),
    )
    doc3.attach_document("https://example.com/receipt.pdf")

    # Get missing required only
    missing_required = manager.get_missing_documents(required_only=True)
    assert len(missing_required) == 1
    assert missing_required[0].transaction_id == 1

    # Get all missing
    all_missing = manager.get_missing_documents(required_only=False)
    assert len(all_missing) == 2
