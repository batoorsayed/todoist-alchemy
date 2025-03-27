import os
from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI

# Load environment variables
load_dotenv()


class TodoistClient:
    """Client for interacting with Todoist API."""

    def __init__(self):
        """Initialize with API token from environment variables."""
        self.api_token = os.getenv("TODOIST_API_TOKEN")
        if not self.api_token:
            raise ValueError("Todoist API token not found in environment variables")

        self.api = TodoistAPI(self.api_token)

    def get_active_tasks(self):
        """Get all active tasks from Todoist."""
        try:
            return self.api.get_tasks()
        except Exception as error:
            print(f"Error fetching tasks: {error}")
            return []

    # Add more methods here as needed


if __name__ == "__main__":
    # Verify the client works
    client = TodoistClient()
    tasks = client.get_active_tasks()
    print(f"Found {len(tasks)} active tasks")
