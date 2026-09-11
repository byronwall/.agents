---
name: create-calendar-entry
description: Create and verify macOS Calendar events for Byron Wall. Use when the user asks to add, schedule, put, or create an event, appointment, meeting, activity, or reminder-like item on Byron's personal calendar or the ByronAnne joint calendar, including when event details come from a selected email, screenshot, webpage, or pasted text.
---

# Create Calendar Entry

Create an accurate event with minimal back-and-forth while respecting the computer-use confirmation policy.

## Calendar mapping

- Map `personal`, `my calendar`, `mine`, or `Byron` to `byron@byroni.us`.
- Map `joint`, `our calendar`, `family`, `shared`, or `ByronAnne` to `byronanne@byroni.us`.
- Treat the mapped account calendar itself as the destination, not another calendar nested under that account.
- Ask which calendar only when the user's wording does not resolve the destination. Never silently guess between the two.

## Build the event

1. Extract the title, date, start time, end time, location, recurrence, and target calendar from the user's words and visible source material.
2. Resolve relative dates using the current local date and `America/Indiana/Indianapolis` unless the source explicitly gives another timezone.
3. Check that a stated weekday agrees with the date. Surface conflicts before creating anything.
4. If a timed event lacks an end time, use a one-hour duration and disclose it in the confirmation summary. Do not invent recurrence, alerts, attendees, or notes.
5. Keep the title concise. Put a venue or address in Calendar's location field rather than appending it to the title.
6. Never add attendees or send invitations unless the user explicitly requests that action.

## Create it in Calendar

1. Prefer a purpose-built calendar connector if one is available. Otherwise invoke the `computer-use` skill and control macOS Calendar.
2. Inspect the target date and target calendar for an exact or clearly equivalent event before creating a duplicate.
3. Select the mapped calendar in Calendar's sidebar or event editor.
4. Prepare the UI as far as safely possible, then present one compact confirmation containing the title, date, time range, location, and calendar. Follow the computer-use confirmation policy: creating or modifying an event requires action-time confirmation, and entering an address into a shared calendar may itself transmit sensitive data.
5. After confirmation, enter the details and save without asking again unless the details materially change.
6. Prefer the full event editor when quick entry would mix the title and location. Set the title and location fields independently.
7. Verify the saved event from fresh Calendar state. Confirm the exact calendar, date, start and end times, title, and location.
8. If verification fails, inspect the editor and correct the existing event. Recheck for duplicates before retrying creation.

## Response

Report the created event in one compact summary. If an existing equivalent event prevented creation, report that instead. Do not claim success until Calendar state verifies it.
