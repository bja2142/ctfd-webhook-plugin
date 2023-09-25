import concurrent.futures

class WebhookExecutor:

    def cleanup(self):
        self.executor.shutdown(wait=False, cancel_futures=False)

    def __init__(self, num_workers=2):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_workers)
        self.job_results = []

    def submit_job(self, fn, arguments):
        future_result = self.executor.submit(fn, arguments)
        self.job_results.append(future_result)
        return future_result
