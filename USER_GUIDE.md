# Interview Administration User Guide

This guide is for administrators coordinating interviews and observers recording candidate evaluations in the Peer Connections application.

## 1. What the application does

The application reads three preassigned candidate groups from Google Sheets and shows the candidates assigned to a selected room and round. Observers record evaluations, review temporary drafts, and submit them to a central observations tab in Google Sheets.

The application does not create an interview timetable, assign observers, or make hiring decisions. The administrator coordinates those activities separately.

## 2. Prepare for interview day

Before sharing the application link:

1. Confirm that the latest application changes have been deployed.
2. Prepare the candidate groups in the connected Google Sheet.
3. Confirm the observations tab has the correct columns.
4. Open the application and check the candidate lists for each room and round.
5. Tell observers their room assignments, round schedule, and scoring criteria.
6. Ask each observer to use their own browser profile or device.

If conducting a test evaluation, clearly label it as a test. If submitted, remove the test row from Google Sheets afterward.

## 3. Set up candidate groups

Use the candidate tab already connected to the application. Keep its tab name unchanged unless the person maintaining the application updates its configuration.

Place these exact headers in row 1:

| Column | Header |
| --- | --- |
| A | Group A First Name |
| B | Group A Last Name |
| C | Group B First Name |
| D | Group B Last Name |
| E | Group C First Name |
| F | Group C Last Name |

Enter each candidate's first and last name below the pair for their assigned group. Each row can contain one candidate from each group; candidates sharing a row are not otherwise linked.

Groups may have different sizes. Blank rows and empty groups are allowed. First names and last names must remain in their matching pair. The application displays full names alphabetically within each group.

Enter each candidate in only one group. Repeated identical names within one group appear once; the same full name in different groups causes a loading warning. If two candidates have identical names, add a consistent distinguishing label to their name cells.

The columns define groups, not rounds. Groups stay together throughout the following rotation:

| Group | Round 1 | Round 2 | Round 3 |
| --- | --- | --- | --- |
| Group A | Mini Lessons | Scenarios | Tinker Toys |
| Group B | Scenarios | Tinker Toys | Mini Lessons |
| Group C | Tinker Toys | Mini Lessons | Scenarios |

For example, Tinker Toys shows Group B in Round 2. This is expected.

After changing names or assignments, allow at least 60 seconds and reload the application. Finalize groups before interviews begin where possible, so observers use consistent assignments.

## 4. Prepare the observations tab

Use the separate observations tab already connected to the application. Keep the candidate list and observations on different tabs.

Keep these columns in this order, with headers in row 1:

| Column | Suggested header | Saved information |
| --- | --- | --- |
| A | Timestamp | Submission time recorded by the server |
| B | Candidate | Candidate's full name |
| C | Round | Selected interview round |
| D | Room | Selected activity room |
| E | Observer | Observer's name |
| F | Teamwork | Teamwork score |
| G | Initiative/Problem Solving | Initiative/problem-solving score |
| H | Personal Representation | Personal representation score |
| I | Work With? | Yes, Maybe, or No |
| J | Notes | Observer's comments |
| K | Profstaff | Observer's Yes/No answer |

The application writes observations by column position. Do not rearrange these columns or insert unrelated tables into this area. Use plain header text, without backticks.

Share Google Sheet access only with people who need it. Access to the application and access to the spreadsheet are separate.

## 5. Record an evaluation

Observers should follow these steps:

1. Open the application link in their own browser profile or device.
2. Under **Observer Details**, enter **Your name**.
3. Answer **Are you a profstaff?** with **Yes** or **No**.
4. Select the room they are observing.
5. Select the current round.
6. Under **Candidate Assessment**, select the candidate.
7. Enter scores for **Team work?**, **Initiative/Problem Solving**, and **Personal Representation**.
8. Choose **Yes**, **Maybe**, or **No** for **Would you like to work with them?** Review this selection; it initially defaults to Yes.
9. Add optional notes with specific examples from the interview.
10. Click **Save Candidate Evaluation (Draft)**.

Ratings support half-point increments from 0.5 to 4. Agree on scoring expectations before interviews; the application does not define a scoring rubric.

Saving a draft does not send the evaluation to Google Sheets. Check the recorded observation before continuing. The observer name, profstaff answer, room, and round remain selected after saving a draft; always confirm them before recording the next evaluation.

The candidate list changes when the room or round changes. An Evaluated marker indicates that a candidate already has an observation in the current browser session; it does not confirm that every round has been evaluated or submitted.

## 6. Review, edit, or delete drafts

Saved observations appear under **Recorded Observations**. Use **All Rounds** or a round tab to review them.

To correct an evaluation, click **Edit**, check the details filled into the form, make changes, and click the update button. Use **Cancel Edit** to leave editing mode.

Use the delete button and confirm the prompt to remove an observation from the current browser's list.

Prefer making corrections before final submission. Editing an observation already marked **In Sheets** creates a pending revision; submitting it appends another row instead of updating the original spreadsheet row. Deleting it from the application does not remove its existing Google Sheets row. An administrator must reconcile those spreadsheet rows manually.

## 7. Submit evaluations to Google Sheets

When ready to save evaluations permanently:

1. Review the recorded observations for accuracy.
2. Find **Finalize & Send to Google Sheets**.
3. Check the pending count on **Final Submit All**.
4. Click the button and confirm submission.
5. Wait for the success message and check that submitted entries show **In Sheets**.

Final submission sends all pending evaluations in that browser session, including pending evaluations from other rounds. It does not submit another observer's drafts.

Observers can submit available drafts during the event; they do not need to wait until all three rounds finish. The administrator should confirm the expected rows appear in the observations tab.

If submission fails, drafts remain available while that server/browser session remains available. Check the observations tab before retrying if it is unclear whether rows were saved, to avoid duplicate entries.

## 8. Understand draft privacy and lifetime

Drafts belong to a browser session. There is no account sign-in.

- Tabs using the same browser profile share drafts.
- Different browsers, profiles, or machines have separate drafts.
- Private/incognito browsing is separate from normal browsing, but private windows may share a session.
- Sharing the application link does not share drafts.
- Closing one tab does not necessarily clear drafts. Browser session restoration may preserve access after reopening the browser.
- Clearing session cookies can remove access to drafts.
- A server restart or redeployment clears unsent drafts.
- Submitted Google Sheets rows remain saved after drafts disappear.

People sharing a browser profile can access that profile's drafts. Each observer should use a separate profile or device. Administrators review everyone's submitted evaluations in Google Sheets; the application does not provide an administrator view of all private drafts.

Submit important evaluations promptly. Coordinate any application redeployment with observers so they can submit pending work first.

## 9. Troubleshooting

**A candidate is missing or appears in an unexpected room:** Check the selected room and round against the rotation table. Check the candidate's group in Google Sheets, wait at least 60 seconds, and reload.

**The page warns that names could not refresh:** Check the six exact candidate headers, confirm the candidate tab was not renamed, and remove names assigned to multiple groups. The page may retain previously loaded groups, so verify assignments before proceeding. If the warning continues, contact the application maintainer to check the connection and spreadsheet permissions.

**The candidate list is empty:** Confirm names have been entered below the group headers. The selected room may correspond to an empty group.

**Drafts disappeared:** Check that the observer is using the same browser profile. A lost session cookie, server restart, or redeployment can make unsent drafts unavailable. Check Google Sheets for previously submitted work before re-entering evaluations.

**An evaluation is marked In Sheets, but needs correction:** Correct the existing row in Google Sheets, or submit a revised evaluation and manually reconcile the original row. Editing in the application does not overwrite the old spreadsheet row.

**Another observer's drafts are visible:** First check whether both people share a browser profile. If they use separate devices, contact the maintainer to verify that the browser-isolation update is deployed.

## 10. End-of-day checklist

- Ask every observer to review and submit all pending evaluations.
- Verify submissions in the observations tab.
- Check for missing candidates, rounds, scores, and observer names.
- Reconcile test rows, duplicate submissions, and revised evaluations.
- Keep spreadsheet access limited to the interview team members who need it.
- Confirm submissions before restarting or redeploying the application.
