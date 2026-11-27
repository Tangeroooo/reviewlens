def is_retryable(job, retry_limit):
    return job["state"] == "failed" and job["attempts"] < retry_limit
