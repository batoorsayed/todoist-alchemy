# Import necessary libraries
import unittest
from unittest.mock import Mock
from server import _is_task_unprocessed, _get_task_data


class TestTaskProcessing(unittest.TestCase):
    def test_is_task_unprocessed(self):
        # Test processed task
        processed_task = Mock(description="Task [TA]")
        self.assertFalse(_is_task_unprocessed(processed_task))

        # Test preserved task
        preserved_task = Mock(description="Task !")
        self.assertFalse(_is_task_unprocessed(preserved_task))

        # Test unprocessed task
        unprocessed_task = Mock(description="Task")
        self.assertTrue(_is_task_unprocessed(unprocessed_task))

    def test_get_task_data(self):
        # Create a mock task
        mock_task = Mock(
            id=123,
            content="Test Task",
            description="Description",
            labels=["label1"],
            priority=2,
            due=Mock(string="2025-03-27"),
            is_completed=False,
        )

        # Get the data
        task_data = _get_task_data(mock_task)

        # Verify the data
        self.assertEqual(task_data["id"], 123)
        self.assertEqual(task_data["content"], "Test Task")
        self.assertEqual(task_data["labels"], ["label1"])
        self.assertEqual(task_data["priority"], 2)
        self.assertEqual(task_data["due_string"], "2025-03-27")
        self.assertFalse(task_data["is_completed"])


# TODO: Add unit tests for `_fetch_unprocessed_tasks`, `_update_task`,
# and other critical functions to ensure full test coverage.


if __name__ == "__main__":
    unittest.main()
