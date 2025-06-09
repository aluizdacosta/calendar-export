#!/usr/bin/env python3
"""
Authentication Example without credentials.json

This example shows how to use the calendar exporter without having 
access to Google Cloud Console to create credentials.json.

Run this script with: uv run python auth_example.py
"""

from main import GoogleCalendarExporter

def main() -> None:
    """Example authentication without credentials.json file."""
    
    print("Google Calendar Authentication Example")
    print("=" * 45)
    print()
    
    # Option 1: Use public OAuth2 credentials (for testing only)
    print("Option 1: Using manually provided credentials")
    print("-" * 45)
    
    # Ask user for credentials
    print("You need OAuth2 Client ID and Secret.")
    print("Get them from: https://console.developers.google.com/")
    print("Or ask someone with Google Cloud access to create them for you.")
    print()
    
    client_id = input("Enter Client ID (or press Enter to skip): ").strip()
    client_secret = input("Enter Client Secret (or press Enter to skip): ").strip()
    
    if client_id and client_secret:
        print("\nTrying to authenticate with provided credentials...")
        exporter = GoogleCalendarExporter(
            client_id=client_id,
            client_secret=client_secret
        )
        
        if exporter.authenticate():
            print("✅ Authentication successful!")
            
            # Test by listing calendars
            calendars = exporter.get_calendars()
            print(f"Found {len(calendars)} calendars:")
            for calendar in calendars[:3]:  # Show first 3
                primary = " (PRIMARY)" if calendar['primary'] else ""
                print(f"  - {calendar['summary']}{primary}")
            
            return
        else:
            print("❌ Authentication failed with provided credentials")
    
    print("\nAlternative Solutions:")
    print("=" * 45)
    print("1. Ask someone to create OAuth2 credentials for you")
    print("2. Use Google's OAuth2 Playground: https://developers.google.com/oauthplayground/")
    print("3. Create a free Google Cloud account (if possible)")
    print("4. Use a different calendar service that doesn't require OAuth2 setup")
    print()
    print("For now, you can also try the command line with manual credentials:")
    print("uv run python main.py --client-id YOUR_ID --client-secret YOUR_SECRET --list-calendars")

if __name__ == "__main__":
    main() 