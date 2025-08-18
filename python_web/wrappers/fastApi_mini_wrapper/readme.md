
# Mini fastApi Wrapper

Mini Wrapper is a lightweight FastAPI application designed for speedy development. It provides a simple and efficient way to set up and run a FastAPI server with various configurations and logging capabilities.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Application](#running-the-application)
4. [Environment Variables](#environment-variables)
5. [Logging](#logging)
6. [Dependencies](#dependencies)

## Installation

To install the required dependencies, you can use `pip` to install the packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt

Alternatively, you can use uv to manage your dependencies [RECOMMENDED]:
make sure uv exists on the system
 
then just copy toml file to your project dir ready to go.

Configuration

The application reads its configuration from the .env file and can also be configured via environment variables. The .env file is used as a fallback if the environment variables are not set.
Environment Variables

    SERVER_TITLE: Title of the server.
    DESCRIPTION: Description of the server.
    VERSION: Version of the server.
    HOST: Host address for the server (default: 0.0.0.0).
    PORT: Port number for the server (default: 8000).
    LOG_LEVEL: Logging level (default: info).
    LOG_FILE: Log file name (default: logs).
    RELOAD: Whether to enable auto-reload on code changes (default: false).
    CORS_ORIGINS: Comma-separated list of origins for CORS (default: *).
    MAX_REQUEST_SIZE: Maximum request size in bytes (default: 16777216).

Running the Application

To run the application, use the following command:

python main.py

Alternatively, you can use uvicorn directly:

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

or 

uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Environment Variables

You can set the environment variables in your shell or through a .env file. Here is an example of a .env file:

# .env
SERVER_TITLE=Your Title
DESCRIPTION=Your Description
VERSION=1.0.0
# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
LOG_FILE=logs
RELOAD=false

Logging

The application uses the logging module with colorlog for colored console output. You can configure the log level and log file in the .env file or via environment variables.
Dependencies

The project dependencies are managed using pip and are listed in requirements.txt and pyproject.toml. The required dependencies are:

    fastapi: A modern, fast (high-performance) web framework for building APIs with Python 3.9+.
    uvicorn: ASGI server for running FastAPI applications.
    python-dotenv: Loads environment variables from a .env file.
    setproctitle: Allows setting the process title.
    colorlog: Colored terminal logging.

Contributing

Contributions are welcome! If you find any issues or have suggestions, please open an issue or submit a pull request.
License

This project is licensed under the MIT License - see the LICENSE file for details.

For more information, please refer to the official documentation of the libraries used:

    FastAPI
    Uvicorn
    python-dotenv
    setproctitle
    colorlog

For detailed instructions on how to use the mini_wrapper project, please refer to the sections above. Make sure to adjust the placeholders and paths as needed for your specific use case
