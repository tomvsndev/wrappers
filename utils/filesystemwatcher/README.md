# AsyncFileWatcher

> **Async-compatible filesystem monitoring with zero-configuration setup**

A reusable asynchronous wrapper around watchdog for monitoring filesystem events (create, delete, modify, move) with optional logging and callback support.

## ✨ Features

- **🔄 Async-compatible** - File watching using asyncio with callback support
- **📁 Auto-creation** - Automatically creates watch directories if missing
- **🎯 Event Callbacks** - Handle created, deleted, modified, and moved events
- **🪶 Lightweight** - Optional logger integration with print fallback
- **⚙️ Configurable** - Pydantic-based configuration with validation
- **🎛️ Flexible** - Supports both sync and async callbacks

## 📦 Installation

```bash
pip install watchdog pydantic
```

## ⚡ Quick Start

```python
import asyncio
from async_file_watcher import AsyncFileWatcher, FileWatcherConfig

async def on_created(path):
    print(f"New file detected: {path}")

async def main():
    config = FileWatcherConfig(watch_directory="./watched")
    watcher = AsyncFileWatcher(config, on_created=on_created)
    await watcher.start()
    
    try:
        await asyncio.Future()  # run forever
    except KeyboardInterrupt:
        await watcher.stop()

asyncio.run(main())
```

## 🎮 Usage Examples

### Simple File Monitoring

```python
import asyncio
from async_file_watcher import AsyncFileWatcher, FileWatcherConfig

def on_deleted(path):
    print(f"Deleted file: {path}")

async def main():
    config = FileWatcherConfig(watch_directory="./data")
    watcher = AsyncFileWatcher(config, on_deleted=on_deleted, verbose=True)
    await watcher.start()
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        await watcher.stop()

asyncio.run(main())
```

### With Logger Integration

```python
import asyncio
import logging
from async_file_watcher import AsyncFileWatcher, FileWatcherConfig

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FileWatcher")

def on_modified(path):
    logger.info(f"Modified: {path}")

async def main():
    config = FileWatcherConfig(watch_directory="./logs", file_extension=".txt")
    watcher = AsyncFileWatcher(config, on_modified=on_modified, logger=logger)
    await watcher.start()
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        await watcher.stop()

asyncio.run(main())
```

## ⚙️ Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `watch_directory` | Directory path to watch (required) | - |
| `file_extension` | Only watch files matching this extension | `".*"` |
| `recursive` | Watch subdirectories | `True` |
| `debounce_delay` | Debounce delay in seconds | `0.5` |

## 🎯 Event Callbacks

Available callback hooks:

- **`on_created`** - Triggered when files are created
- **`on_deleted`** - Triggered when files are deleted  
- **`on_modified`** - Triggered when files are modified
- **`on_moved`** - Triggered when files are moved/renamed

## 🔧 Advanced Features

### Multiple Event Handlers

```python
async def main():
    config = FileWatcherConfig(watch_directory="./monitored")
    
    watcher = AsyncFileWatcher(
        config,
        on_created=lambda path: print(f"➕ Created: {path}"),
        on_deleted=lambda path: print(f"➖ Deleted: {path}"),
        on_modified=lambda path: print(f"✏️ Modified: {path}"),
        verbose=True
    )
    
    await watcher.start()
```

### Custom Logger Integration

```python
class CustomLogger:
    def info(self, msg): print(f"[INFO] {msg}")
    def error(self, msg): print(f"[ERROR] {msg}")

config = FileWatcherConfig(watch_directory="./files")
watcher = AsyncFileWatcher(
    config, 
    logger=CustomLogger(),
    verbose_level="DEBUG"
)
```

## 💡 Use Cases

- **📄 Document Processing** - Auto-process files as they're added
- **📊 Log Monitoring** - Real-time log file analysis
- **🔄 File Sync** - Trigger sync operations on file changes
- **🎯 Build Automation** - Watch source files for automatic builds
- **📱 Hot Reloading** - Development server file watching

## 🛠️ API Reference

### `FileWatcherConfig`
Pydantic model for configuration validation.

### `AsyncFileWatcher(config, **callbacks)`
Main watcher class with event handling.

### `await start()`
Start watching the configured directory.

### `await stop()`
Stop watching and cleanup resources.

---

> *"Watch files, not the clock"* ⏰

**Happy File Watching!** 👀
