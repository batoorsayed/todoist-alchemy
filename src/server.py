# Import necessary libraries
from typing import List, Dict
from mcp.server.fastmcp import FastMCP

# Import Todoist client from todoist_client.py
from todoist_client import TodoistClient

# Create a FastMCP server instance
mcp = FastMCP("Todoist Alchemy")

# Initialize Todoist client
todoist_client = TodoistClient()

### Task Processing Functions ###


def _is_task_unprocessed(task) -> bool:
    """Check if a task is unprocessed and not preserved."""
    # Get description with fallback to empty string
    description = task.description or ""

    # Check if task is processed or preserved
    if "[TA]" in description or "!" in description:
        return False

    # Skip tasks in shared projects
    if todoist_client.is_shared_project(task.project_id):
        return False

    return True


def _get_task_data(task) -> Dict:
    """Extract and format task data for processing."""
    task_data = {
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
        "due": task.due.string if task.due else None,
        "is_completed": task.is_completed,
        # Add other relevant task data here
    }
    return task_data


def _fetch_unprocessed_tasks() -> List[Dict]:
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
        unprocessed_tasks = [task for task in all_tasks if _is_task_unprocessed(task)]

        # Get task data for each unprocessed task
        return [_get_task_data(task) for task in unprocessed_tasks]

    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []


def _get_task_updates(task_dict: dict, processing_notes: dict) -> dict:
    """
    Get updates for a task based on processing notes.
    """
    # Extract the original task information
    task_id = task_dict["id"]
    content = task_dict["content"]
    description = task_dict["description"] or ""
    project_id = task_dict["project_id"]
    project_name = task_dict.get("project_name", "")

    # Apply Claude's transformations from processing_notes
    new_content = processing_notes.get("new_content", content)
    new_description = processing_notes.get("new_description", description)

    # Ensure the task is marked as processed without duplicate markers
    if "[TA]" not in new_description:
        new_description = f"{new_description} [TA]".strip()

    # Create updated task dictionary
    return {
        "id": task_id,
        "content": new_content,
        "description": new_description,
        "priority": processing_notes.get("priority"),
        "labels": processing_notes.get("labels", []),
        "due_string": processing_notes.get("due_string"),
        # Project information
        "project_id": project_id,
        "project_name": project_name,
        # Include original subtasks if they exist
        "original_subtasks": task_dict.get("subtasks", []),
        # Include any new subtasks from processing notes
        "new_subtasks": processing_notes.get("subtasks", []),
        # Include any project changes from processing notes
        "new_project_id": processing_notes.get("project_id"),
        "new_project_name": processing_notes.get("project_name"),
    }


def _create_subtasks(task_dict: dict, processing_notes: dict) -> List[Dict]:
    """
    Create subtasks for a task based on processing notes.
    """
    # Extract the original task information
    task_id = task_dict["id"]
    subtasks = processing_notes.get("subtasks", [])

    # Create subtasks and convert them to dictionaries
    return [todoist_client.create_subtask(task_id, subtask) for subtask in subtasks]


def _update_task(task_dict: dict, processing_notes: dict) -> dict:
    """
    Update a task in Todoist based on processing notes.

    Args:
        task_dict: Dictionary containing task information
        processing_notes: Dictionary containing Claude's processing decisions

    Returns:
        Updated task dictionary with alchemy transformations applied
    """
    # Get task ID
    task_id = task_dict["id"]
    # Get updates
    updates = _get_task_updates(task_dict, processing_notes)
    # Update task in Todoist
    updated_task = todoist_client.update_task(task_id, **updates)

    # Create subtasks if needed
    if processing_notes.get("subtasks"):
        subtasks = _create_subtasks(task_dict, processing_notes)
        # Add subtasks to the updated task dictionary
        updated_task["subtasks"] = subtasks

    return updated_task


### Todoist Integration Functions (Tools) ###


@mcp.tool()
def fetch_unprocessed_tasks() -> List[Dict]:
    """
    Fetch all unprocessed tasks from Todoist that need organization.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary contains
            information about an unprocessed task.
    """
    return _fetch_unprocessed_tasks()


@mcp.tool()
def process_task(task_dict: dict, processing_notes: dict) -> dict:
    """
    Process unorganized tasks without updating them in Todoist.

    Args:
        task_dict: Dictionary containing task information
        processing_notes: Dictionary containing Claude's processing decisions

    Returns:
        Updated task dictionary with alchemy transformations applied
    """
    return _get_task_updates(task_dict, processing_notes)


@mcp.tool()
def update_task(task_dict: dict, processing_notes: dict) -> dict:
    """
    Update a task in Todoist with the changes from processing.

    Args:
        task_dict: Dictionary containing original task information
        processing_notes: Dictionary containing Claude's processing decisions

    Returns:
        Dictionary with update results, including success status and any error messages
    """
    return _update_task(task_dict, processing_notes)


# if __name__ == "__main__":
#    print("Starting Todoist Alchemy MCP Server...")
#    print("This server helps Claude organize your Todoist tasks.")
#    print("Connect to this server in Claude Desktop to begin processing tasks.")

#    # Run the server with stdio transport for Claude Desktop
#    mcp.run(transport="stdio")

# Temp for testing
if __name__ == "__main__":
    # Test fetching unprocessed tasks
    unprocessed = _fetch_unprocessed_tasks()
    print(f"Found {len(unprocessed)} unprocessed tasks")

    # Then run the server normally
    print("Starting Todoist Alchemy MCP Server...")
    mcp.run(transport="stdio")
