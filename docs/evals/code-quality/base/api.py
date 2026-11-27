def status_rows(jobs, retry_limit):
    return [
        {"id": job["id"], "retryable": job["state"] == "failed" and job["attempts"] < retry_limit}
        for job in jobs
    ]
