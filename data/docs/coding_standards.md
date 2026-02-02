# Python Coding Standards and Best Practices
## Reference Document for AI Code Review Assistant

## 1. Naming Conventions (PEP 8)

### Variables and Functions
- Use `snake_case` for variable and function names
- Use descriptive names that indicate purpose
- Avoid single-letter names except for counters

### Classes
- Use `PascalCase` for class names
- Class names should be nouns

### Constants
- Use `UPPER_SNAKE_CASE` for constants

## 2. Code Structure

### Function Length
- Functions should do one thing well
- Aim for functions under 20 lines
- If a function is too long, refactor into smaller functions

### Import Organization
1. Standard library imports
2. Related third-party imports
3. Local application imports

## 3. Documentation

### Docstrings
- All public modules, functions, classes should have docstrings
- Use Google or NumPy style docstrings
- Include Args, Returns, Raises sections

### Comments
- Use comments to explain "why", not "what"
- Keep comments up to date with code changes

## 4. Error Handling

### Best Practices
- Catch specific exceptions, not bare except
- Always clean up resources (use context managers)
- Raise exceptions with meaningful messages

## 5. Security Guidelines

### Never Hardcode
- API keys
- Passwords
- Database credentials
- Use environment variables instead

### Input Validation
- Always validate user input
- Use parameterized queries for databases
- Sanitize data before display

## 6. Performance

### Avoid
- Nested loops when possible
- Repeated expensive operations
- Loading large files into memory

### Prefer
- List comprehensions over loops
- Generators for large datasets
- Caching for repeated computations
