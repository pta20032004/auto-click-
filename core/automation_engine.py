import time
from typing import Dict, Any, List
import os
from playwright.sync_api import Playwright, Browser, Page, BrowserContext, sync_playwright

from .cookie_manager import CookieManager
from .exceptions import CoordinateOutOfBoundError, ActionNotFoundError


class AutomationEngine:
    """
    The core engine for driving web automation tasks based on a configuration file.
    It handles browser setup, viewport standardization, and workflow execution.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the engine with the provided configuration. [cite: 74]
        """
        self.config = config
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.cookie_manager = CookieManager()

    def __enter__(self):
        """
        Starts Playwright and sets up the browser context.
        """
        self.playwright = sync_playwright().start()
        settings = self.config.get("settings", {})
        
        self.browser = getattr(self.playwright, settings.get("browser", "chromium")).launch(
            headless=settings.get("headless", True)
        )
        
        self.context = self.browser.new_context()
        
        # Load cookies if authentication is enabled BEFORE creating a page [cite: 21]
        auth_config = self.config.get("authentication", {})
        if auth_config.get("enabled", False):
            self.cookie_manager.load_cookies_to_context(self.context, auth_config.get("profile_path"))
            
        self.page = self.context.new_page()
        self._standardize_viewport()
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Cleans up and closes the browser and Playwright instances.
        """
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("Automation finished. Browser closed.")

    def _standardize_viewport(self):
        """
        Forces the browser to a fixed viewport size and zoom level. [cite: 50, 104]
        This is critical for consistent coordinate-based interactions. [cite: 51]
        """
        viewport_config = self.config["settings"]["viewport"]
        width = viewport_config["width"]
        height = viewport_config["height"]
        
        print(f"Standardizing viewport to: {width}x{height}")
        self.page.set_viewport_size({"width": width, "height": height}) # [cite: 55]
        
        zoom_level = self.config["settings"].get("zoom_level", 1.0)
        print(f"Locking zoom level to: {zoom_level * 100}%")
        self.page.evaluate(f"document.body.style.zoom = '{zoom_level}'") # [cite: 61, 139]


    def _validate_coordinates(self, x: int, y: int):
        """
        Checks if the given coordinates are within the viewport boundaries. [cite: 91, 98]
        """
        viewport = self.page.viewport_size
        if not (0 <= x < viewport["width"] and 0 <= y < viewport["height"]):
            raise CoordinateOutOfBoundError(x, y, viewport["width"], viewport["height"])

    def run_workflow(self):
        """
        Executes the sequence of actions defined in the workflow configuration.
        """
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
                # Stop workflow on error
                break 
        
        print("\nWorkflow finished.")

    def execute_action(self, action: str, params: Dict[str, Any]):
        """
        Maps an action string to its corresponding method.
        """
        if action == "goto":
            self.page.goto(params["url"])
        elif action == "click":
            x, y = params["x"], params["y"]
            self._validate_coordinates(x, y)
            # Supports both single and double click [cite: 9]
            if params.get("double_click", False):
                self.page.mouse.dblclick(x, y)
            else:
                self.page.mouse.click(x, y) # [cite: 6, 8]
        elif action == "type":
            # Clicks at the coordinate first, then types [cite: 14]
            if "x" in params and "y" in params:
                 self.page.mouse.click(params["x"], params["y"])
            
            # Clears content if specified [cite: 15]
            if params.get("clear_first", False):
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Delete")
                
            self.page.keyboard.type(params["text"])
        elif action == "wait":
            time.sleep(params["milliseconds"] / 1000.0)
        elif action == "screenshot":
            # Ensure directory exists
            os.makedirs(os.path.dirname(params["path"]), exist_ok=True)
            self.page.screenshot(path=params["path"]) # [cite: 80]
        elif action == "save_cookies":
            profile_path = self.config["authentication"]["profile_path"]
            self.cookie_manager.save_cookies_from_page(self.page, profile_path) # [cite: 22]
        elif action == "upload":
            x, y, file_path = params["x"], params["y"], params["file_path"]
            self._validate_coordinates(x, y)
            
            # Listen for the file chooser dialog BEFORE clicking the upload button
            with self.page.expect_file_chooser() as fc_info:
                self.page.mouse.click(x, y)
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)
        else:
            raise ActionNotFoundError(action)