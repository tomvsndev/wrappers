 

import multiprocessing as mp
import asyncio
import uuid
import traceback
from typing import Callable, Dict, Any
from multiprocessing.connection import Connection


class AsyncerMp:
    """
    A hybrid async + multiprocessing wrapper to execute heavy tasks in parallel without blocking the event loop.
    """

    def __init__(self, max_processes: int = 4, logger=None):
        """
        Args:
            max_processes (int): Max concurrent subprocesses allowed.
            logger: Optional logger with .debug and .error methods.
        """
        self.max_processes = max_processes
        self.logger = logger or (lambda: None)
        self.logger.debug = getattr(self.logger, 'debug', lambda x: None)
        self.logger.error = getattr(self.logger, 'error', lambda x: None)

        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._futures: Dict[str, asyncio.Future] = {}
        self._semaphore = asyncio.Semaphore(self.max_processes)

        self.completed_queue: asyncio.Queue = asyncio.Queue()  # Public event stream for task completions

    def _worker_process(self, task_data: Any, async_func: Callable, pipe_conn: Connection) -> None:
        """
        Internal method to run the async task inside a subprocess and send back the result.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(async_func(task_data))
            pipe_conn.send({"status": True, "data": result})
        except Exception as e:
            error_message = f"Worker failed: {e}. Traceback: {traceback.format_exc()}"
            self.logger.error(error_message)
            pipe_conn.send({"status": False, "data": None, "error": error_message})
        finally:
            loop.close()
            pipe_conn.close()

    async def submit(self, task_data: Any, async_func: Callable, uid: str = None) -> asyncio.Future:
        """
        Submit a task to the wrapper.

        Args:
            task_data: Data passed to your async function.
            async_func: The async function to execute.
            uid: Optional uid to identify the task in logs or background logger.

        Returns:
            asyncio.Future that will contain the task result.
        """
        task_id = str(uuid.uuid4())
        future = asyncio.get_running_loop().create_future()
        self._futures[task_id] = future
        await self._task_queue.put((task_id, task_data, async_func, uid or task_id))
        return future

    async def _runner(self):
        """
        Background coroutine that constantly picks tasks and launches them.
        """
        while True:
            task_id, task_data, async_func, uid = await self._task_queue.get()
            asyncio.create_task(self._run_task(task_id, task_data, async_func, uid))

    async def _run_task(self, task_id: str, task_data: Any, async_func: Callable, uid: str):
        """
        Internal coroutine that wraps each subprocess job and tracks its result.
        """
        async with self._semaphore:
            parent_conn, child_conn = mp.Pipe()
            process = mp.Process(
                target=self._worker_process,
                args=(task_data, async_func, child_conn)
            )
            process.start()

            try:
                result = await asyncio.get_event_loop().run_in_executor(None, parent_conn.recv)
                if task_id in self._futures and not self._futures[task_id].done():
                    self._futures[task_id].set_result(result)
                    await self.completed_queue.put((uid, result))
            except Exception as e:
                self.logger.error(f"Exception receiving result for task {task_id}: {e}")
                error_result = {"status": False, "data": None, "error": str(e)}
                if task_id in self._futures and not self._futures[task_id].done():
                    self._futures[task_id].set_result(error_result)
                    await self.completed_queue.put((uid, error_result))
            finally:
                parent_conn.close()
                process.join()
                self._futures.pop(task_id, None)

