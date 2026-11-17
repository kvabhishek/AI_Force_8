---
# Example skill, unfinished on purpose: it has no profiler script yet.
# The first time it runs, Copilot writes one in your language. Review it and
# commit it to finish the skill. Copilot loads this skill when you ask it to
# import or load data, or you can type /data-import in Copilot Chat.
# How skills fit with instructions and agents: docs/copilot-customization.md
name: data-import
description: Imports CSV data files into a database. Profiles the files with a script, plans the tables and how to handle each data issue, then builds a repeatable import that keeps rejected rows and reports the counts. Use when loading data files into a database, reloading them or adding a new file.
---

# Data import

Follow these steps to load CSV files into a database. Use the language and database in `.github/copilot-instructions.md`. If they aren't set, use SQLite.

## 1. Profile the data

Don't read whole data files into the chat. Summarize them with a profiler script in `.github/skills/data-import/scripts/`:

- If there's a profiler in the project's language, run it from the repo root on the data folder.
- If there isn't one yet, write it first, following [the profiler spec](references/profiler-spec.md). Run it, then ask the team to review and commit it, so the skill is complete next time.

Then read the data dictionary, such as `data/README.md`. List every issue it describes and every issue the profile shows, such as two formats in one column.

## 2. Plan the import

Copy [the plan template](assets/import-plan.md) to `docs/data-import.md` and fill in:

- **Tables:** one for each file, with column types, a primary key and the foreign keys between files.
- **Data issues:** for each issue, decide whether to fix, flag or reject the row, and how you'll test it. If the brief says how to handle an issue, follow it. [Common data issues](references/data-issues.md) suggests ways to handle each kind.

Show the plan and wait for approval before you write any code.

## 3. Build the import

- Make one command that rebuilds the database from the files, so it's safe to run again.
- Write each rejected row to an `import_rejects` table with its file, row number, raw values and reason. Never drop a row without a record.
- Keep the source row number on each loaded row, so you can trace any result back to the file.
- Store money as an exact decimal, not a floating-point number. Store times in one time zone, and say which.

## 4. Test and report

- Add a test for each data issue, using a small fixture file with a few rows rather than the real data.
- Run the import and fill in the import report in `docs/data-import.md`. For each file, check that rows read equals rows loaded plus rows rejected.
- Add the import command to the README.
