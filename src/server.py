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


def _create_subtasks(task_id, subtasks):
    """Create subtasks with all provided metadata preserved."""
    created_subtasks = []

    for subtask in subtasks:
        # Extract content (required)
        content = subtask.get("content")
        if not content:
            print("Skipping subtask creation: missing content")
            continue

        # Create a copy of subtask data without modifying the original
        subtask_data = subtask.copy()

        # Set parent task ID
        subtask_data["parent_id"] = task_id

        # Create the subtask
        try:
            new_subtask = todoist_client.api.add_task(**subtask_data)
            if new_subtask:
                created_subtasks.append(
                    {
                        "id": new_subtask.id,
                        "content": new_subtask.content,
                        # Include any other fields you want to track
                    }
                )
        except Exception as e:
            print(f"Error creating subtask '{content}': {e}")

    return created_subtasks


def _update_task(task_dict: dict, processing_notes: dict) -> dict:
    """
    Update a task in Todoist based on processing notes.

    Args:
        task_dict: Dictionary containing task information
        processing_notes: Dictionary containing Claude's processing decisions

    Returns:
        Updated task dictionary with alchemy transformations applied
    """
    try:
        # Get task ID
        task_id = task_dict["id"]
        # Get updates
        updates = _get_task_updates(task_dict, processing_notes)
        # Update task in Todoist
        updated_task = todoist_client.update_task(task_id, **updates)

        # Check if update was successful
        if not updated_task:
            return {"success": False, "error": "Failed to update task"}

        result = {"success": True, "task": updated_task}

        # Create subtasks if needed
        if processing_notes.get("subtasks"):
            subtasks = _create_subtasks(task_id, processing_notes.get("subtasks"))
            # Add subtasks to the updated task dictionary
            result["subtasks"] = subtasks

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def _read_processing_instructions() -> str:
    """
    Read the contents of the processing_instructions.txt file from the src directory.

    Returns:
        str: The contents of the processing_instructions.txt file
    """
    try:
        file_path = os.path.join(
            os.path.dirname(__file__), "processing_instructions.txt"
        )
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "Error: processing_instructions.txt file not found in src directory. "
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
