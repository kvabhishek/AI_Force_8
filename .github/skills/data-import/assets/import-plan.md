# Data import

<!-- Made from the data-import skill's template. Fill it in before you write the import, and update the report after each full import. -->

- **Database:**
- **Import command:**

## Tables

| Table | Source file | Primary key | Foreign keys | Notes |
|---|---|---|---|---|
| | | | | |

## Data issues

| Issue | File and column | Rows | Decision | How | Test |
|---|---|---:|---|---|---|
| | | | | | |

The decision is one of:

- **Fix:** correct the value and load the row, such as trimming spaces from a code.
- **Flag:** load the row as it is and mark it, so the app can show or exclude it.
- **Reject:** don't load the row. Write it to `import_rejects` with the reason.

## Import report

| File | Rows read | Loaded | Fixed | Flagged | Rejected |
|---|---:|---:|---:|---:|---:|
| | | | | | |

Rows read should equal rows loaded plus rows rejected. Fixed and flagged rows are part of the rows loaded.
