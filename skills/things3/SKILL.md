---
name: things3
description: "Things 3 via AppleScript: todos, projects, areas, tags."
version: 1.0.0
author: neo-anderson
license: MIT
platforms: [macos]
prerequisites:
  commands: [osascript]
metadata:
  hermes:
    tags: [Things, tasks, todo, macOS, Apple, AppleScript, Productivity]
  openclaw:
    emoji: "\U0001F4C5"
    requires:
      bins: [osascript]
      os: [darwin]
---
# Things 3 (AppleScript)

Drive Things 3 from the terminal with `osascript`. The app's process/app name is **"Things3"** (not "Things"). Source: https://culturedcode.com/things/support/articles/4562654/

## When to Use

- User mentions "Things", "Things 3", or the Things sidebar (Inbox/Today/Upcoming/Someday)
- Capturing, scheduling, completing, or reorganizing to-dos/projects/areas/tags in Things
- Bulk-reading Things data for reporting/review

## When NOT to Use

- Apple Reminders → use the `apple-reminders` skill (remindctl)
- Calendar events → google-workspace / Apple Calendar
- Editing headings or checklists inside a to-do → not scriptable; Apple Shortcuts only
- Scheduling agent alerts about tasks → your agent client's scheduler/cron tool

## Running scripts

```bash
osascript <<'EOF'
tell application "Things3"
	-- commands here
end tell
EOF
```

- First invocation triggers a macOS Automation permission prompt for the controlling app (Terminal/your agent app); the user must allow it once.
- Agent clients typically gate `osascript` behind an approval prompt; scripts passed via file/pipe can attract stricter review — keep scripts inline and reviewable where possible.
- For multi-line AppleScript with quoting trouble, write a `.applescript` file and run `osascript file.applescript`.

## Performance rule (critical, measured on a ~6,000-item list)

Never `repeat with x in <collection>` reading one property per element: each read is an IPC round-trip (18k reads > 180s). Instead batch-fetch whole properties with `get <prop> of every ...` — 6k items in ~0.9s.

Dump recipe (join per-property linefeed blocks by known count N; to-do names never contain newlines):

```applescript
tell application "Things3"
	set theNames to get name of every to do of list "Today"
	set theIds to get id of every to do of list "Today"
	set theStatus to get status of every to do of list "Today"
end tell
set AppleScript's text item delimiters to linefeed
return (theNames as string) & "\n" & (theIds as string) & "\n" & (theStatus as string)
```

Parse in Python: lines[0:N]=names, [N:2N]=ids, [2N:3N]=status. `id` is Things' short UUID (e.g. `aB3cD5eF7gH9iJ2kL4mN`) — good cross-reference key.

## Built-in lists

`list "Inbox"` / `"Today"` / `"Anytime"` / `"Upcoming"` / `"Someday"` / `"Logbook"` / `"Trash"`. Predefined — `make` can't create them. In non-English Things, use the localized name as shown in the app. Collection order matches the UI (Upcoming is sorted by start date).

## To-dos

```applescript
to dos                          -- all to-dos
to do named "Call mom"          -- by name (also: to do "Call mom")
to dos of list "Inbox"
to dos of project "Vacation in Rome"
to dos of area "Family"
first to do of list "Inbox"     -- first item in UI order

-- create (optionally `at beginning of/end of` a list, project, or area;
-- or plain `tell <container>` block)
set newToDo to make new to do with properties {name:"New to-do", due date:current date} ¬
	at beginning of list "Today"
tell project "Groceries"
	set newToDo to make new to do with properties {name:"Buy bread"}
end tell

-- set properties (bulk record at creation, or one at a time)
set name of newToDo to "Renamed"
set notes of newToDo to "www.apple.com" & linefeed & "Call for details."
set due date of newToDo to (current date) + 7 * days
set tag names of newToDo to "Home, Mac"

-- delete (moves to Trash)
delete to do named "To-do to remove"
```

Properties: `name`, `notes`, `due date`, `start date`, `completion date`, `creation date`, `modification date`, `cancellation date`, `status` (open/completed/canceled), `tag names`, `area`, `project`, `id`, `to dos`, `tags`.

**Gotcha:** `due date` = deadline only, not the start date. To put something in Upcoming with a start date use `schedule` (below).

## Projects & areas

Same shape as to-dos: `projects` / `areas` collections, `project "Name"` / `area "Name"`, `make new project with properties {name:"...", notes:"..."}`, `make new area with properties {name:"Health"}`, `delete`.

- Deleting a **project** trashes the project and its children.
- Deleting an **area** removes only the area; its children go to the Trash.
- Area property-setting supports `name` and `tag names` (no due dates etc.).

## Tags

```applescript
tags                                    -- all tags (objects)
tag names of aToDo                      -- string: "Home, Mac"
tags of aToDo                           -- list of tag objects
set tag names of aToDo to "Home, Mac"   -- set (replaces all)
set name of tag "Errands" to "Shopping" -- rename everywhere
delete tag "Errands"
```

Hierarchy: `set parent tag of tag "Home" to tag "Places"`.

## Moving items

```applescript
move newToDo to list "Today"
move finishedProject to list "Logbook"

-- complete/cancel (also moves to Logbook)
set status of aToDo to completed
set status of aToDo to canceled

-- Upcoming: move FAILS; use schedule (= sets start date)
schedule aToDo for (current date) + 1 * days

-- re-parent
set project of aToDo to project "Groceries"
set area of aToDo to area "Shopping"
set area of aProject to area "Home"

-- detach WITHOUT deleting parent (delete the RELATIONSHIP, not the object)
delete project of orphanToDo
delete area of orphanProject
```

## UI interactions

```applescript
selected to dos                    -- what the user has selected in the app
show to do "Book flights"          -- reveal item in Things
show project "Vacation in Rome"
show area "Personal"
edit newToDo                       -- reveal + expand for editing (NOT for areas)

show quick entry panel                                        -- empty popover
show quick entry panel with properties {name:"Buy flowers", notes:"..."}
show quick entry panel with autofill yes                     -- grab from frontmost app
```

## Other actions

```applescript
set tag names of newToDo to ""   -- clear a property ("" = nil)
empty trash
log completed now                -- when Things logging is set to Manually
```

Notes accept links: a `file:///path` or web URL in `notes` becomes clickable in Things.

## Limits

- Mac-only; if a feature isn't in the article above, AppleScript can't do it. Headings and checklists are NOT scriptable — suggest Apple Shortcuts for those.
- Things' full dictionary: Script Editor → File → Open Dictionary… → Things.
- `delete` moves to-dos/projects to Trash (recoverable); `empty trash` is not.

## Recipes

Add a to-do from the current directory context and confirm it landed:

```bash
osascript -e 'tell application "Things3" to make new to do with properties {name:"Fix login bug", notes:"file://'"$PWD"'"}'
osascript -e 'tell application "Things3" to get name of first to do of list "Inbox"'   -- verify
```

Complete Today's items older than a cutoff, then verify by re-counting `to dos of list "Today"`.

## Rules

1. Always verify writes with a follow-up read (`get name of first to do of list "Inbox"`) before reporting success.
2. Use batch `get ... of every ...` for anything over ~50 items.
3. `schedule` for start dates / Upcoming; `due date` is the deadline.
4. Deleting an item's `project`/`area` PROPERTY detaches; deleting the item trashes.
