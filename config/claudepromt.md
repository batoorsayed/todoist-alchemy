# Todoist Alchemy: AI-Powered Task Organization System

I'm building a Management Control Panel (MCP) that leverages Claude to transform unstructured Todoist tasks into well-organized, actionable items.
I need your help designing and implementing this system.

## Core Functionality

The MCP should process task entries and transform them by:
1. Reading unorganized tasks that don't already have the "[TA]" or "!" marker
2. Cleaning up task names for clarity and consistency (required)
3. Adding short, informative descriptions that explain the purpose and scope (required)
4. Estimating required work hours using consistent format [1h], [20m], [1.5h], etc. (required)
5. Adding due dates only for genuinely urgent tasks (rarely needed)
6. Assigning priority levels from P1 (highest) to P4 (lowest) (required)
7. Adding relevant labels for categorization based on my time-block system (required)
8. Associating with appropriate projects and sections (required when applicable)
9. Breaking down into subtasks only when truly necessary (include description and time estimates for each)
10. Identifying and merging or grouping similar tasks when appropriate

## Task Processing Rules

The system should follow these guidelines when processing tasks:
- Preserve tasks marked with "!" at description
- Skip tasks already marked with "[TA]" at the end of the description
- Skip tasks that are in a shared project
- Create clear, action-oriented task names that start with verbs
- Generate concise descriptions (1-3 sentences) that provide context
- Estimate work hours based on task complexity and scope and add it to description
- Only add due dates for time-sensitive items with clear deadlines
- Assign priority based on:
  * P1: Urgent and important (must be done today/soon)
  * P2: Important but not urgent (should be done soon)
  * P3: Normal priority tasks
  * P4: Low priority, nice-to-have tasks
- Apply time-block labels appropriately:
  * Deep Work (10:00 AM - 1:15 PM): Complex, high-focus tasks
  * Learning Block (2:00 PM - 2:30 PM): Reading, learning activities
  * Quick Wins (2:30 PM - 4:00 PM): Simple, fast-completion tasks
  * Day Close (4:00 PM - 5:00 PM): End-of-day tasks, planning
  * Evening Time (7:00 PM - 10:00 PM): Personal activities
  * Weekend (12:00 PM - 7:00 PM): Weekend-specific tasks
- Only create subtasks for complex items that truly benefit from breakdown
- Always mark processed tasks with "[TA]" at the end of the description
- If unsure about project, label assignment, or description, ask for clarification instead of guessing
- Balance thoroughness with practical utility - avoid creating excessive structure


## Supporting Documentation
Claude should reference these files for context and implementation details:

### Configuration Files
- `todoist-alchemy-config/projects.md`: Complete list of projects and their sections in Todoist
- `todoist-alchemy-config/labels.md`: Time-based and categorical labels used for task organization

### Todoist API Documentation
- `todoist-api/todoist-rest-api.md`: Official REST API documentation for Todoist integration
- `todoist-api/todoist-developer-guide.md`: Developer guidelines and best practices for Todoist

### MCP Documentation
- `mcp/mcp-documentation.md`: Comprehensive documentation for the Management Control Panel
- `mcp/mcp-python-sdk.md`: Python SDK documentation for MCP implementation

## Technical Implementation

I'd like your guidance on:
1. The best approach for structuring this system
2. How to handle task data input and output
3. Building an efficient workflow that minimizes manual intervention
4. Implementing any necessary validation or error handling

## Sample Task Data

Here are some sample unprocessed tasks I typically work with:
1. "Read chapter 3 of programming book"
2. "Organize and update Proton email filtering, using AI"
3. "Update resume"
4. "Message my doctor today"
	Due: [TODAY]
	Description: [15m]
5. "Call mom"
	Description: !
6. "Check emails"
	Description: [15m]
7. "Make a dr appointment"
	Description: [30m]
	Project: Personal / Routines
	Label: Quick Wins
	Priority: P3


## Desired Output Format

The ideal output format for processed tasks would be:
1. Task: "Read Chapter 3 of Programming Book"
	Description: "Complete Chapter 3 on data structures to continue progress in learning course. [1h] [TA]"
	Priority: P3
	Project: Personal / Self-Development
	Label: Learning
2. Task: "Organize and update Proton email filtering, using AI"
	Description: "Review current filters and update Proton email filtering rules using AI. [4.25h] [TA]"
	Priority: P2
	Project: Personal / Projects
	Label: Quick Wins
	Subtasks:
		- Review current filters [30m]
		- Prep work and learn [30m]
		- Update Proton email filtering rules [2h]
		- Test new filters [15m]
3. Task: "Update Resume"
	Description: "Review and update resume for job application. [1h] [TA]"
	Priority: P3
	Project: Professional / Career Development
	Label: Quick Wins
4. Task: "Message my doctor today"
	Description: "Message my doctor today [15m] [TA]"
	Priority: P1
	Project: Personal /
	Label: Day
	Due: [TODAY]
5. Task: "Call mom"
	Description: !
6. Task: "Check emails"
	Description: "Check emails [15m] [TA]"
	Priority: P3
	Project: Personal / Routines
	Label: Quick Wins
7. "Make a dr appointment"
	Description: [30m] [TA]
	Project: Personal / Routines
	Label: Quick Wins
	Priority: P3

## Implementation Roadmap

Please provide a step-by-step implementation plan for the Todoist Alchemy system, breaking down the development process into manageable phases:

1. First, outline the key development phases (e.g., setup, core functionality, testing, refinement)
2. For each phase, list specific tasks and dependencies
3. Prioritize tasks by technical necessity and value delivery
4. Identify potential challenges and suggested approaches
5. Recommend reasonable timeframes for each phase

The roadmap should allow for incremental development and testing rather than attempting to build the entire system at once.
