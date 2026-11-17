# Common data issues

Ways to spot and handle the issues that real data files often have. If the brief or the data dictionary says how to handle an issue, follow that instead.

| Issue | How the profile shows it | Ways to handle it |
|---|---|---|
| Exact duplicate rows | "Exact copies of an earlier row" | Load one copy, and reject the others as duplicates. |
| Same ID, different content | A note about repeated values in an ID column | Decide which version wins, such as the latest. Otherwise reject them all and report the ID. |
| Missing values | Empty is above 0 | Reject the row if a result needs the value. Otherwise load it as null and flag it. |
| Inconsistent codes | Formats such as `A`, `a` and ` A` in one column | Trim spaces and fix the case, then check the code against the list of valid codes. |
| Unknown codes or IDs | "Links between files" shows rows with no match | Reject or flag the row. Don't guess a match. |
| Mixed formats | Two formats in one column, such as `9-9-9` and `9/9/9` | Parse each known format explicitly, and reject anything else. |
| Numbers stored as text | A mixed type, or a format such as `9,9.9` | Remove the thousands separators, then parse the value as a decimal. |
| Impossible values | A range with negatives, zeros or dates in the future | Reject the row with a reason that names the check that failed. |
| Placeholder values | Odd values such as `999.9`, `N/A` or `-` | Treat them as missing, not as real values. |
| Mixed time zones | Timestamps ending in both `A` (for `Z`) and `+9:9` | Convert every time to one zone before you compare or sort. |
| Late or out-of-order rows | "The file isn't in time order" | Sort by the event time, never by the order in the file. |
| Different units | More than one unit for the same measure | Convert to one unit, using the factor in the data dictionary. |
| Corrections | Not shown: two rows for the same thing at different times | Use the latest as the current value. Keep the others if you need the history. |
| Gaps | Not shown: a missing period has no row at all | Don't invent rows. Decide how your rules treat a missing period. |
| Checks across columns | Not shown, such as an end before its start | Add a check for each one to your plan. |
