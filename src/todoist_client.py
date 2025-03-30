# Import necessary libraries
import os
from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI
import logging

# Logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# TODO: Implement retry logic for API operations
# Consider using a decorator to retry failed API calls
# Example:
# def retry_on_error(max_retries=3, delay=1):
#     """Decorator to retry API operations on failure."""
#     def decorator(func):...

# TODO: Add API rate limit handling
# Consider implementing a rate limiter to avoid hitting Todoist API limits


class TodoistClient:
    """Client for interacting with Todoist API."""

    def __init__(self):
        """Initialize with API token from environment variables."""
        self.api_token = os.getenv("TODOIST_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "Todoist API token not found."
                "Please set TODOIST_API_TOKEN in environment variables."
                "Or in your claude_desktop_config.json file."
                "You can get your API token from: "
                "https://app.todoist.com/app/settings/integrations/developer"
            )

        self.api = TodoistAPI(self.api_token)

    def get_active_tasks(self):
        """Get all active tasks from Todoist."""

        try:
            tasks = self.api.get_tasks()
            return tasks
        except Exception as error:
            logger.error(f"Error fetching tasks: {error}", exc_info=True)
            return []

    def get_projects(self):
        """Get all projects from Todoist."""
        try:
            return self.api.get_projects()
        except Exception as error:
            logger.error(f"Error fetching projects: {error}", exc_info=True)
            return []

    def get_sections(self):
        """Get all sections from Todoist."""
        try:
            return self.api.get_sections()
        except Exception as error:
            logger.error(f"Error fetching sections: {error}", exc_info=True)
            return []

    def get_labels(self):
        """Get all labels from Todoist."""
        try:
            return self.api.get_labels()
        except Exception as error:
            logger.error(f"Error fetching labels: {error}", exc_info=True)
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
                "project_id",
                "section_id",
                "order",
                "assignee_id",
                "duration",
                "duration_unit",
                "deadline_date",
                "deadline_lang",
            ]
            api_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}

            logger.info(f"Updating task {task_id} with {list(api_kwargs.keys())}")
            return self.api.update_task(task_id=task_id, **api_kwargs)
        except Exception as error:
            logger.error(f"Error updating task {task_id}: {error}", exc_info=True)
            return None

    def add_task(self, **kwargs):
        """Add a new task to Todoist."""
        try:
            # Filter out invalid parameters
            valid_params = [
                "content",
                "description",
                "project_id",
                "section_id",
                "parent_id",
                "order",
                "labels",
                "priority",
                "due_string",
                "due_date",
                "due_datetime",
                "due_lang",
                "assignee_id",
                "duration",
                "duration_unit",
                "deadline_date",
                "deadline_lang",
            ]
            api_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}

            logger.info(f"Creating new task with fields: {list(api_kwargs.keys())}")
            return self.api.add_task(**api_kwargs)
        except Exception as error:
            logger.error(f"Error creating task: {error}", exc_info=True)
            return None

    def get_subtasks(self, parent_id):
        """Get all subtasks for a given parent task."""
        try:
            return self.api.get_tasks(parent_id=parent_id)
        except Exception as error:
            logger.error(
                f"Error fetching subtasks for parent {parent_id}: {error}",
                exc_info=True,
            )
            return []

    def delete_subtasks(self, parent_id):
        """Delete all subtasks for a given parent task."""

        try:
            # Get all subtasks
            subtasks = self.get_subtasks(parent_id)

            # Delete each subtask
            logger.debug(f"Deleting {len(subtasks)} subtasks for parent {parent_id}")
            for subtask in subtasks:
                self.api.delete_task(task_id=subtask.id)
                logger.debug(f"Deleted subtask {subtask.id}")

            return True
        except Exception as error:
            logger.error(
                f"Error deleting subtasks for parent {parent_id}: {error}",
                exc_info=True,
            )
            return False

    # Add more methods here as needed


# Test in todoist_client.py
if __name__ == "__main__":
    client = TodoistClient()
    tasks = client.get_active_tasks()
    print(f"Found {len(tasks)} active tasks")

    # Print the first task as an example
    if tasks:
        print(f"Example task: {tasks[0].content}")
