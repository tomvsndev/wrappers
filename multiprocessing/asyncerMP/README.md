# AsyncerMp: Hybrid Async + Multiprocessing Task Runner

> **Execute CPU-heavy async tasks in parallel without blocking your event loop**

AsyncerMp combines the power of asyncio and multiprocessing to handle computationally intensive workloads efficiently while maintaining the benefits of asynchronous programming. Perfect for integrating heavy computations seamlessly into async-based applications.

## 🚀 Features

- **🔄 Hybrid Execution** - Combines asyncio for non-blocking I/O with multiprocessing for CPU-bound tasks
- **📋 Task Queueing** - Manages task queue with controlled execution and concurrent process limits
- **⚖️ Scalable Concurrency** - Semaphore-based process limiting prevents system resource overload
- **📊 Result Tracking** - Uses `asyncio.Future` objects for task result and completion status tracking
- **🛡️ Error Handling** - Captures and logs subprocess exceptions with robust error reporting
- **🎯 Completion Events** - Public `completed_queue` for monitoring task completion events

## 📦 Installation

```bash
pip install psutil
```

Clone and include `asyncermp.py` in your project.

**Requirements:** Python 3.7+

## ⚡ Quick Start

```python
import asyncio
from asyncermp import AsyncerMp

class MockHeavyTask:
    async def run(self, task_data):
        n = task_data['n']
        result = sum(i * i for i in range(n))  # CPU-heavy calculation
        await asyncio.sleep(0.01)  # Simulate async operation
        return {"uid": task_data['uid'], "result": result}

async def main():
    wrapper = AsyncerMp(max_processes=4)  # Limit to 4 concurrent processes
    asyncio.create_task(wrapper._runner())  # Start the background runner
    
    # Submit tasks
    tasks = []
    for i in range(8):
        data = {"uid": f"task-{i}", "n": 10_000_000, "data": i}
        fut = await wrapper.submit(data, MockHeavyTask().run, uid=data["uid"])
        tasks.append((data["uid"], fut))
    
    # Collect results
    for uid, fut in tasks:
        result = await fut
        print(f"Task {uid} completed with result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🎯 How It Works

### **Task Submission**
The `submit()` method queues tasks with unique IDs, task data, and async functions. Each task gets an `asyncio.Future` for result tracking.

### **Task Execution**  
The `_runner()` coroutine continuously pulls tasks from the queue and launches them in separate processes. A semaphore ensures no more than `max_processes` run concurrently.

### **Subprocess Handling**
Each task runs in a new process with its own event loop. Results or errors are sent back via `multiprocessing.Pipe`.

### **Result Collection**
The main process receives results and sets them on corresponding Futures. Task completion events are pushed to `completed_queue`.

## 📈 Performance Example

Running the included example shows dramatic performance improvements:

```
LOOP:1, PROCESS_LOAD%:0.0, dt:2025-08-20 14:05:23.123456
LOOP:2, PROCESS_LOAD%:85.0, dt:2025-08-20 14:05:24.123456
[MP] Finished in 5.32 seconds
Detected MP completion, starting run_no_mp
[No MP] Blocked due to cpu load
[No MP] Finished in 12.45 seconds
```

**2.3x faster** execution with multiprocessing! 🚀

## 🎮 Running the Example

```bash
python example.py
```

The example compares CPU-heavy task execution with and without multiprocessing, showing real-time CPU usage and completion times.

## 💡 Use Cases

- **🧮 CPU-Intensive Tasks** - Data processing, numerical computations, ML inference
- **🌐 Async Applications** - Web servers, real-time systems integration  
- **⚡ Resource-Constrained Environments** - Semaphore-based concurrency control

## ⚠️ Limitations

- **Process Overhead** - Best suited for computationally expensive tasks
- **Serialization** - Task data and results must be serializable
- **Windows Compatibility** - Different multiprocessing behavior on Windows

## 🔧 API Reference

### `AsyncerMp(max_processes=4, logger=None)`
Initialize the task runner with process limits and optional logging.

### `await submit(task_data, async_func, uid=None)`
Submit a task for execution. Returns `asyncio.Future` for result tracking.

### `completed_queue`
Public queue for monitoring task completion events.

---

> *"Don't let CPU-heavy tasks block your async dreams"* ⚡

**Happy Parallel Processing!** 🚀
