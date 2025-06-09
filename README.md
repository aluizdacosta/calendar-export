# Google Calendar Export Tool

A Python tool to export Google Calendar events with comprehensive metadata using the Google Calendar API.

## Features

- 🔐 OAuth2 authentication with Google Calendar API
- 📅 Export events from any accessible calendar
- 🎯 Flexible date range filtering
- 📊 Rich metadata extraction including:
  - Event details (title, description, location, time)
  - Attendee information and response status
  - Recurrence rules and patterns
  - Reminders and notifications
  - Conference/meeting links
  - Creator and organizer information
- 📋 List all available calendars
- 💾 Export to structured JSON format
- 🔧 Command-line interface with multiple options

## Prerequisites

- Python 3.11 or higher
- Google Cloud Platform account
- Google Calendar API enabled

## Setup Instructions

### 1. Install Dependencies

This project uses `uv` for dependency management. Dependencies are already installed if you're reading this after following the initial setup.

### 2. Authentication Setup

You have several options for authentication:

#### **Option A: Manual Credentials (No Google Cloud Console needed)**

If you don't have access to Google Cloud Console, ask someone to create OAuth2 credentials for you, or use these commands:

```bash
# Run with manual credentials
uv run python main.py --client-id "YOUR_CLIENT_ID" --client-secret "YOUR_CLIENT_SECRET" --list-calendars

# Interactive setup
uv run python auth_example.py
```

#### **Option B: Traditional credentials.json (Requires Google Cloud Console)**

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select an existing one
3. **Enable the Google Calendar API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"
4. **Create OAuth2 credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the JSON file
5. **Save credentials**:
   - Rename the downloaded file to `credentials.json`
   - Place it in the project root directory

#### **Option C: Alternative Sources**

- **OAuth2 Playground**: Use [Google's OAuth2 Playground](https://developers.google.com/oauthplayground/)
- **Ask for help**: Get someone with Google Cloud access to create credentials
- **Free account**: Create a free Google account to access Google Cloud Console

### 3. First Run Authentication

On your first run, the tool will:

1. Open a browser window for Google OAuth2 authentication
2. Ask you to sign in and grant calendar access permissions
3. Save authentication tokens locally for future use

## Quick Start

To test your setup:

```bash
# Test help (no credentials needed)
uv run python main.py --help

# Test imports
uv run python -c "from main import GoogleCalendarExporter; print('✅ Setup working!')"

# Once you have credentials.json, list your calendars
uv run python main.py --list-calendars

# Export your calendar events
uv run python main.py
```

## Usage

### Basic Usage

Export events from your primary calendar:

```bash
uv run python main.py
```

### Command Line Options

```bash
# List all available calendars
uv run python main.py --list-calendars

# Export from a specific calendar
uv run python main.py --calendar-id "your-calendar-id@gmail.com"

# Custom date range (60 days back, 90 days forward)
uv run python main.py --days-back 60 --days-forward 90

# Custom output filename
uv run python main.py --output my_events.json

# Limit number of events
uv run python main.py --max-results 500

# Use custom credentials file
uv run python main.py --credentials my_credentials.json
```

> **Important**: Always use `uv run python` instead of just `python` to ensure the virtual environment and dependencies are properly loaded.

### Full Command Reference

```bash
uv run python main.py [OPTIONS]
```

```bash
usage: main.py [-h] [--calendar-id CALENDAR_ID] [--output OUTPUT]
               [--days-back DAYS_BACK] [--days-forward DAYS_FORWARD]
               [--max-results MAX_RESULTS] [--list-calendars]
               [--credentials CREDENTIALS]

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
```

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
      "attendees": [
        {
          "email": "attendee@example.com",
          "display_name": "John Doe",
          "response_status": "accepted",
          "optional": false
        }
      ],
      "creator": {
        "email": "creator@example.com",
        "display_name": "Jane Smith"
      },
      "organizer": {
        "email": "organizer@example.com",
        "display_name": "Jane Smith"
      },
      "status": "confirmed",
      "html_link": "https://calendar.google.com/event?eid=...",
      "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO"],
      "reminders": {
        "use_default": false,
        "overrides": [
          {
            "method": "popup",
            "minutes": 15
          }
        ]
      }
    }
  ]
}
```

## Metadata Fields

Each exported event includes comprehensive metadata:

- **Basic Info**: ID, title, description, location
- **Timing**: Start/end times, timezone, all-day flag
- **People**: Creator, organizer, attendees with response status
- **Recurrence**: Recurring event rules and patterns
- **Reminders**: Notification settings and overrides
- **Links**: Calendar links, hangout/meet links
- **Status**: Event status, visibility, transparency
- **Conference**: Video conference details

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
