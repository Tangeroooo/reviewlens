def inspect_job(job, retry_limit):
    return [
        job["id"],
        job["state"],
        job["attempts"],
        retry_limit,
        job["state"] == "failed",
        job["attempts"] < retry_limit,
        job["state"] == "failed" and job["attempts"] < retry_limit,
    ]
