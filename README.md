# GCP Django Logger

A Django-compatible logging formatter that automatically switches between development-friendly logging and Google Cloud Platform (GCP) compatible JSON logging based on the environment.

## Installation

```bash
pip install gcp-django-logger
```

## Features

- 🔄 Automatic environment detection (development vs production)
- 📊 GCP-compatible JSON logging format in production
- 👩‍💻 Human-readable logging format in development
- 🏗️ Support for structured logging with extra fields
- ⚠️ Proper exception formatting
- 🎯 Compatible with Google Cloud Run severity levels

## Usage

```python
from gcp_django_logger import setup_logger

# Create a logger for your module
logger = setup_logger(__name__)

# Basic logging
logger.info("User logged in successfully")
logger.error("Failed to process request")

# Structured logging with extra fields
logger.info(
    "Payment processed", 
    extra={'extra_fields': {'user_id': '123', 'amount': 99.99}}
)

# Exception logging
try:
    raise ValueError("Invalid input")
except Exception as e:
    logger.exception("Error processing request")
```

## Environment Configuration

The logger checks the `ENVIRONMENT` environment variable to determine whether to use GCP-compatible JSON logging:

- If `ENVIRONMENT=production`: Uses GCP JSON format
- Otherwise: Uses human-readable format

## Log Format

### Production (GCP Format)
```json
{
    "message": "User logged in successfully",
    "severity": "INFO",
    "time": "2025-02-13T23:42:07Z",
    "logging.googleapis.com/sourceLocation": {
        "file": "views.py",
        "line": 42,
        "function": "login_view"
    },
    "user_id": "123"  // Extra fields are included at the root level
}
```

### Development Format
```
[INFO] views.py:42 - User logged in successfully
```

## Django Settings Configuration

Add the following to your Django settings to configure the logger:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'gcp': {
            '()': 'gcp_django_logger.CloudRunJsonFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'gcp',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
