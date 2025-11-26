"""Label constants and utilities for Agent Smith.

This module defines standard labels used throughout the system for flagging
transactions that need review, tracking tax implications, and other metadata.

Label Taxonomy:
- System labels (auto-generated): Prefixed with ⚠️ Review: for flags
- User labels (from rules): Descriptive labels like "Tax Deductible"
- Metadata labels: Context like "Shared Expense", "Child Support"
"""

from typing import List

# =============================================================================
# SYSTEM REVIEW LABELS (Auto-Generated Flags)
# =============================================================================

# Conflict/Review Flags
LABEL_CATEGORY_CONFLICT = "⚠️ Review: Category Conflict"
"""Applied when a local rule suggests a different category than existing manual category."""

LABEL_GENERIC_PAYPAL = "⚠️ Review: Generic PayPal"
"""Applied to PayPal transactions with no merchant identifier."""

LABEL_UNCATEGORIZED = "⚠️ Review: Uncategorized"
"""Applied to transactions that couldn't be auto-categorized."""

LABEL_LARGE_AMOUNT = "⚠️ Review: Large Amount"
"""Applied to transactions exceeding threshold for review."""

# All system review labels (for easy detection)
SYSTEM_REVIEW_LABELS = [
    LABEL_CATEGORY_CONFLICT,
    LABEL_GENERIC_PAYPAL,
    LABEL_UNCATEGORIZED,
    LABEL_LARGE_AMOUNT,
]

# =============================================================================
# USER-DEFINED LABELS (Rule-Based)
# =============================================================================

# General Review Labels
LABEL_NEEDS_REVIEW = "Needs Review"
"""Generic review flag applied by rules."""

LABEL_REQUIRES_RECEIPT = "Requires Receipt"
"""Transaction needs receipt for documentation/substantiation."""

# Tax-Related Labels
LABEL_TAX_DEDUCTIBLE = "Tax Deductible"
"""Expense may be tax deductible (consult tax advisor)."""

LABEL_GST_CLAIMABLE = "GST Claimable"
"""GST credit may be claimable for business purchases."""

# Payment/Transfer Labels
LABEL_ONLINE_PAYMENT = "Online Payment"
"""Online payment service transaction."""

LABEL_SHARED_EXPENSE = "Shared Expense"
"""Expense shared between multiple people/accounts."""

# Family/Child-Related Labels
LABEL_CHILD_SUPPORT = "Child Support"
"""Child support payment or receipt."""

LABEL_CHILD_SUPPORT_PAID = "Child Support Paid"
"""Outgoing child support payment."""

LABEL_CHILD_SUPPORT_RECEIVED = "Child Support Received"
"""Incoming child support receipt."""

LABEL_KIDS_EXPENSE = "Kids Expense"
"""Expense related to children (activities, school, etc)."""

# Work-Related Labels
LABEL_WORK_EXPENSE = "Work Expense"
"""Work-related expense (may be deductible)."""

LABEL_WORK_RELATED = "Work Related"
"""Transaction related to employment/business."""

# =============================================================================
# LABEL DETECTION UTILITIES
# =============================================================================


def is_review_label(label: str) -> bool:
    """Check if a label is a system review flag.

    All system review labels use the format: ⚠️ Review: {reason}
    User-defined labels like "Needs Review" do NOT match (no colon).

    Args:
        label: Label string to check

    Returns:
        True if label is a system-generated review flag

    Examples:
        >>> is_review_label("⚠️ Review: Category Conflict")
        True
        >>> is_review_label("⚠️ Review: Generic PayPal")
        True
        >>> is_review_label("Needs Review")
        False
        >>> is_review_label("Tax Deductible")
        False
    """
    # System labels always contain "Review:" (with colon)
    # This distinguishes from user labels like "Needs Review"
    return "Review:" in str(label)


def is_conflict_label(label: str) -> bool:
    """DEPRECATED: Check if a label indicates a category conflict.

    This function is deprecated. Use direct comparison instead:
        label == LABEL_CATEGORY_CONFLICT

    Args:
        label: Label string to check

    Returns:
        True if label is the category conflict label

    Examples:
        >>> is_conflict_label("⚠️ Review: Category Conflict")
        True
        >>> is_conflict_label("⚠️ Review: Generic PayPal")
        False
    """
    # Deprecated: Only kept for backwards compatibility
    # Use: label == LABEL_CATEGORY_CONFLICT instead
    return label == LABEL_CATEGORY_CONFLICT


def has_review_flag(labels: List[str]) -> bool:
    """Check if transaction has any review flag.

    Args:
        labels: List of label strings

    Returns:
        True if any label is a review flag

    Examples:
        >>> has_review_flag(["⚠️ Review: Category Conflict", "Tax Deductible"])
        True
        >>> has_review_flag(["Tax Deductible", "Work Expense"])
        False
    """
    return any(is_review_label(label) for label in labels)


def remove_review_labels(labels: List[str]) -> List[str]:
    """Remove all system review flags from label list.

    Preserves user-defined labels like "Tax Deductible", "Needs Review", etc.

    Args:
        labels: List of label strings

    Returns:
        Filtered list with review flags removed

    Examples:
        >>> remove_review_labels(["⚠️ Review: Category Conflict", "Tax Deductible"])
        ["Tax Deductible"]
        >>> remove_review_labels(["Needs Review", "Work Expense"])
        ["Needs Review", "Work Expense"]
    """
    return [label for label in labels if not is_review_label(label)]


def add_review_label(labels: List[str], review_label: str) -> List[str]:
    """Add a review label if not already present.

    Args:
        labels: Existing label list
        review_label: Review label to add (use constants like LABEL_CATEGORY_CONFLICT)

    Returns:
        Updated label list

    Examples:
        >>> add_review_label(["Tax Deductible"], LABEL_CATEGORY_CONFLICT)
        ["Tax Deductible", "⚠️ Review: Category Conflict"]
        >>> add_review_label(["⚠️ Review: Category Conflict"], LABEL_CATEGORY_CONFLICT)
        ["⚠️ Review: Category Conflict"]
    """
    if review_label not in labels:
        return labels + [review_label]
    return labels


# =============================================================================
# LABEL VALIDATION
# =============================================================================


def validate_label(label: str) -> bool:
    """Check if a label follows naming conventions.

    Args:
        label: Label string to validate

    Returns:
        True if label is valid

    Notes:
        - System labels should use ⚠️ Review: prefix
        - User labels should be descriptive (2-50 chars)
        - No special characters except spaces, hyphens, colons
    """
    if not label or len(label) < 2 or len(label) > 50:
        return False

    # Check for system label format
    if label.startswith("⚠️ Review:"):
        return len(label) > 11  # Has content after prefix

    # User label - allow letters, numbers, spaces, hyphens
    import re

    return bool(re.match(r"^[\w\s\-:]+$", label))
