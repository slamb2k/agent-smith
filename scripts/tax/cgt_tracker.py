"""Capital Gains Tax (CGT) tracking for Level 2+ tax intelligence.

This module provides comprehensive tracking of asset purchases and sales,
automatic FIFO matching, holding period calculation, and CGT discount
eligibility determination for shares, cryptocurrency, and property assets.

Key Features:
- Track asset purchases with cost base calculation (price + fees)
- FIFO matching for sales across multiple parcels
- Automatic holding period calculation
- 50% CGT discount eligibility for assets held > 365 days
- Support for shares, crypto, and property
- Financial year reporting (Australian tax year: July 1 - June 30)
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Dict, Any, Union
from uuid import uuid4


class AssetType(Enum):
    """Supported asset types for CGT tracking."""

    SHARES = "shares"
    CRYPTO = "crypto"
    PROPERTY = "property"


@dataclass
class Asset:
    """Represents an asset purchase (parcel) for CGT tracking.

    Attributes:
        asset_id: Unique identifier for this asset parcel
        asset_type: Type of asset (shares, crypto, property)
        name: Asset name/identifier (e.g., "BHP Group", "Bitcoin", "123 Main St")
        quantity: Quantity purchased (shares, coins, or 1 for property)
        purchase_date: Date of purchase
        purchase_price: Price per unit at purchase
        fees: Transaction fees (brokerage, stamp duty, legal fees, etc.)
        cost_base: Total cost base (quantity * price + fees)
    """

    asset_id: str
    asset_type: AssetType
    name: str
    quantity: Decimal
    purchase_date: date
    purchase_price: Decimal
    fees: Decimal
    cost_base: Decimal = field(init=False)

    def __post_init__(self) -> None:
        """Calculate cost base after initialization."""
        self.cost_base = (self.quantity * self.purchase_price) + self.fees


@dataclass
class CGTEvent:
    """Represents a Capital Gains Tax event (sale).

    Attributes:
        event_id: Unique identifier for this CGT event
        asset_id: Reference to the asset parcel sold
        event_type: Type of event (currently only "sale")
        event_date: Date of the sale
        quantity: Quantity sold
        sale_price: Price per unit at sale
        fees: Transaction fees (brokerage, agent commission, legal fees, etc.)
        holding_period_days: Number of days asset was held
        discount_eligible: True if held > 365 days (50% CGT discount)
        capital_gain: Total capital gain/loss for this event
    """

    event_id: str
    asset_id: str
    event_type: str
    event_date: date
    quantity: Decimal
    sale_price: Decimal
    fees: Decimal
    holding_period_days: int
    discount_eligible: bool
    capital_gain: Decimal


class CGTTracker:
    """Capital Gains Tax tracker with FIFO matching and discount calculation.

    Tracks asset purchases and sales, automatically matches sales to purchases
    using FIFO (First In, First Out) method, calculates holding periods, and
    determines CGT discount eligibility.

    Example:
        >>> tracker = CGTTracker()
        >>> # Track purchase
        >>> asset = tracker.track_purchase(
        ...     asset_type=AssetType.SHARES,
        ...     name="BHP Group",
        ...     quantity=Decimal("100"),
        ...     purchase_date=date(2023, 1, 1),
        ...     purchase_price=Decimal("45.50"),
        ...     fees=Decimal("19.95")
        ... )
        >>> # Track sale
        >>> event = tracker.track_sale(
        ...     asset_type=AssetType.SHARES,
        ...     name="BHP Group",
        ...     quantity=Decimal("100"),
        ...     sale_date=date(2024, 6, 1),
        ...     sale_price=Decimal("52.00"),
        ...     fees=Decimal("19.95")
        ... )
        >>> print(f"Discount eligible: {event.discount_eligible}")
    """

    def __init__(self) -> None:
        """Initialize CGT tracker."""
        self.assets: List[Asset] = []
        self.events: List[CGTEvent] = []

    def track_purchase(
        self,
        asset_type: AssetType,
        name: str,
        quantity: Decimal,
        purchase_date: date,
        purchase_price: Decimal,
        fees: Decimal,
    ) -> Asset:
        """Track an asset purchase.

        Args:
            asset_type: Type of asset
            name: Asset name/identifier
            quantity: Quantity purchased
            purchase_date: Date of purchase
            purchase_price: Price per unit
            fees: Transaction fees

        Returns:
            Asset: The created asset parcel
        """
        asset = Asset(
            asset_id=str(uuid4()),
            asset_type=asset_type,
            name=name,
            quantity=quantity,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            fees=fees,
        )

        self.assets.append(asset)
        return asset

    def track_sale(
        self,
        asset_type: AssetType,
        name: str,
        quantity: Decimal,
        sale_date: date,
        sale_price: Decimal,
        fees: Decimal,
    ) -> Union[CGTEvent, List[CGTEvent]]:
        """Track an asset sale with automatic FIFO matching.

        Matches the sale to purchased assets using FIFO (First In, First Out).
        May create multiple CGT events if the sale spans multiple purchase parcels.

        Args:
            asset_type: Type of asset
            name: Asset name/identifier
            quantity: Quantity sold
            sale_date: Date of sale
            sale_price: Price per unit
            fees: Transaction fees

        Returns:
            CGTEvent or List[CGTEvent]: One or more CGT events

        Raises:
            ValueError: If no holdings found or insufficient quantity
        """
        # Get matching assets (FIFO order)
        matching_assets = [
            a
            for a in self.assets
            if a.asset_type == asset_type and a.name == name and a.quantity > 0
        ]

        if not matching_assets:
            raise ValueError(f"No holdings found for {asset_type.value} '{name}'")

        # Sort by purchase date (FIFO)
        matching_assets.sort(key=lambda a: a.purchase_date)

        # Check total available quantity
        total_available = sum(a.quantity for a in matching_assets)
        if total_available < quantity:
            raise ValueError(
                f"Insufficient quantity. Have {total_available}, trying to sell {quantity}"
            )

        # Match sales to purchases (FIFO)
        events = []
        remaining_to_sell = quantity

        for asset in matching_assets:
            if remaining_to_sell <= 0:
                break

            # Determine how much from this parcel
            quantity_from_parcel = min(remaining_to_sell, asset.quantity)

            # Calculate proportional cost base
            proportion = quantity_from_parcel / asset.quantity
            parcel_cost_base = asset.cost_base * proportion

            # Calculate proportional sale proceeds and fees
            sale_proportion = quantity_from_parcel / quantity
            parcel_sale_proceeds = quantity_from_parcel * sale_price
            parcel_fees = fees * sale_proportion

            # Calculate capital gain: (sale proceeds - fees) - cost base
            capital_gain = (parcel_sale_proceeds - parcel_fees) - parcel_cost_base

            # Calculate holding period
            holding_period = self._calculate_holding_period(asset.purchase_date, sale_date)

            # Determine discount eligibility
            discount_eligible = holding_period > 365

            # Create CGT event
            event = CGTEvent(
                event_id=str(uuid4()),
                asset_id=asset.asset_id,
                event_type="sale",
                event_date=sale_date,
                quantity=quantity_from_parcel,
                sale_price=sale_price,
                fees=parcel_fees,
                holding_period_days=holding_period,
                discount_eligible=discount_eligible,
                capital_gain=capital_gain,
            )

            events.append(event)

            # Reduce asset quantity and cost base
            asset.quantity -= quantity_from_parcel
            asset.cost_base -= parcel_cost_base
            remaining_to_sell -= quantity_from_parcel

        self.events.extend(events)

        # Return single event or list
        return events[0] if len(events) == 1 else events

    def _calculate_holding_period(self, purchase_date: date, sale_date: date) -> int:
        """Calculate holding period in days.

        Args:
            purchase_date: Date of purchase
            sale_date: Date of sale

        Returns:
            int: Number of days held
        """
        return (sale_date - purchase_date).days

    def get_all_assets(self) -> List[Asset]:
        """Get all tracked assets (including sold parcels with quantity=0).

        Returns:
            List[Asset]: All assets sorted by purchase date
        """
        return sorted(self.assets, key=lambda a: a.purchase_date)

    def get_holdings(self, asset_type: AssetType, name: str) -> Dict[str, Any]:
        """Get current holdings for a specific asset.

        Args:
            asset_type: Type of asset
            name: Asset name/identifier

        Returns:
            Dict containing total_quantity and total_cost_base
        """
        matching_assets = [
            a
            for a in self.assets
            if a.asset_type == asset_type and a.name == name and a.quantity > 0
        ]

        total_quantity = sum(a.quantity for a in matching_assets)
        total_cost_base = sum(a.cost_base for a in matching_assets)

        return {
            "asset_type": asset_type,
            "name": name,
            "total_quantity": total_quantity,
            "total_cost_base": total_cost_base,
            "parcels": len(matching_assets),
        }

    def get_events_for_financial_year(self, year: int) -> List[CGTEvent]:
        """Get CGT events for a specific Australian financial year.

        Australian financial year runs from July 1 to June 30.
        Year refers to the year in which the FY ends (e.g., FY 2024-25 = year 2025).

        Args:
            year: Financial year ending (e.g., 2025 for FY 2024-25)

        Returns:
            List[CGTEvent]: Events within the financial year
        """
        fy_start = date(year - 1, 7, 1)
        fy_end = date(year, 6, 30)

        return [event for event in self.events if fy_start <= event.event_date <= fy_end]

    def calculate_total_capital_gains(self, year: int) -> Dict[str, Any]:
        """Calculate total capital gains for a financial year.

        Args:
            year: Financial year ending (e.g., 2025 for FY 2024-25)

        Returns:
            Dict with total_gain, discount_eligible_gain, non_discount_gain
        """
        events = self.get_events_for_financial_year(year)

        total_gain = Decimal("0")
        discount_eligible_gain = Decimal("0")
        non_discount_gain = Decimal("0")

        for event in events:
            total_gain += event.capital_gain

            if event.discount_eligible:
                discount_eligible_gain += event.capital_gain
            else:
                non_discount_gain += event.capital_gain

        return {
            "total_gain": total_gain,
            "discount_eligible_gain": discount_eligible_gain,
            "non_discount_gain": non_discount_gain,
            "total_events": len(events),
        }
