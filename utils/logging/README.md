Python Logging Wrapper
A simplified logging wrapper that automates file creation, provides colored console output, and structures error logs as JSON - all while maintaining full compatibility with Python's standard logging module.
Overview
This is a convenience wrapper around Python's built-in logging module that automatically handles:
    • ✅ Automatic log file creation and directory structure
    • ✅ Colored console output for better readability
    • ✅ JSON-formatted error logs with complete traceback information
    • ✅ Log rotation with configurable size limits
    • ✅ Severity-based log file separation
    • ✅ Environment-based configuration
Installation
bash
pip install colorlog pydantic-settings
Quick Start
Basic Usage
python
from your_logging_module import Logger

# Initialize the logger manager
logger_manager = Logger()

# Get a logger (auto-creates files if needed)
logger = logger_manager.setup_logger()

# Use it like standard logging
logger.debug("Debug message")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Automatic JSON formatting for exceptions
try:
    result = 10 / 0
except Exception:
    logger.exception("Division failed")  # Auto-formats as JSON with traceback
Environment Configuration
Create a .env file:
env
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
ENABLE_SEVERITY_FILES=true
MAX_LOG_SIZE_MB=10
BACKUP_COUNT=5
Per-File/Class Logging (Recommended)
python
# In each file, create a dedicated logger
from your_logging_module import Logger

logger_manager = Logger()
logger = logger_manager.setup_logger(logger_name=__name__)  # Use module name

class DatabaseService:
    def __init__(self):
        # Or create class-specific logger
        self.logger = logger_manager.setup_logger(
            logger_name=f"database.{self.__class__.__name__}"
        )
    
    def query(self, sql):
        self.logger.debug(f"Executing: {sql}")
        try:
            # Database operations
            self.logger.info("Query successful")
        except Exception:
            self.logger.exception("Query failed")  # Auto JSON with traceback
Key Features
1. Automatic File Management
No need to manually create directories or files:
python
# This automatically creates:
# - logs/app.log (main log)
# - logs/severity/warning.log
# - logs/severity/error.log  
# - logs/severity/critical.log
logger = logger_manager.setup_logger(
    config=LoggerConfig(
        LOG_FILE="logs/app.log",
        ENABLE_SEVERITY_FILES=True
    )
)
2. Colored Console Output
Easily distinguish log levels with color-coded messages in your terminal.
3. Structured Error Logging
Exceptions are automatically formatted as JSON with full context:
json
{
  "error_type": "ZeroDivisionError",
  "error_message": "division by zero",
  "file": "example.py",
  "line": 15,
  "function": "calculate",
  "traceback": "Traceback (most recent call last)...",
  "timestamp": "2023-11-15 10:30:45",
  "level": "ERROR",
  "logger": "main",
  "message": "Calculation failed"
}
4. Multiple Logger Support
Create different loggers for various components:
python
# Main application logger
app_logger = logger_manager.setup_logger(
    logger_name="app",
    config=LoggerConfig(LOG_FILE="logs/app.log")
)

# Database logger  
db_logger = logger_manager.setup_logger(
    logger_name="database",
    config=LoggerConfig(LOG_FILE="logs/db.log")
)

# API logger
api_logger = logger_manager.setup_logger(
    logger_name="api",
    config=LoggerConfig(LOG_FILE="logs/api.log")
)
Best Practices
1. Use Module-Based Loggers
python
# In each Python file
import os
from your_logging_module import Logger

logger_manager = Logger()
logger = logger_manager.setup_logger(logger_name=__name__)

def some_function():
    logger.info("This message will show the module name")
2. Add Context to Logs
python
# Add contextual information
def process_request(request_id, user_id):
    logger.info("Processing request", extra={
        'request_id': request_id,
        'user_id': user_id
    })
3. Use Appropriate Log Levels
python
logger.debug("Detailed debugging info")  # For development
logger.info("Normal operation messages")  # For tracking flow
logger.warning("Unexpected but handled situations")  # For potential issues
logger.error("Operation failures")  # For handled exceptions
logger.critical("System-level failures")  # For catastrophic errors
4. Leverage JSON Error Formatting
python
try:
    risky_operation()
except Exception:
    # This automatically creates a JSON log with full traceback
    logger.exception("Operation failed")
    
    # Instead of:
    # logger.error("Operation failed", exc_info=True)  # Standard approach
Configuration Options
Setting
Description
Default
LOG_LEVEL
Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
INFO
LOG_FILE
Main log file path (None for console only)
None
ENABLE_SEVERITY_FILES
Create separate files for WARNING/ERROR/CRITICAL
True
SEVERITY_FILES_DIR
Directory for severity-specific files
"logs/severity"
MAX_LOG_SIZE_MB
Max log file size before rotation (MB)
10
BACKUP_COUNT
Number of backup files to keep
5
Complete Example
python
from your_logging_module import Logger, LoggerConfig

# Initialize
logger_manager = Logger()

# Configure based on environment
config = LoggerConfig(
    LOG_LEVEL="DEBUG",
    LOG_FILE="logs/myapp.log",
    ENABLE_SEVERITY_FILES=True
)

# Create logger
logger = logger_manager.setup_logger(
    config=config,
    logger_name="myapp.service"
)

# Use it
logger.info("Application started")

try:
    result = process_data()
    logger.debug(f"Processing result: {result}")
except ValidationError as e:
    logger.warning(f"Validation issue: {e}")
except Exception as e:
    logger.exception("Unexpected error during processing")

logger.info("Application shutting down")

# Clean up
logger_manager.close_all_loggers()
Migration from Standard Logging
If you're already using Python's logging:
python
# Before (standard logging)
import logging
logging.basicConfig(level=logging.INFO, filename='app.log')
logger = logging.getLogger(__name__)

# After (with this wrapper)
from your_logging_module import Logger
logger_manager = Logger()
logger = logger_manager.setup_logger(
    logger_name=__name__,
    config=LoggerConfig(LOG_FILE="app.log", LOG_LEVEL="INFO")
)

# All your existing logging calls work exactly the same:
logger.info("This works exactly like before")
logger.error("But now with added benefits!")
Benefits Over Standard Logging
    1. No setup boilerplate - Automatic file/directory creation
    2. Better error reporting - JSON-formatted exceptions with full context
    3. Visual differentiation - Colored console output
    4. Structured organization - Severity-based file separation
    5. Environment-based config - Easy configuration through environment variables
Troubleshooting
Log files not created? Check write permissions to the log directory.
Missing logs? Verify your LOG_LEVEL setting isn't filtering out messages.

This wrapper maintains 100% compatibility with standard Python logging while adding convenient features for automatic file management, structured error logging, and better visual output.

