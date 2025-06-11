#!/usr/bin/env python3
"""
Interactive authentication setup example for Google Calendar Export Tool.

This script helps users set up authentication for the Google Calendar API
by providing step-by-step instructions and testing the setup.
"""

import os
import sys
from pathlib import Path

def main():
    """Interactive authentication setup guide."""
    print("🔐 Google Calendar Export Tool - Authentication Setup")
    print("=" * 60)
    print()
    
    # Check if credentials.json exists
    creds_file = Path("credentials.json")
    
    if creds_file.exists():
        print("✅ Found credentials.json file")
        print("Testing authentication...")
        
        # Test authentication
        try:
            from main import GoogleCalendarExporter
            
            exporter = GoogleCalendarExporter()
            if exporter.authenticate():
                print("✅ Authentication successful!")
                print("You can now use the calendar export tool.")
                print()
                print("Try these commands:")
                print("  uv run python main.py --list-calendars")
                print("  uv run python main.py")
            else:
                print("❌ Authentication failed")
                print("Please check your credentials.json file and try again.")
                
        except Exception as e:
            print(f"❌ Error during authentication test: {e}")
            print("Please ensure all dependencies are installed with: uv sync")
    
    else:
        print("❌ credentials.json not found")
        print()
        print("To get OAuth2 credentials:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com)")
        print("2. Create or select a project")
        print("3. Enable the Google Calendar API")
        print("4. Create OAuth2 credentials (Desktop application)")
        print("5. Download the credentials.json file to this directory")
        print()
        print("Once you have credentials.json, run this script again to test authentication.")

if __name__ == "__main__":
    main() 