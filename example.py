import asyncio
import datetime
import os
import time
from asyncermp import AsyncerMp  # Your multiprocessing wrapper
import psutil

class MockHeavyTask:
    async def run(self, task_data):
        n = task_data['n']
        result = 0
        for i in range(n):
            result += i * i  # CPU-heavy calculation
        await asyncio.sleep(0.01)  # Minimal async yield
        return {"uid": task_data['uid'], "result": result}


async def run_no_mp(queue):
    st = time.time()
    mock = MockHeavyTask()
    results = []
    print(f"[No MP] Blocked due to cpu load")
    for i in range(8):
        data = {"uid": f"nomp-{i}", "n": 10_000_0000, "data": i}  # Reduced n for testing
        result = await mock.run(data)
        results.append(result)
    print(f"[No MP] Finished in {time.time() - st:.2f} seconds")
    await queue.put({'nomp_is_done':True,'results':results})  # Signal completion via queue




async def run_with_mp(wrapper, queue):
    st = time.time()
    mock = MockHeavyTask()
    tasks = []
    for i in range(8):
        data = {"uid": f"mp-{i}", "n": 10_000_0000, "data": i}  # Reduced n for testing
        fut = await wrapper.submit(data, mock.run, uid=data["uid"])
        tasks.append((data["uid"], fut))
    results = []
    for uid, fut in tasks:
        result = await fut
        results.append(result)
    print(f"[MP] Finished in {time.time() - st:.2f} seconds")
    await queue.put({'mp_is_done':True,'results':results})  # Signal completion via queue



async def main(max_processes=8):
    wrapper = AsyncerMp(max_processes=max_processes)
    asyncio.create_task(wrapper._runner())

    # Create a queue for signaling
    queue = asyncio.Queue()

    # Run multiprocessing version
    asyncio.create_task(run_with_mp(wrapper, queue))

    # Get the current process for CPU usage
    process = psutil.Process(os.getpid())

    # Non-blocking main loop
    i = 0
    while True:
        i+=1
        try:
            # Check queue non-blockingly
            result = await asyncio.wait_for(queue.get(), timeout=0.001)

            if result.get('mp_is_done',None):
                print("Detected MP completion, starting run_no_mp")
                asyncio.create_task(run_no_mp(queue))


            if result.get('nomp_is_done', None):

              break

        except asyncio.TimeoutError:
            # Queue is empty, continue looping
            pass

        # Get CPU usage for the current process
        cpu_load = process.cpu_percent(interval=None)  # Non-blocking, but may need interval
        print(f'LOOP:{i}, PROCESS_LOAD%:{cpu_load}, dt:{datetime.datetime.now()}')

        await asyncio.sleep(1)




if __name__ == '__main__':
    asyncio.run(main(max_processes=8))