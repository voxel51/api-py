# Examples

Example uses of the Python Client Library to run analytics in the cloud on the
Voxel51 Vision Services Platform.

All of the following examples assume that you have activated a valid API token
either by setting the `VOXEL51_API_TOKEN` environment variable in your shell or
permanently activating it via `voxel51.auth.activate_token()`.


## vehicle-detector

The following code will upload the `road.mp4` video from your current working
directory to the Voxel51 Vision Services Platform, run the `vehicle-detector`
analytic on it, and download the output to `output.zip` when the job completes.

You can download this [dashcam video clip](
https://drive.google.com/file/d/1gg6zJpp8j_ZiUaAy3Sdl3VvD5zUq9LX7) to use as
an example input if you would like.

```py
from voxel51.api import API
from voxel51.jobs import JobRequest

# Create an API session
api = API()

# Upload data
data = api.upload_data("road.mp4")
data_id = data["data_id"]

# Upload job request
job_request = JobRequest("vehicle-detector")
job_request.set_input("video", data_id=data_id)
job = api.upload_job_request(job_request, "detect-vehicles")
job_id = job["job_id"]

# Run job
api.start_job(job_id)

# Wait until job completes, and then download the output
api.wait_until_job_completes(job_id)
api.download_job_output(job_id, "output.zip")
```

Unzip the downloaded `output.zip` file to inspect the result of the job.
