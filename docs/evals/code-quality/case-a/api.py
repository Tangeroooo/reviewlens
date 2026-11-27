from policy import inspect_job


def status_rows(jobs, retry_limit):
    rows = []
    for job in jobs:
        inspected = inspect_job(job, retry_limit)
        rows.append({"id": inspected[0], "retryable": inspected[6]})
    return rows
