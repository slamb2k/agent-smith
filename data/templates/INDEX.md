# Rule Templates

Preset rule hierarchies for different household types. Select the template that best matches your situation during initial setup.

## Available Templates

| Template | Best For | Key Features |
|----------|----------|--------------|
| **simple.yaml** | Single person | Basic categories, essential/discretionary labels |
| **separated-families.yaml** | Separated parents | Kids expense tracking, contributor tracking, child support |
| **shared-household.yaml** | Couples/roommates | Shared expense tracking, approval workflows, reconciliation |
| **advanced.yaml** | Complex finances | Tax optimization, investment tracking, business expenses |

## Template Metadata

Each template includes:
- **Category hierarchy** - Organized category structure
- **Label taxonomy** - Labels for tracking and workflows
- **Sample rules** - Pre-configured patterns for common merchants

## Customization

After selecting a template:
1. Copy to `data/rules.yaml`
2. Update merchant patterns for your region
3. Adjust account names to match your setup
4. Add custom rules as needed

## Template Details

### Simple
- **Target:** Individual managing personal finances
- **Categories:** Income, Groceries, Utilities, Dining, Entertainment, Transport
- **Labels:** Essential, Discretionary, Large Purchase

### Separated Families
- **Target:** Divorced/separated parents with shared custody
- **Categories:** Child Support, Kids Education, Kids Medical, Kids Activities
- **Labels:** Contributor tracking, Shared Responsibility, Needs Reconciliation

### Shared Household
- **Target:** Couples, roommates, or families with joint expenses
- **Categories:** Shared Groceries, Rent, Utilities, Personal expenses
- **Labels:** Contributor tracking, Needs Approval, Monthly Reconciliation

### Advanced
- **Target:** High-income households, business owners, investors
- **Categories:** Multiple income streams, Investment categories, Business expenses
- **Labels:** Tax deductible (ATO codes), CGT tracking, EOFY review, Documentation requirements
