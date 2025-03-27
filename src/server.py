# Import necessary libraries
from typing import List, Dict
from mcp.server.fastmcp import FastMCP

# Import Todoist client from todoist_client.py
from todoist_client import TodoistClient

# Create a FastMCP server instance
mcp = FastMCP("Todoist Alchemy")

# Initialize Todoist client
todoist_client = TodoistClient()

### Helper Functions


def is_task_unprocessed(task) -> bool:
    """Check if a task is unprocessed and not preserved."""
    # Get description with fallback to empty string
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
        "due_string": task.due.string if task.due else None,
        "is_completed": task.is_completed,
        # Add other relevant task data here
    }


### Tools


@mcp.tool()
def fetch_unprocessed_tasks() -> List[Dict]:
    """
    Fetch all unprocessed tasks from Todoist that need organization.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary contains
            information about an unprocessed task.

    Raises:
        Exception: If there is an error fetching tasks from Todoist
    """
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


@mcp.tool()
def process_task(task_dict: dict, processing_notes: dict) -> dict:
    """
    Process a task according to Alchemy rules and return the transformed task.

    Args:
        task_dict: Dictionary containing task information
        processing_notes: Dictionary containing Claude's processing decisions

    Returns:
        Updated task dictionary with alchemy transformations applied
    """
    # Extract the original task information
    task_id = task_dict["id"]
    content = task_dict["content"]
    description = task_dict["description"] or ""

    # Apply Claude's transformations from processing_notes
    new_content = processing_notes.get("new_content", content)
    new_description = processing_notes.get("new_description", description)

    # Ensure the task is marked as processed without duplicate markers
    if "[TA]" not in new_description:
        new_description = f"{new_description} [TA]".strip()

    # Create updated task dictionary
    updated_task = {
        "id": task_id,
        "content": new_content,
        "description": new_description,
        "priority": processing_notes.get("priority"),
        "labels": processing_notes.get("labels", []),
        # Include other fields that Claude might have processed
        "due_string": processing_notes.get("due_string"),
        # If subtasks were created, they'll be in a separate field
        "subtasks": processing_notes.get("subtasks", []),
    }

    return updated_task


# TODO: Do I need one tool and multiple functions or multiple tools?
# TODO: Create a Task Update Tool
# TODO: Add a Tool to Get Project and Label Information

if __name__ == "__main__":
    # Run the server with stdio transport
    mcp.run(transport="stdio")
