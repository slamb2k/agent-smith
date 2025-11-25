"""Category hierarchy visualization for dry-run previews and change detection."""

from typing import Dict, List, Any, Optional
from collections import defaultdict


class CategoryChange:
    """Represents a change to a category."""

    NEW = "new"
    RENAMED = "renamed"
    MOVED = "moved"  # Parent changed
    REUSED = "reused"  # Exact match, no changes

    def __init__(
        self,
        change_type: str,
        category: Dict[str, Any],
        old_name: Optional[str] = None,
        old_parent: Optional[str] = None,
    ):
        self.change_type = change_type
        self.category = category
        self.old_name = old_name
        self.old_parent = old_parent


class CategoryVisualizer:
    """Visualize category hierarchies with ASCII tree diagrams."""

    # ASCII tree characters
    BRANCH = "├── "
    LAST_BRANCH = "└── "
    VERTICAL = "│   "
    SPACE = "    "

    # Change indicators
    SYMBOLS = {
        CategoryChange.NEW: "+ ",
        CategoryChange.RENAMED: "~ ",
        CategoryChange.MOVED: "→ ",
        CategoryChange.REUSED: "  ",
    }

    def __init__(self, use_colors: bool = True):
        """Initialize visualizer.

        Args:
            use_colors: Whether to use ANSI color codes (disable for file output)
        """
        self.use_colors = use_colors

    def build_tree_structure(
        self, categories: List[Dict[str, Any]]
    ) -> Dict[Optional[str], List[Dict[str, Any]]]:
        """Build a tree structure from flat category list.

        Args:
            categories: List of category dicts with 'name' and 'parent' keys

        Returns:
            Dict mapping parent_name -> list of child categories
        """
        tree: Dict[Optional[str], List[Dict[str, Any]]] = defaultdict(list)

        for cat in categories:
            parent = cat.get("parent")
            tree[parent].append(cat)

        # Sort children by name for consistent display
        for parent in tree:
            tree[parent] = sorted(tree[parent], key=lambda c: c["name"])

        return tree

    def render_tree(
        self,
        categories: List[Dict[str, Any]],
        changes: Optional[Dict[str, CategoryChange]] = None,
        title: str = "Category Structure",
    ) -> str:
        """Render category tree as ASCII diagram.

        Args:
            categories: List of categories to render
            changes: Optional dict mapping category name to CategoryChange
            title: Title for the tree diagram

        Returns:
            Multi-line string with tree diagram
        """
        tree = self.build_tree_structure(categories)
        lines = []

        # Title
        lines.append(f"\n{title}")
        lines.append("=" * len(title))
        lines.append("")

        # Render from root level
        root_categories = tree.get(None, [])

        if not root_categories:
            lines.append("(No categories)")
            return "\n".join(lines)

        for i, cat in enumerate(root_categories):
            is_last = i == len(root_categories) - 1
            self._render_node(cat, tree, changes, "", is_last, lines)

        # Add legend if changes present
        if changes and any(c.change_type != CategoryChange.REUSED for c in changes.values()):
            lines.append("")
            lines.append("Legend:")
            lines.append(f"  {self.SYMBOLS[CategoryChange.NEW]}New category")
            lines.append(f"  {self.SYMBOLS[CategoryChange.RENAMED]}Renamed (was: old name)")
            lines.append(f"  {self.SYMBOLS[CategoryChange.MOVED]}Moved to new parent")

        return "\n".join(lines)

    def _render_node(
        self,
        category: Dict[str, Any],
        tree: Dict[Optional[str], List[Dict[str, Any]]],
        changes: Optional[Dict[str, CategoryChange]],
        prefix: str,
        is_last: bool,
        lines: List[str],
    ) -> None:
        """Recursively render a category node and its children.

        Args:
            category: Category to render
            tree: Full tree structure
            changes: Change information
            prefix: Current line prefix (indentation and branches)
            is_last: Whether this is the last sibling
            lines: Output lines list to append to
        """
        cat_name = category["name"]

        # Determine branch character
        branch = self.LAST_BRANCH if is_last else self.BRANCH

        # Get change info
        change = changes.get(cat_name) if changes else None
        symbol = self.SYMBOLS.get(change.change_type, "  ") if change else "  "

        # Build line with change indicator
        line = f"{prefix}{branch}{symbol}{cat_name}"

        # Add change details
        if change:
            if change.change_type == CategoryChange.RENAMED and change.old_name:
                line += self._dim(f" (was: {change.old_name})")
            elif change.change_type == CategoryChange.MOVED and change.old_parent:
                old_parent_display = change.old_parent or "(root)"
                line += self._dim(f" (moved from: {old_parent_display})")

        lines.append(line)

        # Render children
        children = tree.get(cat_name, [])
        if children:
            # Update prefix for children
            extension = self.SPACE if is_last else self.VERTICAL
            child_prefix = prefix + extension

            for i, child in enumerate(children):
                child_is_last = i == len(children) - 1
                self._render_node(child, tree, changes, child_prefix, child_is_last, lines)

    def render_side_by_side(
        self,
        existing_categories: List[Dict[str, Any]],
        new_categories: List[Dict[str, Any]],
        changes: Dict[str, CategoryChange],
    ) -> str:
        """Render side-by-side comparison of existing vs new structure.

        Args:
            existing_categories: Current categories in PocketSmith
            new_categories: Categories after applying template
            changes: Detected changes

        Returns:
            Multi-line string with side-by-side comparison
        """
        new_tree = self.render_tree(new_categories, changes, title="After Applying Template")

        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("CATEGORY STRUCTURE COMPARISON")
        lines.append("=" * 70)
        lines.append("")

        # Count changes
        new_count = sum(1 for c in changes.values() if c.change_type == CategoryChange.NEW)
        renamed_count = sum(1 for c in changes.values() if c.change_type == CategoryChange.RENAMED)
        moved_count = sum(1 for c in changes.values() if c.change_type == CategoryChange.MOVED)
        reused_count = sum(1 for c in changes.values() if c.change_type == CategoryChange.REUSED)

        lines.append("Summary of Changes:")
        if new_count > 0:
            lines.append(f"  {self._green(f'+ {new_count}')} new categories")
        if renamed_count > 0:
            lines.append(f"  {self._yellow(f'~ {renamed_count}')} renamed categories")
        if moved_count > 0:
            lines.append(f"  {self._blue(f'→ {moved_count}')} categories moved to new parent")
        if reused_count > 0:
            lines.append(f"    {reused_count} existing categories reused")
        lines.append("")

        # Show new tree
        lines.append(new_tree)

        return "\n".join(lines)

    def detect_changes(
        self,
        existing_categories: List[Dict[str, Any]],
        new_categories: List[Dict[str, Any]],
        strategy: str = "add_new",
    ) -> Dict[str, CategoryChange]:
        """Detect changes between existing and new category structures.

        Args:
            existing_categories: Current PocketSmith categories
            new_categories: Template categories to apply
            strategy: Application strategy (add_new, smart_merge, replace)

        Returns:
            Dict mapping category name to CategoryChange
        """
        changes: Dict[str, CategoryChange] = {}

        # Build maps of existing categories
        existing_map = {cat["name"]: cat for cat in existing_categories}

        for new_cat in new_categories:
            new_name = new_cat["name"]

            if new_name in existing_map:
                # Category exists - check for changes
                existing = existing_map[new_name]

                # Check if parent changed
                existing_parent = existing.get("parent")
                new_parent = new_cat.get("parent")

                if existing_parent != new_parent:
                    changes[new_name] = CategoryChange(
                        CategoryChange.MOVED, new_cat, old_parent=existing_parent
                    )
                else:
                    changes[new_name] = CategoryChange(CategoryChange.REUSED, new_cat)
            else:
                # New category
                changes[new_name] = CategoryChange(CategoryChange.NEW, new_cat)

        return changes

    def render_compact_list(
        self, categories: List[Dict[str, Any]], changes: Optional[Dict[str, CategoryChange]] = None
    ) -> str:
        """Render compact list view (no tree, just indented by hierarchy).

        Args:
            categories: Categories to render
            changes: Optional change information

        Returns:
            Multi-line string
        """
        lines = []
        tree = self.build_tree_structure(categories)

        # Group by top-level parent
        root_categories = tree.get(None, [])

        for root_cat in root_categories:
            # Render root
            change = changes.get(root_cat["name"]) if changes else None
            symbol = self.SYMBOLS.get(change.change_type, "  ") if change else "  "
            lines.append(f"{symbol}{root_cat['name']}")

            # Render children
            self._render_compact_children(root_cat["name"], tree, changes, 1, lines)

        return "\n".join(lines)

    def _render_compact_children(
        self,
        parent_name: str,
        tree: Dict[Optional[str], List[Dict[str, Any]]],
        changes: Optional[Dict[str, CategoryChange]],
        level: int,
        lines: List[str],
    ) -> None:
        """Recursively render children in compact format."""
        children = tree.get(parent_name, [])
        indent = "  " * level

        for child in children:
            child_name = child["name"]
            change = changes.get(child_name) if changes else None
            symbol = self.SYMBOLS.get(change.change_type, "  ") if change else "  "

            lines.append(f"{indent}{symbol}{child_name}")
            self._render_compact_children(child_name, tree, changes, level + 1, lines)

    # Color helpers (ANSI escape codes)
    def _green(self, text: str) -> str:
        """Green text (additions)."""
        if not self.use_colors:
            return text
        return f"\033[32m{text}\033[0m"

    def _yellow(self, text: str) -> str:
        """Yellow text (modifications)."""
        if not self.use_colors:
            return text
        return f"\033[33m{text}\033[0m"

    def _blue(self, text: str) -> str:
        """Blue text (movements)."""
        if not self.use_colors:
            return text
        return f"\033[34m{text}\033[0m"

    def _dim(self, text: str) -> str:
        """Dimmed text (secondary info)."""
        if not self.use_colors:
            return text
        return f"\033[2m{text}\033[0m"
