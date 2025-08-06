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
        Loads cookies from a file and adds them to the browser context. [cite: 21, 40]
        This should be done before navigating to any page.
        """
        if os.path.exists(profile_path):
            print(f"Loading cookies from: {profile_path}")
            with open(profile_path, 'r') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
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