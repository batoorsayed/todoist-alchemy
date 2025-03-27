from typing import List, Dict
from mcp.server.fastmcp import FastMCP

# Import Todoist client from todoist_client.py
from todoist_client import TodoistClient

# Create a FastMCP server instance
mcp = FastMCP("Todoist Alchemy")

# Initialize Todoist client
todoist_client = TodoistClient()


def is_task_unprocessed(task) -> bool:
    """Check if a task is unprocessed and not preserved."""
    description = task.description or ""

    # Check if task is processed or preserved
    if "[TA]" in description or "!" in description:
        return False

    # TODO: Skip tasks in shared projects (Implement this logic later)
    # if is_shared_project(task.project_id):
    #     return False

    return True


def get_task_data(task) -> Dict:
    """Extract and format task data."""
    return {
        # required fields
        "id": task.id,
        "content": task.content,
        # Optional fields
        "project_id": task.project_id,
        "section_id": task.section_id,
        "parent_id": task.parent_id,
        "description": task.description,
        "labels": task.labels,
        "priority": task.priority,
        "order": task.order,
        "due": task.due.date if task.due else None,
        "is_completed": task.is_completed,
        # Add other relevant task data here
    }


@mcp.tool()
def fetch_unprocessed_tasks() -> List[Dict]:
    """Fetch all unprocessed tasks from Todoist that need organization."""
    try:
        # Get all active tasks
        all_tasks = todoist_client.get_active_tasks()

        # Filter out already processed tasks
        unprocessed_tasks = [task for task in all_tasks if is_task_unprocessed(task)]

        # Get task data for each unprocessed task
        return [get_task_data(task) for task in unprocessed_tasks]

    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []


if __name__ == "__main__":
    # Run the server with stdio transport
    mcp.run(transport="stdio")
