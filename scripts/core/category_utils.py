"""Category utility functions for working with PocketSmith categories.

This module provides helper functions for searching and working with PocketSmith
categories, handling the hierarchical structure properly.
"""

from typing import List, Dict, Any, Optional


def find_category_by_name(
    categories: List[Dict[str, Any]], name: str, case_sensitive: bool = False
) -> Optional[Dict[str, Any]]:
    """Find a category by name in a flat list of categories.

    This function assumes categories have already been flattened using
    api_client.get_categories(user_id, flatten=True).

    Args:
        categories: Flat list of category objects
        name: Category name to search for
        case_sensitive: If True, performs case-sensitive match (default: False)

    Returns:
        Category object if found, None otherwise

    Example:
        >>> from scripts.core.api_client import PocketSmithClient
        >>> client = PocketSmithClient()
        >>> user = client.get_user()
        >>> categories = client.get_categories(user['id'], flatten=True)
        >>> cat = find_category_by_name(categories, "Internet & Phone")
        >>> print(cat['id'])
        26927667
    """
    search_name = name if case_sensitive else name.lower()

    for cat in categories:
        cat_name = cat.get("title", "")
        compare_name = cat_name if case_sensitive else cat_name.lower()

        if compare_name == search_name:
            return cat

    return None


def find_category_by_id(
    categories: List[Dict[str, Any]], category_id: int
) -> Optional[Dict[str, Any]]:
    """Find a category by ID in a flat list of categories.

    Args:
        categories: Flat list of category objects
        category_id: Category ID to search for

    Returns:
        Category object if found, None otherwise
    """
    for cat in categories:
        if cat.get("id") == category_id:
            return cat

    return None


def get_category_path(categories: List[Dict[str, Any]], category: Dict[str, Any]) -> List[str]:
    """Get the full path of a category (e.g., ["Utilities", "Internet & Phone"]).

    Args:
        categories: Flat list of category objects
        category: Category object to get path for

    Returns:
        List of category names from root to the given category

    Example:
        >>> path = get_category_path(categories, internet_phone_cat)
        >>> print(" → ".join(path))
        Utilities → Internet & Phone
    """
    path = [category.get("title", "Unknown")]

    # Walk up the parent chain
    current = category
    while current.get("parent_id"):
        parent = find_category_by_id(categories, current["parent_id"])
        if parent:
            path.insert(0, parent.get("title", "Unknown"))
            current = parent
        else:
            break

    return path


def filter_categories(
    categories: List[Dict[str, Any]],
    parent_only: bool = False,
    child_only: bool = False,
    exclude_transfers: bool = True,
) -> List[Dict[str, Any]]:
    """Filter categories by various criteria.

    Args:
        categories: Flat list of category objects
        parent_only: If True, return only parent categories (no parent_id)
        child_only: If True, return only child categories (has parent_id)
        exclude_transfers: If True, exclude transfer categories (default: True)

    Returns:
        Filtered list of categories
    """
    result = categories.copy()

    if exclude_transfers:
        result = [c for c in result if not c.get("is_transfer", False)]

    if parent_only:
        result = [c for c in result if not c.get("parent_id")]
    elif child_only:
        result = [c for c in result if c.get("parent_id")]

    return result


def search_categories(
    categories: List[Dict[str, Any]], query: str, limit: int = 10
) -> List[Dict[str, Any]]:
    """Search categories by partial name match (case-insensitive).

    Args:
        categories: Flat list of category objects
        query: Search query
        limit: Maximum number of results (default: 10)

    Returns:
        List of matching categories, sorted by relevance

    Example:
        >>> results = search_categories(categories, "internet")
        >>> for cat in results:
        >>>     print(f"{cat['title']} (ID: {cat['id']})")
        Internet (ID: 17151517)
        Internet & Phone (ID: 26927667)
    """
    query_lower = query.lower()
    matches = []

    for cat in categories:
        title = cat.get("title", "")
        title_lower = title.lower()

        if query_lower in title_lower:
            # Calculate relevance score (exact match > starts with > contains)
            if title_lower == query_lower:
                score = 3
            elif title_lower.startswith(query_lower):
                score = 2
            else:
                score = 1

            matches.append((score, cat))

    # Sort by score (descending), then by title
    matches.sort(key=lambda x: (-x[0], x[1].get("title", "")))

    return [cat for score, cat in matches[:limit]]


def sort_by_specificity(
    categories: List[Dict[str, Any]], prefer_specific: bool = True
) -> List[Dict[str, Any]]:
    """Sort categories by hierarchy level (specificity).

    Args:
        categories: Flat list of category objects with 'hierarchy_level' field
        prefer_specific: If True, sort child categories first (descending level).
                        If False, sort parent categories first (ascending level).

    Returns:
        Sorted list of categories

    Example:
        >>> # Prefer specific (child) categories
        >>> sorted_cats = sort_by_specificity(categories, prefer_specific=True)
        >>> # Result: ["Internet & Phone" (level 1), "Utilities" (level 0)]

        >>> # Prefer general (parent) categories
        >>> sorted_cats = sort_by_specificity(categories, prefer_specific=False)
        >>> # Result: ["Utilities" (level 0), "Internet & Phone" (level 1)]
    """
    if prefer_specific:
        # Higher level = more specific (children first)
        return sorted(categories, key=lambda c: c.get("hierarchy_level", 0), reverse=True)
    else:
        # Lower level = more general (parents first)
        return sorted(categories, key=lambda c: c.get("hierarchy_level", 0))


def find_most_specific_category(
    categories: List[Dict[str, Any]], query: str, limit: int = 10
) -> List[Dict[str, Any]]:
    """Search categories and prioritize more specific (child) matches.

    Combines search_categories with specificity sorting to prefer child categories
    over parent categories when both match.

    Args:
        categories: Flat list of category objects with 'hierarchy_level' field
        query: Search query
        limit: Maximum number of results (default: 10)

    Returns:
        List of matching categories, sorted by relevance then specificity

    Example:
        >>> # Searching for "utilities" might match both parent and children
        >>> results = find_most_specific_category(categories, "utilities")
        >>> # Prefer: "Internet & Phone", "Power", "Gas" over "Utilities"
    """
    # First, search for matches
    matches = search_categories(categories, query, limit=100)  # Get more matches

    # Sort by hierarchy level (more specific first)
    specific_matches = sort_by_specificity(matches, prefer_specific=True)

    return specific_matches[:limit]


def get_hierarchy_level(category: Dict[str, Any]) -> int:
    """Get the hierarchy level of a category.

    Args:
        category: Category object (should have 'hierarchy_level' if flattened)

    Returns:
        Hierarchy level (0 = root/parent, 1 = child, 2 = grandchild, etc.)
        Returns 0 if level not found (treats as parent)

    Example:
        >>> level = get_hierarchy_level(internet_phone_cat)
        >>> print(f"Level: {level}")  # Level: 1 (child of Utilities)
    """
    level = category.get("hierarchy_level", 0)
    return int(level) if level is not None else 0


def is_child_category(category: Dict[str, Any]) -> bool:
    """Check if a category is a child (has a parent).

    Args:
        category: Category object

    Returns:
        True if category has a parent_id, False otherwise
    """
    return category.get("parent_id") is not None


def is_parent_category(category: Dict[str, Any]) -> bool:
    """Check if a category is a parent (no parent_id).

    Args:
        category: Category object

    Returns:
        True if category has no parent_id, False otherwise
    """
    return category.get("parent_id") is None
