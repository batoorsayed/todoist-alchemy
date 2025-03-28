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
            raise ValueError(
                "Todoist API token not found."
                "Please set TODOIST_API_TOKEN in environment variables."
                "or in your claude_desktop_config.json file."
            )

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

    def get_sections(self):
        """Get all sections from Todoist."""
        try:
            return self.api.get_sections()
        except Exception as error:
            print(f"Error fetching sections: {error}")
            return []

    def get_labels(self):
        """Get all labels from Todoist."""
        try:
            return self.api.get_labels()
        except Exception as error:
            print(f"Error fetching labels: {error}")
            return []

    def update_task(self, task_id, **kwargs):
        """Update a task in Todoist."""
        try:
            # Filter out parameters that aren't valid for the API
            valid_params = [
                "content",
                "description",
                "labels",
                "priority",
                "due_string",
                "due_date",
                "due_datetime",
                "due_lang",
                "project_id",  # Not listed in Docs
                "section_id",  # Not listed in Docs
                "order",  # Not listed in Docs
                "assignee_id",
                # "duration",
                # "duration_unit",
                # "deadline_date",
                # "deadline_lang",
            ]
            api_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}

            return self.api.update_task(task_id=task_id, **api_kwargs)
        except Exception as error:
            print(f"Error updating task {task_id}: {error}")
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
