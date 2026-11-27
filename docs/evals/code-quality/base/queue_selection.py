def retry_ids(jobs, retry_limit):
    return [job["id"] for job in jobs
            if job["state"] == "failed" and job["attempts"] < retry_limit]
