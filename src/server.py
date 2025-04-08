# Import necessary libraries
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
import os
import logging

# Import Todoist client from todoist_client.py
from todoist_client import TodoistClient

# Create a FastMCP server instance
mcp = FastMCP("Todoist Alchemy")

# Initialize Todoist client
todoist_client = TodoistClient()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "..", "Logs", "todoist_alchemy.log")
        ),
    ],
)

# Create a logger
logger = logging.getLogger(__name__)

# TODO: Improve dependency management for easier user installation
#   Options to consider:
#   1. Create an npm package wrapper (like official MCP servers)
#   2. Add auto-dependency installation in this script
#   3. Create an installer shell script that users run first
#   See README.md for current installation requirements

#### Supporting Information ####


### Instructions ###
## Function
def _read_processing_instructions() -> str:
    """Read the contents of the processing_instructions.txt file from the config directory."""
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
        logger.error(f"Error reading processing instructions: {str(e)}", exc_info=True)
        return f"Error reading processing instructions: {str(e)}"


## Tool
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


### Metadata ###
## Tool
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

        metadata = {
            "projects": project_data,
            "sections": section_data,
            "labels": label_data,
        }
        logger.debug(
            f"Retrieved {len(project_data)} projects, {len(section_data)} sections, {len(label_data)} labels"
        )
        return metadata

    except Exception as error:
        logger.error(f"Error fetching metadata: {str(error)}", exc_info=True)
        return {"error": str(error)}


#### Fetching Tasks ####
## Function
def _is_task_unprocessed(task, projects_data) -> bool:
    """Check if a task is unprocessed and not preserved."""

    try:
        # Get description
        description = task.description

        # Check if task is processed or preserved
        if "[TA]" in description or "!" in description:
            return False

        # Skip tasks in shared projects
        project_id = task.project_id
        if project_id and project_id in projects_data:
            if projects_data[project_id]["is_shared"]:
                return False

        return True
    except Exception as e:
        logger.error(f"Error checking if task is unprocessed: {str(e)}", exc_info=True)
        return False  # Default to False if we can't determine


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
    try:
        subtasks = todoist_client.get_subtasks(task.id)
        if subtasks:
            logger.info(f"Found {len(subtasks)} subtasks for task {task.id}")
            task_data["subtasks"] = [_get_task_data(subtask) for subtask in subtasks]
    except Exception as e:
        logger.error(
            f"Error fetching subtasks for task {task.id}: {str(e)}", exc_info=True
        )

    return task_data


def _fetch_unprocessed_tasks() -> List[Dict]:
    """
    Fetch all unprocessed tasks from Todoist that need organization."""

    try:
        # Get all active tasks
        all_tasks = todoist_client.get_active_tasks()

        # Get projects data
        metadata = get_todoist_metadata()
        projects_data = {p["id"]: p for p in metadata["projects"]}

        # Filter out already processed tasks
        unprocessed_tasks = [
            task for task in all_tasks if _is_task_unprocessed(task, projects_data)
        ]
        logger.info(
            f"Found {len(unprocessed_tasks)} unprocessed tasks out of {len(all_tasks)} total tasks"
        )

        # Get task data for each unprocessed task
        return [_get_task_data(task) for task in unprocessed_tasks]

    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}", exc_info=True)
        return []


## Tool
@mcp.tool()
def fetch_unprocessed_tasks() -> List[Dict]:
    """
    Fetch all unprocessed tasks from Todoist that need organization.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary contains
            information about an unprocessed task.
    """
    return _fetch_unprocessed_tasks()


#### Processing Tasks ####


## Function
def _prepare_for_processing() -> Dict:
    """Prepare a complete data package for batch processing."""

    try:
        # Get all unprocessed tasks
        unprocessed_tasks = _fetch_unprocessed_tasks()

        # Get metadata (projects, sections, labels)
        metadata = get_todoist_metadata()

        # Combine into a single data package
        return {"tasks": unprocessed_tasks, "metadata": metadata}
    except Exception as e:
        logger.error(f"Error preparing batch for processing: {str(e)}", exc_info=True)
        return {"tasks": [], "metadata": {}}


def _process_tasks(data_package: Dict) -> Dict:
    """Process tasks using Claude's analysis."""
    try:
        # Extract data
        tasks = data_package.get("tasks", [])

        # Skip processing if no tasks to process
        if not tasks:
            logger.info("No tasks to process in batch")
            return {"processed_tasks": [], "error": None}

        # Add [TA] marker to all tasks being processed
        for task in tasks:
            description = task.get("description", "")
            task["description"] = f"{description} [TA]".strip()

        logger.info(f"Processing {len(tasks)} tasks")
        return {"processed_tasks": tasks, "error": None}

    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}", exc_info=True)
        return {"processed_tasks": [], "error": str(e)}


def _process_subtasks(task_id: str, subtasks_data: List[Dict]) -> List[Dict]:
    """Process subtasks by deleting existing ones and creating new ones."""

    try:
        # Delete existing subtasks
        if not todoist_client.delete_subtasks(task_id):
            return []

        # Create new subtasks
        created = []
        for data in subtasks_data:
            # Only add non-empty values
            clean_data = {
                "parent_id": task_id,
                "content": data["content"],
                "description": f"{data.get('description', '')} [TA]".strip(),
            }

            if subtask := todoist_client.add_task(**clean_data):
                created.append({"id": subtask.id, "content": subtask.content})

        return created

    except Exception as e:
        logger.error(f"Error processing subtasks for task {task_id}: {e}")
        return []


## Tool
@mcp.tool()
def process_task() -> Dict:
    """
    Process all unprocessed tasks in a single batch.

    Returns:
        Dictionary containing processing results
    """
    try:
        # Prepare data package
        data_package = _prepare_for_processing()

        # Process the batch
        return _process_tasks(data_package)

    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}", exc_info=True)
        return {"error": str(e), "processed_tasks": []}


#### Updating Tasks ####
## Function
def _get_task_updates(task_dict: dict, processing_notes: dict) -> dict:
    """Get updates for a task based on processing notes."""
    # Start with required fields
    updates = {
        "id": task_dict["id"],
        "content": processing_notes.get("content", task_dict["content"]),
        "description": processing_notes.get(
            "description", task_dict["description"] or ""
        ),
        "priority": processing_notes.get("priority", task_dict["priority"]),
        "labels": processing_notes.get("labels", task_dict["labels"]),
    }

    # Add optional fields that exist in processing_notes
    optional_fields = [
        "parent_id",  # Keep task hierarchy
        "due_string",
        "project_id",
        "section_id",
        "subtasks",  # Process separately in _update_task
    ]

    for field in optional_fields:
        if field in processing_notes:
            updates[field] = processing_notes[field]

    return updates


def _update_task(task_dict: dict, processing_notes: dict) -> Dict:
    """Update a task in Todoist based on processing notes."""
    try:
        task_id = task_dict["id"]

        # Get updates for a task
        updates = _get_task_updates(task_dict, processing_notes)

        # Extract subtasks before modifying updates
        subtasks = updates.pop("subtasks", None)

        # Prepare API updates
        api_updates = {k: v for k, v in updates.items() if k not in ["id", "subtasks"]}

        # Update task
        updated_task = todoist_client.update_task(task_id, **api_updates)

        # Check if update was successful
        if not updated_task:
            logger.error(f"Failed to update task {task_id}")
            return {"success": False, "error": "Failed to update task"}

        result = {"success": True, "task": updated_task}

        # Process subtasks if present
        if subtasks:
            logger.info(f"Processing {len(subtasks)} subtasks for task {task_id}")
            result["subtasks"] = _process_subtasks(task_id, subtasks)

        return result

    except Exception as e:
        logger.error(f"Error updating task {task_dict.get('id')}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def update_tasks(processed_tasks: List[Dict]) -> Dict:
    """
    Update a batch of tasks in Todoist with the changes from processing.

    Args:
        processed_tasks: List of processed task dictionaries from Claude

    Returns:
        Dictionary with results of update operations
    """
    try:
        if not processed_tasks:
            return {"success": True, "updated": [], "failed": []}

        updated = []
        failed = []

        for task in processed_tasks:
            result = _update_task(
                task, task
            )  # Task dict serves as both input and processing notes
            if result["success"]:
                updated.append(result["task"])
            else:
                failed.append({"id": task["id"], "error": result["error"]})

        return {"success": len(failed) == 0, "updated": updated, "failed": failed}

    except Exception as e:
        return {"success": False, "error": str(e), "updated": [], "failed": []}


if __name__ == "__main__":
    print("Starting Todoist Alchemy MCP Server...")
    print("This server helps Claude organize your Todoist tasks.")
    print("Connect to this server in Claude Desktop to begin processing tasks.")

    # Run the server with stdio transport for Claude Desktop
    mcp.run(transport="stdio")
