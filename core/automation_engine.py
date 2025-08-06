# core/automation_engine.py

import time
import os
import json
from typing import Dict, Any, List

from playwright.sync_api import Playwright, Browser, Page, BrowserContext, sync_playwright

from .exceptions import CoordinateOutOfBoundError, ActionNotFoundError


class AutomationEngine:
    """
    The core engine, now upgraded to use Playwright's storage_state
    for more reliable session management.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    def __enter__(self):
        """
        Starts Playwright and sets up the browser context.
        This final version robustly cleans the storage state, handling all known
        'sameSite' attribute inconsistencies including case-sensitivity.
        """
        self.playwright = sync_playwright().start()
        settings = self.config.get("settings", {})
        auth_config = self.config.get("authentication", {})
        
        storage_state = None # Start with no state
        storage_state_path = auth_config.get("profile_path") if auth_config.get("enabled", False) else None

        if storage_state_path and os.path.exists(storage_state_path):
            print(f"Loading and cleaning authentication state from: {storage_state_path}")
            try:
                with open(storage_state_path, 'r') as f:
                    state_from_file = json.load(f)
                
                # Robustly clean the 'sameSite' attribute in cookies
                if 'cookies' in state_from_file:
                    for cookie in state_from_file['cookies']:
                        if 'sameSite' in cookie:
                            # Normalize the value to lowercase for consistent comparison
                            samesite_value = str(cookie['sameSite']).lower()
                            
                            if samesite_value == 'strict':
                                cookie['sameSite'] = 'Strict'
                            elif samesite_value == 'lax':
                                cookie['sameSite'] = 'Lax'
                            # Handle both 'none' and the common 'no_restriction' from extensions
                            elif samesite_value in ['none', 'no_restriction']:
                                cookie['sameSite'] = 'None'
                            # If it's still not a valid value, it's safer to remove the key
                            # to let the browser apply its default.
                            elif cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                                del cookie['sameSite']

                storage_state = state_from_file
                print("Authentication state cleaned successfully.")
            except Exception as e:
                print(f"Failed to load or clean authentication state: {e}")
                storage_state = None # Ensure we start a fresh session on failure

        elif storage_state_path:
            print(f"Authentication state file not found: {storage_state_path}. Starting a new session.")

        self.browser = getattr(self.playwright, settings.get("browser", "chromium")).launch(
            headless=settings.get("headless", True)
        )
        
        # Create context using the cleaned state object
        self.context = self.browser.new_context(storage_state=storage_state)
        self.page = self.context.new_page()
        
        self._standardize_viewport()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("Automation finished. Browser closed.")

    def _standardize_viewport(self):
        viewport_config = self.config["settings"]["viewport"]
        width = viewport_config["width"]
        height = viewport_config["height"]
        print(f"Standardizing viewport to: {width}x{height}")
        self.page.set_viewport_size({"width": width, "height": height})
        zoom_level = self.config["settings"].get("zoom_level", 1.0)
        print(f"Locking zoom level to: {zoom_level * 100}%")
        self.page.evaluate(f"document.body.style.zoom = '{zoom_level}'")

    def _validate_coordinates(self, x: int, y: int):
        viewport = self.page.viewport_size
        if not (0 <= x < viewport["width"] and 0 <= y < viewport["height"]):
            raise CoordinateOutOfBoundError(x, y, viewport["width"], viewport["height"])
            
    def _save_session_state(self, params: Dict[str, Any]):
        """Saves the entire browser state (cookies, localStorage) to a file."""
        # Use path from params if provided, otherwise from main auth config
        profile_path = params.get("profile_path") or self.config.get("authentication", {}).get("profile_path")
        if not profile_path:
            print("Error: No profile_path specified for saving session.")
            return

        print(f"Saving authentication state to: {profile_path}")
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        
        state = self.context.storage_state()
        with open(profile_path, 'w') as f:
            json.dump(state, f, indent=2)
        print("Authentication state saved successfully.")


    def run_workflow(self):
        workflow_steps: List[Dict[str, Any]] = self.config.get("workflow", [])
        print("Starting workflow execution...")
        for i, step in enumerate(workflow_steps):
            action = step.get("action")
            params = step.get("params", {})
            description = step.get("description", "No description")
            print(f"\n[Step {i+1}/{len(workflow_steps)}] Action: {action.upper()} - {description}")
            try:
                self.execute_action(action, params)
            except Exception as e:
                print(f"ERROR at step {i+1} ({action}): {e}")
                self.page.screenshot(path=f"screenshots/error_step_{i+1}.png")
                break
        print("\nWorkflow finished.")

    def execute_action(self, action: str, params: Dict[str, Any]):
        if action == "goto":
            self.page.goto(params["url"])
        elif action == "click":
            x, y = params["x"], params["y"]
            self._validate_coordinates(x, y)
            # Sửa lỗi logic: Dùng if/else để gọi đúng hàm click hoặc dblclick
            if params.get("double_click", False):
                self.page.mouse.dblclick(x, y)
            else:
                self.page.mouse.click(x, y)
        elif action == "type":
            if "x" in params and "y" in params:
                self.page.mouse.click(params["x"], params["y"])
            if params.get("clear_first", False):
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Delete")
            self.page.keyboard.type(params["text"])
        elif action == "wait":
            time.sleep(params["milliseconds"] / 1000.0)
        elif action == "screenshot":
            os.makedirs(os.path.dirname(params["path"]), exist_ok=True)
            self.page.screenshot(path=params["path"])
        elif action == "save_session": # Changed from save_cookies
            self._save_session_state(params)
        elif action == "upload":
            x, y, file_path = params["x"], params["y"], params["file_path"]
            self._validate_coordinates(x, y)
            with self.page.expect_file_chooser() as fc_info:
                self.page.mouse.click(x, y)
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)
        else:
            raise ActionNotFoundError(action)