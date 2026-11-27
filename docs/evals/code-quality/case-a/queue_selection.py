from policy import inspect_job


def retry_ids(jobs, retry_limit):
    selected = []
    for job in jobs:
        inspected = inspect_job(job, retry_limit)
        if inspected[6]:
            selected.append(inspected[0])
    return selected
