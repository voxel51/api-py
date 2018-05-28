# Voxel51 API Python Client Library

This package defines a Python client library for accessing the Voxel51 Vision
Services API.


## Installation

To install the library, first clone it:

```shell
git clone https://github.com/voxel51/api-python
cd api-python
```

and then install the package:

```shell
pip install .
```


## Sign-up and Authentication

To use the API, you must first create an account at [https://console.voxel51.com](
https://console.voxel51.com) and download an API token.
**Keep this token private**. It is your access key to the API.

Each API request you make must be authenticated by your token. To activate your
token, set the `VOXEL51_API_TOKEN` environment variable in your shell to point
to your API token file:

```shell
export VOXEL51_API_TOKEN="/path/to/your/api-token.json"
```

Alternatively, you can permanently activate a token with:

```py
from voxel51.auth import activate_token

activate_token("/path/to/your/api-token.json")
```

In the latter case, your token is copied to `~/.voxel51/` and will be
automatically used in all future sessions. A token can be
deactivated via the `voxel51.auth.deactivate_token()` method.

After you have activated an API token, you have full access to the API.


## Example Usage

The following examples describe some actions you can take using the API.

To initialize an API session, issue the following commands:

```py
from voxel51.api import API

api = API()
```

### Analytics

List available analytics:

```py
analytics = api.list_analytics();
```

Get documentation for an analytic:

```py
doc = api.get_analytic_doc(analytic_id);
```

### Data

Upload data to the cloud:

```py
metadata = api.upload_data("/path/to/video.mp4")
```

List uploaded data:

```py
data = api.list_data()
```

### Jobs

Upload a job request:

```py
# Create a job request
job_request = JobRequest(analytic_id)
job_request.set_input("<input>", data_id=data_id)
job_request.set_parameter("<param1>", val1)
job_request.set_parameter("<param2>", val2)

# Upload the request
metadata = api.upload_job_request(job_request, "test-job")
```

List the jobs you have created:

```py
jobs = api.list_jobs()
```

Start a job:

```py
api.start_job(job_id)
```

Get the status of a job:

```py
status = api.get_job_status(job_id)
```

Download the output of a completed job:

```py
api.download_job_output(job_id, "/path/to/output.zip")
```


## Generating Documentation

This project uses
[Sphinx-Napoleon](https://pypi.python.org/pypi/sphinxcontrib-napoleon)
to generate its documentation from source. To install the necessary
dependencies to generate the documentation, run:

```shell
pip install --upgrade sphinx
pip install --upgrade sphinx_rtd_theme
pip install --upgrade sphinxcontrib-napoleon
pip install --upgrade m2r
```

To generate the documentation, run:

```shell
bash generate_docs.bash
```

To view the documentation, open the `build/html/index.html` file in
your browser.


## Copyright

Copyright 2018, Voxel51, LLC<br>
[voxel51.com](https://voxel51.com)

Brian Moore, brian@voxel51.com<br>
David Hodgson, david@voxel51.com
