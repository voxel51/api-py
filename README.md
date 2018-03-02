# Voxel51 API Python Client Library

This package defines a Python client library for accessing the Voxel51 Vision
Services API. The library is a thin wrapper that provides full access to all
of the API's capabilities from Python code.

See the `docs/` directory for full documentation of the library.


## Installation

First, clone the repository
```shell
git clone https://github.com/voxel51/api-python
cd api-python
```

Then install the package
```shell
pip install .
```

## Sign-up and Authentication

To use the API, you must first create an account at [https://api.voxel51.com](
https://api.voxel51.com). Next, download an API authentication token from
[https://api.voxel51.com/authenticate](https://api.voxel51.com/authenticate).
**Keep this token private**---it is your access key to the API.

Each API request you make must provide a valid API token. To activate a token,
you can set the `VOXEL51_API_TOKEN` environment variable to point to your
API token file:

```shell
# You can make this permanent by setting this variable
# in your ~/.bashrc or /etc/environment
export VOXEL51_API_TOKEN="/path/to/your/token.json"
```

Alternatively, you can activate a token using the client library:

```python
from voxel51.auth import activate_token

activate_token("/path/to/your/token.json")
```

With this approach, your token is copied to `~/.voxel51/api-token.json` for
safe-keeping, so you can safely delete/move the input token file.


## Hello World

After you have activated an API token, you have full access to the API.
The following code block demonstrates a simple use case:

```python
from voxel51.api import API
from voxel51.utils import print_response

# Start an API session
api = API()

# Get basic information about the API
res = api.get_home_page()

# Pretty-print the response
print_response(res)
```


## Additional Usage Examples

The following examples highlights some actions you can take using the API.
For a complete description of the supported methods, see the documentation
in the `docs/` directory.

* Get a list of all data you have uploaded
```python
res = api.get_data_list()
print_response(res)
```

* Upload new data to the cloud
```python
# Upload a single file
res = api.upload_data("video.mp4")
print_response(res)

# Upload multiple files and assign them to a dataset
res = api.upload_data(["video1.mp4", "video2.mp4"], group_name="videos")
print_response(res)
```

* Create a new job in the cloud
```python
# Pass the path to a job JSON
res = api.create_job("/path/to/your/job.json")
print_response(res)

# Pass a JSON dictionary
res = api.create_job({
    "name": "test-job",
    "data": [
        "#",
    ]
    "params": {
        "size": [1920, 1080],
    },
})
print_response(res)
```

* Run a job
```python
job_id = "XXXXXXXXXXXXXXXX"
res = api.start_job(job_id)
print_response(res)
```

* Check the status of a job
```python
res = api.get_job_status(job_id)
print_response(res)
```

* Download the output of a completed job
```python
output_path = "/path/to/output.json"
res = api.download_job_output(job_id, output_path)
print_response(res)
```

* Delete a job
```python
res = api.delete_job(job_id)
print_response(res)
```
