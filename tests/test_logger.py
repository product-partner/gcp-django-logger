import json
import logging
import os
import sys
from unittest import TestCase, mock

from gcp_django_logger import CloudRunJsonFormatter, setup_logger


class TestCloudRunJsonFormatter(TestCase):
    def setUp(self):
        self.formatter = CloudRunJsonFormatter()
        self.log_record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )

    def test_devo_format(self):
        with mock.patch.dict(os.environ, {"ENVIRONMENT": "devo"}):
            formatter = CloudRunJsonFormatter()
            formatted = formatter.format(self.log_record)
            self.assertIn("[INFO]", formatted)
            self.assertIn("test_file.py:42", formatted)
            self.assertIn("Test message", formatted)

    def test_prod_format(self):
        with mock.patch.dict(os.environ, {"ENVIRONMENT": "prod"}):
            formatter = CloudRunJsonFormatter()
            formatted = formatter.format(self.log_record)
            log_dict = json.loads(formatted)
            
            # Check required fields
            self.assertEqual(log_dict["severity"], "INFO")
            self.assertIn("timestamp", log_dict)
            self.assertTrue(log_dict["timestamp"].endswith("Z"))  # Check for Z-normalization
            self.assertEqual(log_dict["resource"], {"type": "global"})
            
            # Check message in jsonPayload
            self.assertEqual(log_dict["jsonPayload"]["message"], "Test message")
            
            # Check source location
            self.assertEqual(
                log_dict["logging.googleapis.com/sourceLocation"],
                {
                    "file": "test_file.py",
                    "line": 42,
                    "function": "None"
                }
            )

    def test_different_log_levels(self):
        with mock.patch.dict(os.environ, {"ENVIRONMENT": "prod"}):
            formatter = CloudRunJsonFormatter()
            levels = {
                logging.NOTSET: "DEFAULT",
                logging.DEBUG: "DEBUG",
                logging.INFO: "INFO",
                logging.WARNING: "WARNING",
                logging.ERROR: "ERROR",
                logging.CRITICAL: "CRITICAL"
            }
            
            for level, expected in levels.items():
                record = logging.LogRecord(
                    name="test_logger",
                    level=level,
                    pathname="test_file.py",
                    lineno=42,
                    msg="Test message",
                    args=(),
                    exc_info=None
                )
                formatted = formatter.format(record)
                log_dict = json.loads(formatted)
                self.assertEqual(log_dict["severity"], expected)

    def test_extra_fields(self):
        with mock.patch.dict(os.environ, {"ENVIRONMENT": "prod"}):
            formatter = CloudRunJsonFormatter()
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="test_file.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None
            )
            record.user_id = "123"
            record.request_id = "abc-xyz"
            
            formatted = formatter.format(record)
            log_dict = json.loads(formatted)
            
            # Extra fields should be in jsonPayload
            self.assertEqual(log_dict["jsonPayload"]["user_id"], "123")
            self.assertEqual(log_dict["jsonPayload"]["request_id"], "abc-xyz")

    def test_exception_handling(self):
        with mock.patch.dict(os.environ, {"ENVIRONMENT": "prod"}):
            formatter = CloudRunJsonFormatter()
            try:
                raise ValueError("Test error")
            except ValueError:
                record = logging.LogRecord(
                    name="test_logger",
                    level=logging.ERROR,
                    pathname="test_file.py",
                    lineno=42,
                    msg="Error occurred",
                    args=(),
                    exc_info=sys.exc_info()
                )
            
            formatted = formatter.format(record)
            log_dict = json.loads(formatted)
            
            # Check that exception is in jsonPayload
            self.assertIn("exception", log_dict["jsonPayload"])
            self.assertIn("ValueError: Test error", log_dict["jsonPayload"]["exception"])
            self.assertEqual(log_dict["severity"], "ERROR")


class TestSetupLogger(TestCase):
    def test_logger_setup(self):
        logger = setup_logger("test_logger", "DEBUG")
        
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 1)
        
        handler = logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertIsInstance(handler.formatter, CloudRunJsonFormatter)

    def test_logger_removes_existing_handlers(self):
        logger = logging.getLogger("test_logger_handlers")
        original_handler = logging.StreamHandler()
        logger.addHandler(original_handler)
        
        # Setup logger should remove the existing handler
        setup_logger("test_logger_handlers")
        self.assertEqual(len(logger.handlers), 1)
        self.assertNotEqual(logger.handlers[0], original_handler)

    def test_default_log_level(self):
        logger = setup_logger("test_logger_default")
        self.assertEqual(logger.level, logging.INFO)
