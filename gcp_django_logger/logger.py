import json
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime, UTC

class CloudRunJsonFormatter(logging.Formatter):
    """
    A logging formatter that outputs logs in a format compatible with Google Cloud Run.
    In development, it falls back to a more readable format.
    """
    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        env = os.getenv('ENVIRONMENT', 'devo').lower()
        use_gcp_format = env in ['prod', 'staging', 'gamma']
        if use_gcp_format:
            return self._format_for_cloud_run(record)
        return self._format_for_development(record)

    def _format_for_cloud_run(self, record: logging.LogRecord) -> str:
        # Map Python logging levels to GCP severity levels
        severity_map = {
            'NOTSET': 'DEFAULT',
            'DEBUG': 'DEBUG',
            'INFO': 'INFO',
            'WARNING': 'WARNING',
            'ERROR': 'ERROR',
            'CRITICAL': 'CRITICAL'
        }

        # Create the base log record
        log_record = {
            "message": record.getMessage(),  # Main message at the top level
            "severity": severity_map.get(record.levelname, 'DEFAULT'),
            "file": record.filename,
            "line": record.lineno,
            "function": str(record.funcName),
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat() + 'Z'
        }

        # Include exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Include all extra attributes at the top level
        for key, value in record.__dict__.items():
            if key not in ['args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                          'funcName', 'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated',
                          'stack_info', 'thread', 'threadName']:
                log_record[key] = value

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
