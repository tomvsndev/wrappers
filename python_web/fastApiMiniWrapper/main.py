import sys
import setproctitle
import os
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from helpers.fast_api_setup import FastApiSetup
from utils.logger import setup_logger
from utils.validate_env import load_config

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_file = os.getenv("LOG_FILE", "logs").lower()
SERVER_TITLE = os.getenv("SERVER_TITLE", 'None')
logger = setup_logger(log_level=log_level, log_file=log_file)


# Configure enviroment settings what will be accesed later over config dict
# Validate configuration before proceeding add t

required_keys = [
    "SERVER_TITLE",
    "DESCRIPTION",
    "VERSION",
    "HOST",
    "PORT",
    "LOG_LEVEL",
    "LOG_FILE",
    "RELOAD",
    "CORS_ORIGINS",
    "MAX_REQUEST_SIZE",

]

try:
    config = load_config(logger, required_keys)
    if isinstance(config, list):
        logger.error("[main] Configuration loading failed due to missing keys")
        sys.exit(1)
    elif not isinstance(config, dict):
        logger.error("[main] Configuration loading failed unexpectedly")
        sys.exit(1)
except Exception as e:
    logger.error(f"[main] Failed to load configuration: {str(e)}")
    sys.exit(1)

class Main:
    def __init__(self):
        # Initialize the FastAPI application with CORS and lifespan
        self.app = FastApiSetup().app_create(
            lifespan=self.lifespan,
            title=os.getenv("SERVER_TITLE", 'None'),
            description=os.getenv("DESCRIPTION", 'None'),
            version=os.getenv("VERSION", 'None'),
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
            allow_headers=["*"],
            allow_methods=["*"]
        )


    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        try:
            #add your function here what will run constanly like time watcher etc...

            yield
        finally:
            logger.info("[main] Server is shutting down.")

setproctitle.setproctitle(SERVER_TITLE)
logger.info(f"[main] Setting server name under {SERVER_TITLE}")
# Create the main application instance
app = Main().app

def main():
    """Main entry point"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    logger.info(f"[main] Starting - {SERVER_TITLE} on {host}:{port}")

  

    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level
        )
    except Exception as e:
        logger.error(f"[main] Failed to start Uvicorn: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()