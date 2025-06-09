#!/usr/bin/env python3
"""
Example usage of the Google Calendar Exporter

This script demonstrates how to use the GoogleCalendarExporter class
programmatically without using the command-line interface.

Run this script with: uv run python example.py
"""

from main import GoogleCalendarExporter

def main() -> None:
    """Example of programmatic usage."""
    
    # Initialize the exporter
    exporter = GoogleCalendarExporter()
    
    print("=== Google Calendar Export Example ===")
    
    # Authenticate
    print("\n1. Authenticating...")
    if not exporter.authenticate():
        print("Authentication failed!")
        return
    
    print("Authentication successful!")
    
    # List calendars
    print("\n2. Available calendars:")
    calendars = exporter.get_calendars()
    for i, calendar in enumerate(calendars, 1):
        primary = " (PRIMARY)" if calendar['primary'] else ""
        print(f"   {i}. {calendar['summary']}{primary}")
        print(f"      ID: {calendar['id']}")
        print(f"      Access: {calendar['access_role']}")
        print()
    
    # Get events from primary calendar
    print("3. Fetching recent events from primary calendar...")
    events = exporter.get_events(
        calendar_id='primary',
        days_back=7,      # Last 7 days
        days_forward=7,   # Next 7 days
        max_results=10    # Limit to 10 events
    )
    
    print(f"Found {len(events)} events")
    
    # Display some event information
    if events:
        print("\n4. Sample events:")
        for i, event in enumerate(events[:3], 1):  # Show first 3 events
            print(f"   {i}. {event['summary']}")
            print(f"      Start: {event['start_time']}")
            print(f"      All-day: {event['all_day']}")
            if event['location']:
                print(f"      Location: {event['location']}")
            if event['attendees']:
                print(f"      Attendees: {len(event['attendees'])}")
            print()
    
    # Export to JSON
    print("5. Exporting to example_export.json...")
    calendar_info = calendars[0] if calendars else None  # Use first calendar info
    
    if exporter.export_to_json(events, 'example_export.json', calendar_info):
        print("Export successful!")
        
        # Show some statistics
        all_day_events = sum(1 for event in events if event['all_day'])
        events_with_attendees = sum(1 for event in events if event['attendees'])
        
        print(f"\nExport statistics:")
        print(f"- Total events: {len(events)}")
        print(f"- All-day events: {all_day_events}")
        print(f"- Events with attendees: {events_with_attendees}")
        
    else:
        print("Export failed!")

if __name__ == "__main__":
    main() 