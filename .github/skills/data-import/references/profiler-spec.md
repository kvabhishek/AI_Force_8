# Profiler spec

The data-import skill needs a profiler: a script that summarizes CSV files, so Copilot can plan an import without reading every row. Write it in the project's language, using only its standard library if you can, and save it in `.github/skills/data-import/scripts/`.

## Input

A folder of CSV files, `data` by default, or one or more file paths. It runs from the repo root.

## Output

Short Markdown, because Copilot reads it. For each file:

1. A heading with the file name, then the number of rows and columns.
2. A note for each of these, if found:
   - Rows that are exact copies of an earlier row.
   - Rows with a different number of fields from the header.
   - ID columns, ending in `_id`, where a few values repeat. Show some examples.
   - Timestamp columns where a few rows are earlier than the row before, so the file isn't in time order. Compare times in UTC.
3. A table with one row for each column:

| Column | Show |
|---|---|
| Type | integer, decimal, date, datetime or text. If the values have more than one type, show each type with its count. |
| Empty | The number of blank values |
| Distinct | The number of different values, or "all unique" |
| Range | The lowest and highest number, date or time |
| Formats | Each value with runs of digits replaced by `9`, capitals by `A` and lower-case letters by `a`, so `2026-10-14` becomes `9-9-9`. Show up to 5 formats with their counts, or "varied" if there are more. |
| Common values | The 3 most common values with their counts, if the column has 30 or fewer different values |

Wrap values in backticks, so spaces at the start or end stay visible.

Then add a section that checks the links between files. For each `_id` column in more than one file, find the file where it's unique, and list values in the other files that aren't there.

## Done when

- It runs in a few seconds on `data/`.
- Its output shows the issues the data dictionary describes, such as duplicates, blanks, odd formats and unknown IDs.
