# Tests Directory

This directory contains tests for the Z Cartridge project.

## Running Tests

Run all tests using npm:
```bash
npm test
```

Or run Python tests directly:
```bash
python3 tests/test_sub_issue_suggester.py
```

## Test Coverage

### Integration Tests

- **test_sub_issue_suggester.py** - Integration tests for the sub-issue suggester tool
  - Tests all task types (development, research, analysis, testing, documentation, architecture)
  - Verifies dependency tracking
  - Checks critical path identification
  - Validates output format

## Adding New Tests

When adding new tests:

1. Create test files with the prefix `test_`
2. Use descriptive test function names
3. Add assertions with clear error messages
4. Update this README with new test descriptions
5. Run tests locally before committing

## Test Requirements

- Python 3.7+
- Access to the scripts being tested
- No external dependencies beyond Python standard library

## CI/CD Integration

Tests are automatically run as part of the CI pipeline defined in `.github/workflows/main.yml`.

## Future Test Plans

- Unit tests for task_decomposer.py
- Unit tests for swarm coordinator
- Integration tests for swarm assemblies
- End-to-end tests for workflow execution
