# CRLA Level 3 Project

Run locally with `uvicorn app:app --reload`.
On Render, build with `pip install -r requirements.txt` and start with
`uvicorn app:app --host 0.0.0.0 --port $PORT`.

Configure these variables in local `.env` or Render Environment settings:

- `GOOGLE_CREDENTIALS`: service account JSON.
- `GOOGLE_SHEET_ID`: spreadsheet ID shared by both tabs.
- `GOOGLE_OBSERVATIONS_SHEET_NAME`: exact observations tab name (for example `sheet1`).
- `GOOGLE_INTERVIEWEES_SHEET_NAME`: exact candidate tab name (for example `Interviewees`).

Tab names are case sensitive and must be different. See `.env.example`.
Enable the Google Sheets API and share the spreadsheet with the service account as an Editor.
Observations append to columns A–K of the explicitly selected observations tab;
place observation headers in row 1 and keep this table contiguous.
Add `Profstaff` as the header in column K. The required Yes/No answer is saved
with each evaluation and remains selected after saving a draft.

The interviewees tab must have these six unique headers in row 1:

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
| Group 1 First Name | Group 1 Last Name | Group 2 First Name | Group 2 Last Name | Group 3 First Name | Group 3 Last Name |

Place each candidate below the first/last name pair for their assigned group.
Replace the old two-column headers with this layout; existing names in A–B
will belong to Group 1 until you move them to another pair. Columns are matched
by header, so their order can also be changed. Groups may have different sizes;
blank cells and empty groups are allowed. Names are trimmed, combined,
deduplicated within each group, and sorted for display. A name appearing in
multiple groups is treated as an error; give people with identical names distinct
labels if necessary.

Groups stay together and rotate as follows:

| Group | Round 1 | Round 2 | Round 3 |
| --- | --- | --- | --- |
| 1 | Tinker Toys | Mini Lessons | Scenarios |
| 2 | Mini Lessons | Scenarios | Tinker Toys |
| 3 | Scenarios | Tinker Toys | Mini Lessons |

Names refresh on page loads at most once per 60 seconds per server process.
Connection, header, or duplicate-group failures show a warning and retain the
last successfully loaded groups in that process. A valid tab with headers but
no names clears all groups. Restarting clears the cache. No CSV or sample-name
fallback is used.
Remove any old Render `names.csv` secret file or `NAMES_CSV_PATH` setting if desired;
they are no longer used.

Run checks with `.venv/bin/python -m unittest discover -s tests`.
