"""
Test cases for creating tasks in Google Tasks app
"""
import pytest
from pages.tasks_list_page import TasksListPage
import time


class TestCreateTask:
    """Test suite for task creation functionality"""

    def test_create_single_task(self, driver):
        """Test creating a single task"""
        print("\n🧪 Test: Create single task")

        tasks_page = TasksListPage(driver)
        task_name = f"Test Task {int(time.time())}"

        print(f"📝 Creating task: {task_name}")
        tasks_page.add_new_task(task_name)

        print("🔍 Verifying task exists...")
        assert tasks_page.verify_task_exists(task_name), \
            f"Task '{task_name}' was not created successfully"

        print("✅ Test PASSED!")

