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

    def get_projects(self):
        """Get all projects from Todoist."""
        try:
            return self.api.get_projects()
        except Exception as error:
            print(f"Error fetching projects: {error}")
            return []

    def is_shared_project(self, project_id):
        """Check if a project is shared."""
        try:
            project = self.api.get_project(project_id)
            return project.is_shared
        except Exception as error:
            print(f"Error checking project: {error}")
            return False

    def update_task(self, task_id, **kwargs):
        """Update a task in Todoist."""
        try:
            return self.api.update_task(task_id, **kwargs)
        except Exception as error:
            print(f"Error updating task: {error}")
            return None

    def create_subtask(self, parent_id, content, **kwargs):
        """Create a subtask for a task in Todoist."""
        try:
            kwargs["parent_id"] = parent_id
            kwargs["content"] = content

            return self.api.add_task(**kwargs)
        except Exception as error:
            print(f"Error creating subtask for {parent_id}: {error}")
            return None

    # Add more methods here as needed


# Test in todoist_client.py
if __name__ == "__main__":
    client = TodoistClient()
    tasks = client.get_active_tasks()
    print(f"Found {len(tasks)} active tasks")

    # Print the first task as an example
    if tasks:
        print(f"Example task: {tasks[0].content}")
