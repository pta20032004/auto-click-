import json
import os
from typing import Dict, Any

from playwright.sync_api import BrowserContext, Page

class CookieManager:
    """
    Manages loading, saving, and applying cookies for session management. [cite: 103]
    """

    def load_cookies_to_context(self, context: BrowserContext, profile_path: str):
        """
        Loads cookies from a file and adds them to the browser context.
        This version is updated to handle complex JSON objects from browser extensions.
        """
        if os.path.exists(profile_path):
            print(f"Loading cookies from: {profile_path}")
            with open(profile_path, 'r') as f:
                try:
                    loaded_data = json.load(f)
                    cookies_to_load = []

                    # Check if the loaded data is a dictionary that contains a 'cookies' key
                    # This handles formats from popular cookie exporter extensions. 
                    if isinstance(loaded_data, dict) and 'cookies' in loaded_data:
                        cookies_to_load = loaded_data['cookies']
                    # Check if the loaded data is already a list (the format our app saves in)
                    elif isinstance(loaded_data, list):
                        cookies_to_load = loaded_data
                    
                    if cookies_to_load:
                        context.add_cookies(cookies_to_load)
                        print(f"Successfully loaded {len(cookies_to_load)} cookies.")
                    else:
                        print("Warning: Cookie file was found, but no valid cookies were loaded from it.")

                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON from {profile_path}. The file might be corrupted.")
                except Exception as e:
                    print(f"An unexpected error occurred while loading cookies: {e}")
        else:
            print(f"Cookie file not found: {profile_path}. Starting a new session.")

    def save_cookies_from_page(self, page: Page, profile_path: str):
        """
        Saves cookies from the current page to a file. [cite: 22, 41]
        """
        print(f"Saving cookies to: {profile_path}")
        # Ensure the directory exists
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        
        # Get all cookies from the current context
        cookies = page.context.cookies()
        
        with open(profile_path, 'w') as f:
            json.dump(cookies, f, indent=2)
        print("Cookies saved successfully.")