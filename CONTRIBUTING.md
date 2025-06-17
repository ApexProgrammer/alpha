# Contributing to Alpha - Honeypot Threat Intelligence Solution

Thank you for your interest in contributing to the Alpha Honeypot project! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Issues
- Use the GitHub issue tracker to report bugs
- Check existing issues before creating a new one
- Provide clear, detailed descriptions with steps to reproduce
- Include system information (OS, Python version, etc.)

### Suggesting Enhancements
- Use GitHub issues to suggest new features
- Clearly describe the proposed enhancement
- Explain why this would be useful to other users
- Consider the scope and complexity of the change

### Pull Requests
1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Setup Steps
```bash
# Clone the repository
git clone https://github.com/ApexProgrammer/alpha.git
cd alpha

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py

# Start development server
python app.py
```

## Coding Standards

### Python Style Guide
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### Code Example
```python
def extract_features(username: str, password: str, ip_address: str) -> dict:
    """
    Extract machine learning features from login attempt data.
    
    Args:
        username: The attempted username
        password: The attempted password  
        ip_address: The source IP address
        
    Returns:
        Dictionary containing extracted features
        
    Raises:
        ValueError: If any input is invalid
    """
    if not all([username, password, ip_address]):
        raise ValueError("All parameters are required")
    
    return {
        'username_length': len(username),
        'password_length': len(password),
        'ip_numeric': ip_to_int(ip_address)
    }
```

### File Organization
- Keep related functions together
- Use clear module names
- Separate concerns (ML, web, config, etc.)
- Add appropriate imports at the top

## Testing

### Manual Testing
Before submitting changes, test:
- Basic login functionality
- Dashboard display and updates
- Model training and retraining
- Error handling

### Test Data
Use the included sample data or create your own test scenarios:
```bash
# The setup script creates initial test data automatically
python setup.py
```

### Browser Testing
Test the web interface in:
- Chrome/Chromium
- Firefox
- Safari (if available)
- Mobile browsers

## Documentation

### Code Documentation
- Add docstrings to all public functions
- Use clear, descriptive comments
- Update README.md for user-facing changes
- Document configuration options

### Commit Messages
Use clear, descriptive commit messages:
```
Add geolocation caching feature

- Implement IP address caching to reduce API calls
- Add cache expiration logic
- Update documentation for new config options
```

## Security Considerations

### Security Guidelines
- Never commit sensitive data (API keys, passwords)
- Validate all user inputs
- Use secure defaults in configuration
- Follow security best practices for web applications

### Sensitive Data
- Use environment variables for secrets
- Add sensitive files to .gitignore
- Review code for potential vulnerabilities

## Areas for Contribution

### High Priority
- **Enhanced ML Models**: Improve classification accuracy
- **Additional Visualizations**: New dashboard charts and metrics
- **Mobile Responsiveness**: Better mobile web interface
- **Performance Optimization**: Faster loading and processing

### Medium Priority
- **Docker Support**: Containerization for easy deployment
- **Database Integration**: Replace CSV with proper database
- **API Endpoints**: RESTful API for external integration
- **User Authentication**: Optional admin panel protection

### Nice to Have
- **Dark/Light Theme Toggle**: User preference support
- **Export Features**: CSV/JSON data export
- **Notification System**: Email/webhook alerts
- **Multi-language Support**: Internationalization

## Pull Request Checklist

Before submitting a pull request:

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have appropriate docstrings
- [ ] Changes are tested manually
- [ ] No sensitive data is committed
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary files are included
- [ ] Code is compatible with Python 3.8+

## Bug Report Template

When reporting bugs, please include:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python Version: [e.g. 3.9.0]
- Browser: [e.g. Chrome 96]

**Additional context**
Add any other context about the problem.
```

## Feature Request Template

For feature requests, please include:

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features considered.

**Additional context**
Add any other context or screenshots about the feature request.
```

## Getting Help

If you need help with development:

1. Check the existing documentation
2. Search existing issues
3. Ask questions in discussions
4. Contact the maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special mentions for outstanding contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Alpha - Honeypot Threat Intelligence Solution!
