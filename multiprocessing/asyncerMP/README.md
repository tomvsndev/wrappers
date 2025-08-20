AsyncerMp: Hybrid Async and Multiprocessing Task Runner
AsyncerMp is a Python library that combines the power of asyncio and multiprocessing to execute CPU-heavy asynchronous tasks in parallel without blocking the main event loop. It is designed to handle computationally intensive workloads efficiently while maintaining the benefits of asynchronous programming. This library is particularly useful for scenarios where you need to perform heavy computations in parallel but want to integrate them seamlessly into an async-based application.
Features

Hybrid Execution: Combines asyncio for non-blocking I/O with multiprocessing for CPU-bound tasks.
Task Queueing: Manages a queue of tasks to ensure controlled execution within a specified number of concurrent processes.
Scalable Concurrency: Limits the number of subprocesses with a semaphore to prevent overloading system resources.
Result Tracking: Uses asyncio.Future objects to track task results and completion status.
Error Handling: Captures and logs exceptions from subprocesses, ensuring robust error reporting.
Completion Events: Provides a public completed_queue for monitoring task completion events.

Installation
To use AsyncerMp, you need Python 3.7 or higher. The library depends on the standard library modules asyncio, multiprocessing, and uuid, as well as the psutil package for monitoring CPU usage in the example.
Install the required dependency:
pip install psutil

Clone the repository and include the asyncermp.py and example.py files in your project.
Usage
The library provides a simple interface to submit asynchronous tasks to be executed in separate processes. Below is an overview of how to use AsyncerMp with the provided example.
Key Components

AsyncerMp Class:

Initializes with a maximum number of concurrent processes (max_processes) and an optional logger.
Provides a submit method to queue tasks and a background _runner to manage task execution.
Maintains a completed_queue for task completion events.


Example Script (example.py):

Demonstrates the performance difference between running CPU-heavy tasks with and without multiprocessing.
Uses a MockHeavyTask class to simulate a computationally intensive task.
Monitors CPU usage and task completion times.



Example Code
Below is a simplified example of how to use AsyncerMp to run CPU-heavy tasks in parallel:
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

Running the Example
The provided example.py compares the execution of a CPU-heavy task with and without multiprocessing. To run it:

Save both asyncermp.py and example.py in the same directory.
Ensure psutil is installed (pip install psutil).
Run the script:

python example.py

The script will:

Execute 8 CPU-heavy tasks using AsyncerMp with multiprocessing.
Monitor CPU usage and print progress in a non-blocking loop.
After the multiprocessing tasks complete, run the same tasks sequentially without multiprocessing for comparison.
Output the completion times for both approaches.

Example Output
Running example.py will produce output similar to the following:
LOOP:1, PROCESS_LOAD%:0.0, dt:2025-08-20 14:05:23.123456
LOOP:2, PROCESS_LOAD%:85.0, dt:2025-08-20 14:05:24.123456
[MP] Finished in 5.32 seconds
Detected MP completion, starting run_no_mp
[No MP] Blocked due to cpu load
[No MP] Finished in 12.45 seconds

This demonstrates that AsyncerMp significantly reduces execution time for CPU-bound tasks by leveraging multiple processes.
How It Works

Task Submission:

The submit method queues tasks with a unique ID, task data, and an async function to execute.
Each task is associated with an asyncio.Future to track its result.


Task Execution:

The _runner coroutine continuously pulls tasks from the queue and launches them in separate processes using _run_task.
A semaphore ensures that no more than max_processes processes run concurrently.


Subprocess Handling:

Each task runs in a new process with its own event loop to execute the async function.
Results or errors are sent back to the main process via a multiprocessing.Pipe.


Result Collection:

The main process receives results and sets them on the corresponding Future.
Task completion events are pushed to the completed_queue for external monitoring.



Use Cases

CPU-Intensive Tasks: Ideal for tasks like data processing, numerical computations, or machine learning inference that benefit from parallel execution.
Async Applications: Integrates seamlessly with asyncio-based applications, such as web servers or real-time systems.
Resource-Constrained Environments: The semaphore-based concurrency control prevents overloading the system.

Limitations

Overhead: Spawning processes introduces some overhead, so AsyncerMp is best suited for tasks that are sufficiently computationally expensive.
Serialization: Task data and results must be serializable for inter-process communication.
Windows Compatibility: Multiprocessing behaves differently on Windows due to process creation mechanics. Ensure your async functions are compatible with multiprocessing on all platforms.

Contributing
Contributions are welcome! Please submit issues or pull requests to the GitHub repository. Ensure that any changes include tests and follow the coding style in the existing codebase.
License
This project is licensed under the MIT License. See the LICENSE file for details.
