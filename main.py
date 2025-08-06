import yaml
from core.automation_engine import AutomationEngine

CONFIG_PATH = "workflows/config.yaml"

def main():
    """
    Main function to load configuration and run the automation engine.
    """
    print("Loading configuration...")
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{CONFIG_PATH}'")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        return

    # Use a context manager to ensure the browser is closed properly
    try:
        with AutomationEngine(config) as engine:
            engine.run_workflow()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()