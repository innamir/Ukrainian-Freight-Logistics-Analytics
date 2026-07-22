# Data Quality Summary

## Overview

The dataset was validated before any profitability analysis to ensure consistency, completeness, and business realism.

The validation process included:

- duplicate primary keys
- missing values
- referential integrity
- business rule validation
- tariff consistency
- route consistency
- fuel consistency

## Validation Results

Most validation checks passed successfully.

### Passed

- No duplicate primary keys
- No critical missing values
- No orphan foreign keys
- No trips during truck downtime
- No fuel batch calculation errors
- No refueling records exceeding truck tank capacity
- No invalid trip dates or negative distances

### Business Exceptions

Two validation checks intentionally returned non-zero results:

- **650 trips exceeded the nominal truck capacity.**
  This reflects real freight operations, where moderate overloading (up to 15%) may occur to improve trip profitability.

- **16 trips exceeded the maximum allowed overload threshold (115% of truck capacity).**
  These records were retained as identified data quality exceptions and documented for transparency.

## Conclusion

The dataset passed all critical quality checks and is suitable for analytical modeling. The remaining exceptions represent documented business scenarios rather than structural data issues.