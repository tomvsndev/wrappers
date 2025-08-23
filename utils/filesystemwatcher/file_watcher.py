

import asyncio
from pathlib import Path
from typing import Optional, Callable, Any
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pydantic import BaseModel, Field, validator


class FileWatcherConfig(BaseModel):
    """Configuration for file watcher"""

    watch_directory: str = Field(..., description="Directory to watch")
    file_extension: str = Field(".*", description="File extension to watch")
    recursive: bool = Field(True, description="Watch subdirectories")
    debounce_delay: float = Field(0.5, description="Debounce delay in seconds")

    @validator("watch_directory")
    def validate_directory(cls, v):
        """Ensure the watch_directory exists and is a directory"""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Directory does not exist: {v}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {v}")
        return str(path.absolute())

class AsyncFileWatcher(FileSystemEventHandler):
    """Async file system watcher wrapper for handling file events with callbacks"""

    def __init__(
            self,
            config: FileWatcherConfig,
            on_created: Optional[Callable[[str], Any]] = None,
            on_deleted: Optional[Callable[[str], Any]] = None,
            on_modified: Optional[Callable[[str], Any]] = None,
            on_moved: Optional[Callable[[str, str], Any]] = None,
            logger: Optional[object] = None,
            verbose: bool = True,
            verbose_level: str = "INFO",  # INFO/DEBUG/ERROR/WARNING/CRITICAL
    ):
        """Initialize watcher with config, callbacks, and optional logger"""
        self.config = config
        self.on_created_cb = on_created
        self.on_deleted_cb = on_deleted
        self.on_modified_cb = on_modified
        self.on_moved_cb = on_moved

        self.observer: Optional[Observer] = None
        self.event_queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        self.loop = asyncio.get_event_loop()

        # logging setup
        self.logger = logger
        self.verbose = verbose
        self.verbose_level = verbose_level

    def _log(self, message: str, level: str = "INFO"):
        """Helper to log messages either using provided logger or fallback to print"""
        if self.logger:
            log_fn = getattr(self.logger, level.lower(), None)
            if callable(log_fn):
                log_fn(message)
            else:
                self.logger.info(message)
        elif self.verbose:
            print(f"[{level}] {message}")

    # ---------------- Watchdog event hooks ----------------

    def on_created(self, event):
        """Handle file created event"""
        if not event.is_directory and event.src_path.endswith(self.config.file_extension):
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(("created", event.src_path)), self.loop
            )
            self._log(f"File created: {event.src_path}", self.verbose_level)

    def on_deleted(self, event):
        """Handle file deleted event"""
        if not event.is_directory and event.src_path.endswith(self.config.file_extension):
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(("deleted", event.src_path)), self.loop
            )
            self._log(f"File deleted: {event.src_path}", self.verbose_level)

    def on_modified(self, event):
        """Handle file modified event"""
        if not event.is_directory and event.src_path.endswith(self.config.file_extension):
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(("modified", event.src_path)), self.loop
            )
            self._log(f"File modified: {event.src_path}", self.verbose_level)

    def on_moved(self, event):
        """Handle file moved/renamed event"""
        if not event.is_directory and event.dest_path.endswith(self.config.file_extension):
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(("moved", event.src_path, event.dest_path)),
                self.loop,
            )
            self._log(
                f"File moved: {event.src_path} -> {event.dest_path}", self.verbose_level
            )

    # ---------------- Internal async event loop ----------------

    async def _process_events(self):
        """Process queued filesystem events and call appropriate callbacks"""
        while True:
            event_type, *paths = await self.event_queue.get()

            try:
                if event_type == "created" and self.on_created_cb:
                    await self._execute_callback(self.on_created_cb, paths[0])
                elif event_type == "deleted" and self.on_deleted_cb:
                    await self._execute_callback(self.on_deleted_cb, paths[0])
                elif event_type == "modified" and self.on_modified_cb:
                    await self._execute_callback(self.on_modified_cb, paths[0])
                elif event_type == "moved" and self.on_moved_cb:
                    await self._execute_callback(self.on_moved_cb, paths[0], paths[1])

            except Exception as e:
                self._log(f"Error processing event: {e}", level="ERROR")
            finally:
                self.event_queue.task_done()

    async def _execute_callback(self, callback, *args):
        """Execute callback with proper async/await handling"""
        if asyncio.iscoroutinefunction(callback):
            await callback(*args)
        else:
            callback(*args)

    # ---------------- Public API ----------------

    async def start(self):
        """Start the file watcher and begin observing events"""
        Path(self.config.watch_directory).mkdir(parents=True, exist_ok=True)
        self.processing_task = asyncio.create_task(self._process_events())

        self.observer = Observer()
        self.observer.schedule(
            self, self.config.watch_directory, recursive=self.config.recursive
        )
        self.observer.start()

        self._log(
            f"Watching directory: {self.config.watch_directory} for {self.config.file_extension} files",
            self.verbose_level,
        )

    async def stop(self):
        """Stop the file watcher and cleanup resources"""
        if self.observer:
            self.observer.stop()
            self.observer.join()

        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass

        self._log("File watcher stopped", "INFO")
