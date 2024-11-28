# Contributing to Key Generator

## Welcome Contributors!

We appreciate your interest in contributing to the Key Generator project. This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the Repository**
   - Fork the project on GitHub
   - Clone your forked repository locally

2. **Set Up Development Environment**
   ```bash
   # Clone the repository
   git clone https://github.com/your-username/key-generator.git
   cd key-generator

   # Create a virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Contributing Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow PEP 8 style guidelines
   - Write clear, concise code
   - Add/update tests for new functionality
   - Ensure all tests pass

3. **Commit Changes**
   - Use descriptive commit messages
   ```bash
   git add .
   git commit -m "Add detailed description of changes"
   ```

4. **Run Tests**
   ```bash
   pytest tests/
   bandit -r .
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Open a pull request on GitHub
   - Describe the purpose and details of your changes

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help maintain a welcoming community

## Reporting Issues

- Use GitHub Issues to report bugs
- Include detailed information:
  - Steps to reproduce
  - Expected vs. actual behavior
  - Environment details

## Questions?

If you have questions, please open an issue or reach out to the maintainers.

Thank you for contributing!
