"""Report output formatters."""

import csv
import io
import json
from typing import Dict, Any


def format_markdown(data: Dict[str, Any], report_type: str = "spending") -> str:
    """Format data as Markdown report.

    Args:
        data: Report data dict
        report_type: Type of report (spending, trends, etc.)

    Returns:
        Formatted Markdown string
    """
    lines = []

    # Header
    period = data.get("period", "Unknown")
    lines.append(f"# {report_type.title()} Report - {period}")
    lines.append("")

    # Summary section
    if "summary" in data:
        summary = data["summary"]
        lines.append("## Summary")
        lines.append("")
        lines.append(f"Total Income: ${summary.get('total_income', 0):,.2f}")
        lines.append(f"Total Expenses: ${summary.get('total_expenses', 0):,.2f}")
        lines.append(f"Net Income: ${summary.get('net_income', 0):,.2f}")
        lines.append("")

    # Categories table
    if "categories" in data:
        lines.append("## Spending by Category")
        lines.append("")
        lines.append("| Category | Total Spent | Transactions |")
        lines.append("|----------|-------------|--------------|")

        for cat in data["categories"]:
            name = cat.get("category_name", "Unknown")
            total = cat.get("total_spent", 0)
            count = cat.get("transaction_count", 0)
            lines.append(f"| {name} | ${total:,.2f} | {count} |")

        lines.append("")

    return "\n".join(lines)


def format_csv(data: Dict[str, Any], report_type: str = "spending") -> str:
    """Format data as CSV.

    Args:
        data: Report data dict
        report_type: Type of report

    Returns:
        CSV string
    """
    output = io.StringIO()

    if "categories" in data:
        categories = data["categories"]
        if not categories:
            return ""

        # Get fieldnames from first row
        fieldnames = list(categories[0].keys())

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        # Format numeric values with 2 decimal places
        formatted_rows = []
        for row in categories:
            formatted_row = {}
            for key, value in row.items():
                if isinstance(value, float):
                    formatted_row[key] = f"{value:.2f}"
                else:
                    formatted_row[key] = value
            formatted_rows.append(formatted_row)

        writer.writerows(formatted_rows)

    return output.getvalue()


def format_json(data: Dict[str, Any]) -> str:
    """Format data as JSON.

    Args:
        data: Report data dict

    Returns:
        JSON string
    """
    return json.dumps(data, indent=2)
