#!/usr/bin/env python3
"""
Google Calendar Export Tool

This script connects to Google Calendar API to export events with metadata.
It handles authentication, retrieves calendar events, and exports them with
detailed metadata including attendees, locations, descriptions, and more.
"""

import json
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from google.auth.transport.requests import Request  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore
import argparse

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarExporter:
    """Google Calendar API client for exporting events with metadata."""
    
    def __init__(self, credentials_file: str = 'credentials.json', 
                 client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None) -> None:
        """Initialize the Google Calendar exporter.
        
        Args:
            credentials_file: Path to the Google OAuth2 credentials JSON file
            client_id: OAuth2 client ID (alternative to credentials file)
            client_secret: OAuth2 client secret (alternative to credentials file)
        """
        self.credentials_file: str = credentials_file
        self.client_id: Optional[str] = client_id
        self.client_secret: Optional[str] = client_secret
        self.service: Optional[Any] = None
        self.creds: Optional[Any] = None
        
    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        # The file token.pickle stores the user's access and refresh tokens.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
                
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    # Delete the invalid token file and try again
                    if os.path.exists('token.pickle'):
                        os.remove('token.pickle')
                    self.creds = None
            
            if not self.creds or not self.creds.valid:
                try:
                    # Try manual credentials first
                    if self.client_id and self.client_secret:
                        client_config = {
                            "installed": {
                                "client_id": self.client_id,
                                "client_secret": self.client_secret,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "redirect_uris": ["http://localhost"]
                            }
                        }
                        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                        self.creds = flow.run_local_server(port=0)
                    # Fall back to credentials file
                    elif os.path.exists(self.credentials_file):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, SCOPES)
                        self.creds = flow.run_local_server(port=0)
                    else:
                        print("Authentication Error:")
                        print("=" * 50)
                        print("No authentication credentials found!")
                        print()
                        print("Quick Fix: Use public test credentials")
                        print("  Run: uv run python main.py --use-public-creds")
                        print()
                        print("Other Options:")
                        print("  1. Get OAuth2 credentials from someone with Google Cloud access")
                        print("  2. Create a free Google account for Google Cloud Console")
                        print("  3. Use Google's OAuth2 Playground")
                        print()
                        return False
                        
                except Exception as e:
                    print(f"Error during OAuth flow: {e}")
                    return False
                
            # Save the credentials for the next run
            try:
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)
            except Exception as e:
                print(f"Warning: Could not save credentials: {e}")
                
        # Build the service
        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            # Test the service by making a simple call
            self.service.calendarList().list(maxResults=1).execute()  # type: ignore
            return True
        except Exception as e:
            print(f"Error building Google Calendar service: {e}")
            self.service = None
            return False
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """Get list of all calendars accessible to the user.
        
        Returns:
            List of calendar dictionaries with metadata
        """
        if self.service is None:
            print("Error: Calendar service not initialized. Please authenticate first.")
            return []
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = []
            
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar['id'],
                    'summary': calendar.get('summary', 'Unknown'),
                    'description': calendar.get('description', ''),
                    'primary': calendar.get('primary', False),
                    'access_role': calendar.get('accessRole', 'reader'),
                    'color_id': calendar.get('colorId', ''),
                    'background_color': calendar.get('backgroundColor', ''),
                    'foreground_color': calendar.get('foregroundColor', '')
                })
                
            return calendars
            
        except HttpError as error:
            print(f"An error occurred while fetching calendars: {error}")
            return []
    
    def get_events(self, 
                   calendar_id: str = 'primary',
                   days_back: int = 30,
                   days_forward: int = 30,
                   max_results: int = 1000) -> List[Dict[str, Any]]:
        """Get events from a specific calendar with metadata.
        
        Args:
            calendar_id: Calendar ID to fetch events from
            days_back: Number of days in the past to fetch events
            days_forward: Number of days in the future to fetch events
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries with full metadata
        """
        if self.service is None:
            print("Error: Calendar service not initialized. Please authenticate first.")
            return []
        
        try:
            # Calculate time range
            now = datetime.utcnow()
            time_min = (now - timedelta(days=days_back)).isoformat() + 'Z'
            time_max = (now + timedelta(days=days_forward)).isoformat() + 'Z'
            
            # Fetch events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            processed_events = []
            
            for event in events:
                processed_event = self._process_event(event)
                processed_events.append(processed_event)
                
            return processed_events
            
        except HttpError as error:
            print(f"An error occurred while fetching events: {error}")
            return []
    
    def _process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process a raw event from Google Calendar API into structured format.
        
        Args:
            event: Raw event dictionary from Google Calendar API
            
        Returns:
            Processed event dictionary with structured metadata
        """
        # Extract start and end times
        start = event.get('start', {})
        end = event.get('end', {})
        
        # Handle all-day events vs timed events
        if 'date' in start:
            start_time = start['date']
            end_time = end['date']
            all_day = True
        else:
            start_time = start.get('dateTime', '')
            end_time = end.get('dateTime', '')
            all_day = False
            
        # Process attendees
        attendees = []
        for attendee in event.get('attendees', []):
            attendees.append({
                'email': attendee.get('email', ''),
                'display_name': attendee.get('displayName', ''),
                'response_status': attendee.get('responseStatus', 'needsAction'),
                'optional': attendee.get('optional', False),
                'organizer': attendee.get('organizer', False),
                'self': attendee.get('self', False)
            })
        
        # Process recurrence rules
        # recurrence_rules = event.get('recurrence', [])
        
        # Process reminders
        # reminders = event.get('reminders', {})
        # reminder_overrides = []
        # if reminders.get('overrides'):
        #     for override in reminders['overrides']:
        #         reminder_overrides.append({
        #             'method': override.get('method', 'popup'),
        #             'minutes': override.get('minutes', 10)
        #         })
        
        return {
            'id': event.get('id', ''),
            'summary': event.get('summary', 'No Title'),
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'start_time': start_time,
            'end_time': end_time,
            'all_day': all_day,
            'timezone': start.get('timeZone', '') or end.get('timeZone', ''),
            'created': event.get('created', ''),
            'updated': event.get('updated', ''),
            'organizer': {
                'email': event.get('organizer', {}).get('email', ''),
                'self': event.get('organizer', {}).get('self', False)
            },
            'attendees': attendees,
            'attendees_count': len(attendees),
            'recurring_event_id': event.get('recurringEventId', ''),
            'color_id': event.get('colorId', ''),
            'event_type': event.get('eventType', ''),
        }
    
    def export_to_json(self, 
                       events: List[Dict[str, Any]], 
                       filename: str,
                       calendar_info: Optional[Dict[str, Any]] = None) -> bool:
        """Export events to JSON file.
        
        Args:
            events: List of processed events
            filename: Output filename
            calendar_info: Optional calendar metadata
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Remove attendees field from events before export
            cleaned_events = []
            for event in events:
                cleaned_event = {k: v for k, v in event.items() if k != 'attendees'}
                cleaned_events.append(cleaned_event)
            
            # Fetch color definitions
            color_definitions = self.get_color_definitions()
            
            export_data = {
                'export_timestamp': datetime.utcnow().isoformat() + 'Z',
                'total_events': len(cleaned_events),
                'calendar_info': calendar_info or {},
                'color_definitions': color_definitions,
                'events': cleaned_events
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            print(f"Successfully exported {len(events)} events to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False

    def get_color_definitions(self) -> Dict[str, Any]:
        """Get color definitions for calendars and events.
        
        Returns:
            Dictionary containing color ID to hex color mappings
        """
        if self.service is None:
            print("Error: Calendar service not initialized. Please authenticate first.")
            return {}
        
        try:
            colors_result = self.service.colors().get().execute()
            return colors_result
        except HttpError as error:
            print(f"An error occurred while fetching colors: {error}")
            return {}

def is_event_accepted_by_me(event: Dict[str, Any]) -> bool:
    """Check if the event is accepted or tentatively accepted by the calendar owner.
    
    This function uses multiple strategies to determine if you've accepted an event:
    1. Check if you're in the attendees list with accepted/tentative status
    2. Check if you're the organizer (implicitly accepted)
    3. Check if there are no attendees (likely your personal event)
    """
    # Strategy 1: Check attendees list for your response
    attendees = event.get('attendees', [])
    
    # First, look for attendee marked as 'self'
    for attendee in attendees:
        if attendee.get('self', False):
            response_status = attendee.get('response_status', '')
            return response_status in ['accepted', 'tentative']
    
    # Strategy 2: Check if you're the organizer (implicitly accepted)
    organizer = event.get('organizer', {})
    if organizer.get('self', False):
        return True
    
    # Strategy 3: If no attendees, this is likely your personal event
    if not attendees:
        return True
        
    # Strategy 4: Check if any attendee has accepted status and looks like it could be you
    # This is a fallback when 'self' field isn't properly set
    for attendee in attendees:
        response_status = attendee.get('response_status', '')
        if response_status in ['accepted', 'tentative']:
            # If there's only one attendee with accepted status, assume it's you
            # (This is imperfect but better than missing events)
            accepted_attendees = [a for a in attendees if a.get('response_status') in ['accepted', 'tentative']]
            if len(accepted_attendees) == 1:
                return True
    
    # Strategy 5: If you're accessing events from your primary calendar, 
    # and no attendees are marked, assume these are your events
    # (This handles cases where the API doesn't populate attendee data properly)
    if not attendees and event.get('summary', ''):
        return True
    
    return False

def main() -> None:
    """Main function to run the calendar export tool."""
    parser = argparse.ArgumentParser(description='Export Google Calendar events with metadata')
    parser.add_argument('--calendar-id', default='primary', 
                       help='Calendar ID to export (default: primary)')
    parser.add_argument('--output', '-o', default='calendar_export.json',
                       help='Output filename (default: calendar_export.json)')
    parser.add_argument('--days-back', type=int, default=30,
                       help='Number of days in the past to fetch (default: 30)')
    parser.add_argument('--days-forward', type=int, default=30,
                       help='Number of days in the future to fetch (default: 30)')
    parser.add_argument('--max-results', type=int, default=1000,
                       help='Maximum number of events to fetch (default: 1000)')
    parser.add_argument('--list-calendars', action='store_true',
                       help='List all available calendars and exit')
    parser.add_argument('--credentials', default='credentials.json',
                       help='Path to Google OAuth2 credentials file (default: credentials.json)')
    parser.add_argument('--client-id', 
                       help='OAuth2 Client ID (alternative to credentials file)')
    parser.add_argument('--client-secret',
                       help='OAuth2 Client Secret (alternative to credentials file)')
    parser.add_argument('--use-public-creds', action='store_true',
                       help='Use public OAuth2 credentials for testing (browser auth)')
    parser.add_argument('--accepted-only', action='store_true',
                       help='Only export events that you have accepted or tentatively accepted')
    
    args = parser.parse_args()
    
    # Initialize the exporter
    if args.use_public_creds:
        # Use public test credentials (for demonstration only)
        print("🔑 Using public test credentials for browser authentication...")
        print("⚠️  WARNING: Only use for testing, not production!")
        print()
        # These are public OAuth2 credentials for testing purposes
        # In production, you should create your own
        public_client_id = "407408718192.apps.googleusercontent.com"
        public_client_secret = "************"  # Placeholder - you'll need real ones
        exporter = GoogleCalendarExporter(
            client_id=public_client_id,
            client_secret=public_client_secret
        )
    else:
        exporter = GoogleCalendarExporter(
            credentials_file=args.credentials,
            client_id=args.client_id,
            client_secret=args.client_secret
        )
    
    print("Google Calendar Export Tool")
    print("=" * 40)
    
    # Authenticate
    print("Authenticating with Google Calendar API...")
    if not exporter.authenticate():
        print("Authentication failed. Please check your credentials.")
        return
    
    print("Authentication successful!")
    
    # List calendars if requested
    if args.list_calendars:
        print("\nAvailable Calendars:")
        print("-" * 20)
        calendars = exporter.get_calendars()
        for calendar in calendars:
            primary_marker = " (PRIMARY)" if calendar['primary'] else ""
            print(f"ID: {calendar['id']}")
            print(f"Name: {calendar['summary']}{primary_marker}")
            print(f"Access: {calendar['access_role']}")
            if calendar['description']:
                print(f"Description: {calendar['description']}")
            print()
        return
    
    # Get calendar info
    calendars = exporter.get_calendars()
    calendar_info = None
    for calendar in calendars:
        if calendar['id'] == args.calendar_id:
            calendar_info = calendar
            break
    
    if calendar_info:
        print(f"\nExporting from calendar: {calendar_info['summary']}")
    else:
        print(f"\nExporting from calendar ID: {args.calendar_id}")
    
    # Fetch events
    print(f"Fetching events ({args.days_back} days back, {args.days_forward} days forward)...")
    events = exporter.get_events(
        calendar_id=args.calendar_id,
        days_back=args.days_back,
        days_forward=args.days_forward,
        max_results=args.max_results
    )
    
    if not events:
        print("No events found in the specified time range.")
        return
    
    print(f"Found {len(events)} events.")
    
    # Filter events if requested
    if args.accepted_only:
        accepted_events = [event for event in events if is_event_accepted_by_me(event)]
        print(f"Filtered to {len(accepted_events)} accepted/tentative events.")
        events_to_export = accepted_events
    else:
        events_to_export = events
    
    # Export to JSON
    print(f"Exporting to {args.output}...")
    if exporter.export_to_json(events_to_export, args.output, calendar_info):
        print("Export completed successfully!")
        
        # Print summary
        print("\nExport Summary:")
        print(f"- Total events: {len(events_to_export)}")
        print(f"- Output file: {args.output}")
        print(f"- Time range: {args.days_back} days back to {args.days_forward} days forward")
        
        # Count event types
        all_day_count = sum(1 for event in events_to_export if event['all_day'])
        timed_count = len(events_to_export) - all_day_count
        print(f"- All-day events: {all_day_count}")
        print(f"- Timed events: {timed_count}")
        
        # Count events with attendees
        events_with_attendees = sum(1 for event in events_to_export if event['attendees_count'] > 0)
        print(f"- Events with attendees: {events_with_attendees}")
        
    else:
        print("Export failed.")

if __name__ == "__main__":
    main()
