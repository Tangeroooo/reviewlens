from policy import is_retryable


def retry_ids(jobs, retry_limit):
    return [job["id"] for job in jobs if is_retryable(job, retry_limit)]
