#!/usr/bin/env python3
"""
Integration tests for the sub-issue suggester tool

Tests the basic functionality of the suggest_sub_issues.py script
"""

import subprocess
import sys
from pathlib import Path


def run_suggester(title, description="", task_type="development"):
    """Run the suggester script and return output"""
    script_path = Path(__file__).parent.parent / "scripts" / "suggest_sub_issues.py"
    cmd = [sys.executable, str(script_path), title, "--type", task_type]
    
    if description:
        cmd.extend(["--description", description])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_basic_development_task():
    """Test basic development task decomposition"""
    print("Testing: Basic development task...")
    code, stdout, stderr = run_suggester("Test task", task_type="development")
    
    assert code == 0, f"Script failed with code {code}: {stderr}"
    assert "Suggested Sub-Issues" in stdout, "Missing header in output"
    assert "story points" in stdout, "Missing effort estimation"
    assert "Phase" in stdout, "Missing phase sections"
    assert "design_0001" in stdout, "Missing task IDs"
    print("✓ Basic development task test passed")


def test_research_task():
    """Test research task decomposition"""
    print("Testing: Research task...")
    code, stdout, stderr = run_suggester("Research task", task_type="research")
    
    assert code == 0, f"Script failed with code {code}: {stderr}"
    assert "Literature survey" in stdout, "Missing research phase"
    assert "research" in stdout.lower(), "Missing research context"
    print("✓ Research task test passed")


def test_documentation_task():
    """Test documentation task decomposition"""
    print("Testing: Documentation task...")
    code, stdout, stderr = run_suggester("Write docs", task_type="documentation")
    
    assert code == 0, f"Script failed with code {code}: {stderr}"
    assert "documentation outline" in stdout.lower(), "Missing doc phase"
    print("✓ Documentation task test passed")


def test_with_description():
    """Test with description parameter"""
    print("Testing: Task with description...")
    code, stdout, stderr = run_suggester(
        "Complex task",
        description="This is a detailed description",
        task_type="development"
    )
    
    assert code == 0, f"Script failed with code {code}: {stderr}"
    assert "Complex task" in stdout, "Missing title in output"
    print("✓ Task with description test passed")


def test_dependency_tracking():
    """Test that dependencies are properly tracked"""
    print("Testing: Dependency tracking...")
    code, stdout, stderr = run_suggester("Dependency test", task_type="development")
    
    assert code == 0, f"Script failed with code {code}: {stderr}"
    # Check that there are dependencies mentioned (except for first task)
    assert "Depends on:" in stdout, "Missing dependency tracking"
    assert "(blocks)" in stdout, "Missing dependency type"
    print("✓ Dependency tracking test passed")


def test_critical_path():
    """Test that critical path is identified"""
    print("Testing: Critical path identification...")
    code, stdout, stderr = run_suggester("Critical path test", task_type="architecture")
    
    assert code == 0, f"Script failed with code {code}: {stderr}"
    assert "CRITICAL PATH" in stdout, "Missing critical path markers"
    assert "Critical Path:" in stdout, "Missing critical path summary"
    print("✓ Critical path test passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Running Sub-Issue Suggester Integration Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_basic_development_task,
        test_research_task,
        test_documentation_task,
        test_with_description,
        test_dependency_tracking,
        test_critical_path,
    ]
    
    failed = []
    
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed.append(test.__name__)
        print()
    
    print("=" * 60)
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed:")
        for name in failed:
            print(f"  - {name}")
        return 1
    else:
        print(f"SUCCESS: All {len(tests)} tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
