from policy import is_retryable


def status_rows(jobs, retry_limit):
    return [{"id": job["id"], "retryable": is_retryable(job, retry_limit)} for job in jobs]
