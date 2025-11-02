# Notion Checklists

This project automates the "next due" dates for items stored in a Notion database. It reads your database configuration from `settings.yml`, calculates the next occurrence for each checklist entry based on custom recurrence rules, and writes the result back to Notion using the public API.

## Features

- Pulls active checklist items from a Notion database.
- Computes the next occurrence date from custom interval rules.
- Updates both the `Next Date` property and (optionally) a `Scheduled` property in Notion.
- Supports complex schedules such as weekly, monthly, quarterly, and yearly recurrences.

## Requirements

- Python 3.9+
- A Notion integration token with read/write access to the checklist database.
- The following Python packages (installable with `pip`):
  - `requests`
  - `ruamel.yaml`
  - `python-dateutil`
  - `cryptocode`

```bash
pip install requests ruamel.yaml python-dateutil cryptocode
```

## Configuration

1. Copy the provided template and rename it to `settings.yml`:

   ```bash
   cp "settings - Copy.yml" settings.yml
   ```

2. Edit `settings.yml` with your own values:

   ```yaml
   notion:
     token: "secret_xxx"              # Notion integration token
     checklist_db: "xxxxxxxx"         # Checklist database ID
     type: Type                        # Select property that stores the interval (e.g. "Monthly")
     units: Units                      # Select property that stores the interval pattern (e.g. "Week-Day")
     number: on                        # Text/number property with the pattern value (e.g. "2-5")
     last_date:                        # One or more date properties containing the last completed date
       - previous
       - previous_raw
     next_date: next_date              # Date property that will store the next occurrence
     scheduled: Scheduled              # (Optional) Date property to mirror the next occurrence
   options:
     use_scheduled: true               # If true, also write to the scheduled property
   ```

   - The names on the right-hand side (e.g. `Type`, `Units`, `on`) must match the property names in your Notion database.
   - `last_date` can list several properties. The script will pick the most recent date across them.

## Notion Database Expectations

The script expects the database to have at least the following properties:

| Property            | Type                 | Purpose                                           |
|---------------------|----------------------|---------------------------------------------------|
| `Name`              | Title                | Display name of the checklist item.               |
| `Status`            | Select               | Only items with value `Active` are processed.     |
| `Type`              | Select               | Interval category (see [Interval Rules](#interval-rules)). |
| `Units`             | Select               | Specifies the pattern that accompanies `Type`.    |
| `on`                | Text/Number          | Stores the recurrence values (comma separated).   |
| `previous`          | Date (example)       | Last completion date (listed in `last_date`).     |
| `previous_raw`      | Date (example)       | Optional additional last-date property.           |
| `next_date`         | Date                 | Updated with the calculated next occurrence.      |
| `Scheduled`         | Date (optional)      | Updated when `options.use_scheduled` is `true`.   |

You may rename these properties, provided you update the references in `settings.yml` accordingly.

## Running the Checklist Update

After configuring the settings file, run the updater:

```bash
python run_checklists.py
```

The script will:

1. Read your Notion settings.
2. Fetch every page in the target database whose `Status` is `Active`.
3. Determine the most recent completion date across the configured `last_date` properties.
4. Calculate the next due date based on the interval fields.
5. Write the new date to `next_date` (and `Scheduled`, if enabled).

Any errors encountered for individual pages are logged to the console, and processing continues for the remaining items.

## Interval Rules

The recurrence logic is controlled by three fields:

- **Type** (`settings.notion.type`): The high-level cadence.
- **Units** (`settings.notion.units`): How to interpret the values in the `number` field.
- **on** (`settings.notion.number`): The actual pattern values. Multiple values can be comma separated (e.g. `1,15`).

The combinations understood by `run_checklists.py` are summarised below.

| Type       | Units / Pattern            | `on` value format                        | Description |
|------------|----------------------------|-------------------------------------------|-------------|
| `Daily`    | *(ignored)*                | *(ignored)*                               | Always schedules for the next day. |
| `Interval` | `Day`, `Week`, or `Month`  | Integer count (e.g. `3`)                  | Adds the specified number of days, weeks, or months to the last date. |
| `Weekly`   | `Day`                      | ISO weekday number (`1`=Mon … `7`=Sun)    | Finds the next matching weekday after the last date. |
| `Monthly`  | `Day`                      | Day of month (`15`) or `0` for last day.  | Schedules for the next month/day occurrence. |
| `Monthly`  | `Week-Day`                 | `week-day` (e.g. `2-5` = second Friday)   | Targets the nth weekday of the month; use `0` for the last occurrence (e.g. `0-1` = last Monday). |
| `Quarterly`| `Month-Day`                | `month-day` within the quarter (`2-10`)   | Uses the nth month of the quarter (1–3) and day of month. |
| `Quarterly`| `Month-Week-Day`           | `month-week-day` (e.g. `3-1-2`)           | Month within the quarter (1–3), week of month, ISO weekday. |
| `Quarterly`| `Day`                      | Day of the quarter (`45`, `0` for last).  | Counts days from the start of the quarter. |
| `Yearly`   | `Month-Day`                | `month-day` (e.g. `12-31`)                | Specific date each year. |
| `Yearly`   | `Month-Week-Day`           | `month-week-day` (e.g. `11-4-4`)          | e.g. fourth Thursday in November. |
| `Yearly`   | `Month`                    | Month number (`7`)                        | Uses the first day of that month. |
| `Yearly`   | `Week`                     | ISO week number (`23`)                    | Uses the first day of that ISO week. |
| `Yearly`   | `Week-Day`                 | `week-day`                                | Combines ISO week and weekday. |
| `Yearly`   | `Day`                      | Day of year (`256`)                       | Day number within the year. |

If multiple values are provided in the `on` property (e.g. `1,15` for two monthly triggers), the script calculates the next date for each value and keeps the earliest one after the last completion date.

## Troubleshooting

- Ensure the Notion integration token has been shared with the target database.
- Verify that every property referenced in `settings.yml` exists in the database and matches the expected type.
- If a page has never been completed (i.e. no `last_date` values), the script starts from the current day.
- Run with `options.use_scheduled: false` if you do not maintain a separate scheduled field in Notion.

## License

This project is released under the terms of the [MIT License](LICENSE).
