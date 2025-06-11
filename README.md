# Google Calendar Export Tool

A comprehensive Python tool for exporting Google Calendar events with detailed metadata. Export your calendar data to JSON format with complete event information including attendees, locations, timestamps, and more.

## Features

- **Complete Event Data**: Export all event metadata including attendees, descriptions, locations, and timing
- **Flexible Time Ranges**: Customize how far back and forward to fetch events
- **Event Filtering**: Export only events you've accepted or tentatively accepted  
- **Multiple Calendar Support**: Export from any calendar you have access to
- **Rich Metadata**: Includes colors, recurrence patterns, reminders, and conference details
- **JSON Output**: Clean, structured JSON format perfect for analysis and processing

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Google Calendar API credentials (`credentials.json`)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd calendar-export
```

### 2. Install Dependencies

This project uses `uv` for dependency management:

```bash
uv sync
```

### 3. Get Google Calendar API Credentials

You need OAuth2 credentials from Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create OAuth2 credentials (Desktop application type)
5. Download the `credentials.json` file to the project directory

### 4. Run the Tool

```bash
# Export calendar events (requires authentication on first run)
uv run python main.py

# List available calendars
uv run python main.py --list-calendars

# Export from specific calendar with custom settings
uv run python main.py --calendar-id "your-calendar-id" --days-back 60 --days-forward 90
```

## Authentication

The tool uses OAuth2 authentication via Google Cloud Console credentials:

1. **First Run**: Opens browser for Google OAuth consent
2. **Subsequent Runs**: Uses saved token (`token.pickle`) for authentication
3. **Credentials File**: Place your `credentials.json` in the project directory

### Troubleshooting Authentication

- **Missing credentials**: Ensure `credentials.json` exists in the current directory
- **Token expired**: Delete `token.pickle` and re-authenticate
- **Permission denied**: Enable Google Calendar API in Google Cloud Console

## Usage Examples

```bash
# Basic export (30 days back, 30 days forward)
uv run python main.py

# Custom time range
uv run python main.py --days-back 90 --days-forward 180

# Export only accepted events
uv run python main.py --accepted-only

# Export to custom file
uv run python main.py --output my_calendar.json

# Export from specific calendar
uv run python main.py --calendar-id "work-calendar@company.com"

# Combine options
uv run python main.py --accepted-only --days-back 180 --output accepted_events.json
```

### Full Command Reference

```bash
uv run python main.py [OPTIONS]
```

```bash
usage: main.py [-h] [--calendar-id CALENDAR_ID] [--output OUTPUT]
               [--days-back DAYS_BACK] [--days-forward DAYS_FORWARD]
               [--max-results MAX_RESULTS] [--list-calendars]
               [--credentials CREDENTIALS] [--accepted-only]

Export Google Calendar events with metadata

options:
  -h, --help            show this help message and exit
  --calendar-id CALENDAR_ID
                        Calendar ID to export (default: primary)
  --output OUTPUT, -o OUTPUT
                        Output filename (default: calendar_export.json)
  --days-back DAYS_BACK
                        Number of days in the past to fetch (default: 30)
  --days-forward DAYS_FORWARD
                        Number of days in the future to fetch (default: 30)
  --max-results MAX_RESULTS
                        Maximum number of events to fetch (default: 1000)
  --list-calendars      List all available calendars and exit
  --credentials CREDENTIALS
                        Path to Google OAuth2 credentials file (default: credentials.json)
  --accepted-only       Only export events that you have accepted or tentatively accepted
```

> **Important**: Always use `uv run python` instead of just `python` to ensure the virtual environment and dependencies are properly loaded.

## Event Filtering

### Accepted Events Only

You can filter events to only include those you have accepted or tentatively accepted using the `--accepted-only` flag:

```bash
# Export only events you've accepted
uv run python main.py --accepted-only
```

This filter works by checking:
- **Your response status** in the attendees list (`accepted` or `tentative`)  
- **Organizer status** - Events you organize are automatically included
- **Self identification** - Uses the `self` field in attendee/organizer data

### Understanding Response Status

The tool recognizes these response statuses:
- `accepted` - You have confirmed attendance
- `tentative` - You have tentatively accepted  
- `declined` - You have declined (excluded when using `--accepted-only`)
- `needsAction` - No response yet (excluded when using `--accepted-only`)

### Use Cases for Filtering

- **Time analysis**: See only events that count toward your actual time commitment
- **Calendar cleanup**: Export confirmed events for migration or backup
- **Meeting reports**: Focus on events you actually participated in
- **Personal analytics**: Analyze your confirmed commitments vs total invitations

## Output Format

The tool exports events to JSON with the following structure:

```json
{
  "export_timestamp": "2024-01-15T10:30:00Z",
  "total_events": 25,
  "calendar_info": {
    "id": "primary",
    "summary": "Your Calendar",
    "primary": true,
    "access_role": "owner"
  },
  "events": [
    {
      "id": "event_id_here",
      "summary": "Meeting Title",
      "description": "Meeting description",
      "location": "Conference Room A",
      "start_time": "2024-01-15T14:00:00-08:00",
      "end_time": "2024-01-15T15:00:00-08:00",
      "all_day": false,
      "timezone": "America/Los_Angeles",
      "organizer": {
        "email": "organizer@example.com",
        "display_name": "Jane Smith",
        "self": true
      },
      "color_id": "11",
      "event_type": "default",
    }
  ]
}
```

## Metadata Fields

Each exported event includes comprehensive metadata:

- **Basic Info**: ID, title, description, location
- **Timing**: Start/end times, timezone, all-day flag
- **People**: Creator, organizer, attendees with detailed response status and self-identification
- **Colors**: Color ID and categorization for visual organization
- **Recurrence**: Recurring event rules and patterns
- **Reminders**: Notification settings and overrides
- **Links**: Calendar links, hangout/meet links
- **Status**: Event status, visibility, transparency
- **Conference**: Video conference details

### Enhanced Attendee Data

Each attendee entry now includes:
- `email` - Attendee's email address
- `display_name` - Attendee's display name
- `response_status` - Response: `accepted`, `tentative`, `declined`, or `needsAction`
- `optional` - Whether attendance is optional
- `organizer` - Whether this attendee is the organizer
- `self` - Whether this attendee represents you (the calendar owner)

### Color Information

Events now include color metadata:
- `color_id` - Google Calendar color ID (e.g., "11" for red)
- `event_type` - Event type classification
- Use the Colors API to map color IDs to actual hex values

## Troubleshooting

### Authentication Issues

1. **"credentials.json not found"**: Download OAuth2 credentials from Google Cloud Console
2. **"Access denied"**: Ensure Google Calendar API is enabled in your project
3. **"Token expired"**: Delete `token.pickle` file and re-authenticate

### API Limits

- Google Calendar API has usage quotas (typically 1,000,000 requests/day)
- Rate limiting: 100 requests per 100 seconds per user
- Batch requests can help with large exports

### Common Issues

- **No events found**: Check date range and calendar permissions
- **Permission denied**: Ensure you have access to the specified calendar
- **Invalid calendar ID**: Use `--list-calendars` to find correct IDs

## Development

The project uses `uv` for dependency management:

```bash
# Add new dependencies
uv add package-name

# Add development dependencies
uv add --dev package-name

# Run your application
uv run python main.py

# Run the example script
uv run python example.py

# Update dependencies
uv lock --upgrade

# Install dependencies on a new machine
uv sync
```

## Important Notes

- **Always use `uv run`**: This project requires `uv run python` instead of just `python`
- **Virtual environment**: `uv` automatically manages the virtual environment in `.venv/`
- **Dependencies**: All Google API dependencies are isolated in the project environment

## License

This project is open source. Feel free to modify and distribute as needed.

## Security Notes

- Keep your `credentials.json` file secure and never commit it to version control
- The `token.pickle` file contains access tokens - treat it as sensitive data
- Consider using service account credentials for production deployments
