# TODO: Replace print statements with proper logging
# import logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


# Import necessary libraries
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
import os

# Import Todoist client from todoist_client.py
from todoist_client import TodoistClient

# TODO: Improve dependency management for easier user installation
#   Options to consider:
#   1. Create an npm package wrapper (like official MCP servers)
#   2. Add auto-dependency installation in this script
#   3. Create an installer shell script that users run first
#   See README.md for current installation requirements

# TODO: Ensure consistent type annotations throughout the codebase
# Consider using more specific types (e.g., TypedDict) for task data structures

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

    # Fetch existing subtasks if this is a parent task
    if task.parent_id is None:  # Only fetch subtasks for top-level tasks
        try:
            subtasks = todoist_client.get_subtasks(task.id)
            if subtasks:
                task_data["subtasks"] = [
                    _get_task_data(subtask) for subtask in subtasks
                ]
        except Exception as e:
            print(f"Error fetching subtasks for task {task.id}: {e}")

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

    # Create updated task dictionary with all possible fields from processing_notes
    updates = {
        "id": task_id,
        # Use processing_notes values with fallback to original values
        "content": processing_notes.get("content", task_dict["content"]),
        "description": processing_notes.get(
            "description", task_dict["description"] or ""
        ),
        "priority": processing_notes.get("priority", task_dict["priority"]),
        "labels": processing_notes.get("labels", task_dict["labels"]),
    }

    # Ensure the task is marked as processed without duplicate markers
    if "[TA]" not in updates["description"]:
        updates["description"] = f"{updates['description']} [TA]".strip()

    # Add optional fields only if they exist in processing_notes
    optional_fields = ["due_string", "project_id", "section_id"]
    for field in optional_fields:
        if field in processing_notes:
            updates[field] = processing_notes[field]

    # Include subtasks if present
    if "subtasks" in processing_notes:
        updates["subtasks"] = processing_notes["subtasks"]

    return updates


def _process_subtasks(
    task_id: int, subtasks_data: List[Dict], todoist_client: TodoistClient
) -> List[Dict]:
    """
    Process subtasks by deleting existing ones and creating new ones.

    Args:
        task_id: Parent task ID
        subtasks_data: List of subtask data dictionaries
        todoist_client: Todoist client instance

    Returns:
        List of created subtasks with their IDs and content
    """
    created_subtasks = []
    try:
        # Delete existing subtasks
        if not todoist_client.delete_subtasks(task_id):
            print(f"Failed to delete subtasks for task {task_id}")

        # Create new subtasks
        for subtask_data in subtasks_data:
            # Add parent_id
            subtask_data["parent_id"] = task_id

            # Add TA marker to description
            if (
                "description" in subtask_data
                and "[TA]" not in subtask_data["description"]
            ):
                subtask_data["description"] = (
                    f"{subtask_data['description']} [TA]".strip()
                )

            # Create subtask
            try:
                new_subtask = todoist_client.api.add_task(**subtask_data)
                if new_subtask:
                    created_subtasks.append(
                        {"id": new_subtask.id, "content": new_subtask.content}
                    )
            except Exception as e:
                print(f"Error creating subtask: {e}")

    except Exception as e:
        print(f"Error processing subtasks for task {task_id}: {e}")

    return created_subtasks


def _update_task(task_dict: dict, processing_notes: dict) -> Dict:
    """
    Update a task in Todoist based on processing notes.

    Args:
        task_dict: Dictionary containing task information
        processing_notes: Dictionary containing Claude's processing decisions

    Returns:
        dict: Result of the update operation with:
            - success: bool indicating operation success
            - task: Updated task information
            - subtasks_created: List of created subtasks
            - error: Error message if operation failed
    """
    try:
        task_id = task_dict["id"]
        updates = _get_task_updates(task_dict, processing_notes)

        # Prepare API updates
        api_updates = {k: v for k, v in updates.items() if k not in ["id", "subtasks"]}

        # Update task
        updated_task = todoist_client.update_task(task_id, **api_updates)

        # Check if update was successful
        if not updated_task:
            return {"success": False, "error": "Failed to update task"}

        result = {"success": True, "task": updated_task}

        # Process subtasks if present
        if "subtasks" in processing_notes:
            result["subtasks_created"] = _process_subtasks(
                task_id, processing_notes["subtasks"], todoist_client
            )

        return result

    except Exception as e:
        print(f"Error updating task {task_dict.get('id')}: {e}")
        return {"success": False, "error": str(e)}


def _read_processing_instructions() -> str:
    """
    Read the contents of the processing_instructions.txt file from the config directory.

    Returns:
        str: The contents of the processing_instructions.txt file
    """
    try:
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "processing_instructions.txt"
        )
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "Error: processing_instructions.txt file not found in config directory. "
            "Please create this file with your Todoist Alchemy instructions."
        )
    except Exception as e:
        return f"Error reading processing instructions: {str(e)}"


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


@mcp.tool()
def get_todoist_metadata() -> dict:
    """
    Get projects, sections, and labels from Todoist for reference.

    Returns:
        Dictionary containing projects, sections, and labels
    """
    try:
        # Get all projects with full metadata
        projects = todoist_client.get_projects()
        project_data = [
            {
                "id": project.id,
                "name": project.name,
                "parent_id": project.parent_id,
                "is_shared": project.is_shared,
            }
            for project in projects
        ]

        # Get all sections with full metadata
        sections = todoist_client.get_sections()
        section_data = [
            {
                "id": section.id,
                "name": section.name,
                "project_id": section.project_id,
            }
            for section in sections
        ]

        # Get all labels with full metadata
        labels = todoist_client.get_labels()
        label_data = [
            {
                "id": label.id,
                "name": label.name,
            }
            for label in labels
        ]

        return {
            "projects": project_data,
            "sections": section_data,
            "labels": label_data,
        }
    except Exception as error:
        print(f"Error fetching metadata: {error}")
        return {"error": str(error)}


@mcp.tool()
def get_processing_instructions() -> str:
    """
    Get detailed instructions for how to process Todoist tasks.

    Returns:
        str: Complete instructions from the processing_instructions.txt file for the
        Todoist Alchemy system, including processing rules, task formatting
        guidelines, and output formats.
    """
    return _read_processing_instructions()


if __name__ == "__main__":
    print("Starting Todoist Alchemy MCP Server...")
    print("This server helps Claude organize your Todoist tasks.")
    print("Connect to this server in Claude Desktop to begin processing tasks.")

    # Run the server with stdio transport for Claude Desktop
    mcp.run(transport="stdio")

# Testing
# if __name__ == "__main__":
# Test fetching unprocessed tasks
# unprocessed = _fetch_unprocessed_tasks()
# print(f"Found {len(unprocessed)} unprocessed tasks")

# Then run the server normally
# print("Starting Todoist Alchemy MCP Server...")
# mcp.run(transport="stdio")


# TODO: Improve error reporting and propagation
# Consider returning structured error objects instead of just printing
