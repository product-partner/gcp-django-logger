import json
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

class CloudRunJsonFormatter(logging.Formatter):
    """
    A logging formatter that outputs logs in a format compatible with Google Cloud Run.
    In development, it falls back to a more readable format.
    """
    def __init__(self):
        super().__init__()
        self.is_prod = os.getenv('ENVIRONMENT', 'development').lower() == 'production'

    def format(self, record: logging.LogRecord) -> str:
        if self.is_prod:
            return self._format_for_cloud_run(record)
        return self._format_for_development(record)

    def _format_for_cloud_run(self, record: logging.LogRecord) -> str:
        # Map Python logging levels to GCP severity levels
        severity_map = {
            'DEBUG': 'DEBUG',
            'INFO': 'INFO',
            'WARNING': 'WARNING',
            'ERROR': 'ERROR',
            'CRITICAL': 'CRITICAL'
        }

        log_record = {
            "message": record.getMessage(),
            "severity": severity_map.get(record.levelname, record.levelname),
            "time": datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            "logging.googleapis.com/sourceLocation": {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName
            }
        }

        # Include exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Include custom fields if present
        if hasattr(record, 'extra_fields'):
            log_record.update(record.extra_fields)

        return json.dumps(log_record)

    def _format_for_development(self, record: logging.LogRecord) -> str:
        """Human-readable format for development environment"""
        return f'[{record.levelname}] {record.filename}:{record.lineno} - {record.getMessage()}'

def setup_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """
    Set up a logger with the CloudRunJsonFormatter.
    
    Args:
        name: The name of the logger (typically __name__)
        level: The logging level (default: 'INFO')
    
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setFormatter(CloudRunJsonFormatter())
    
    # Set levels
    logger.setLevel(level)
    handler.setLevel(level)
    
    logger.addHandler(handler)
    return logger
