# Voxel51 API Python Client Library

This package defines a Python client library for interacting with the Voxel51
Vision Services Platform.


## Installation

To install the library, first clone it:

```shell
git clone https://github.com/voxel51/api-py
cd api-py
```

and then install the package:

```shell
pip install .
```


## Documentation

For full documentation of the Voxel51 Vision Services API, including usage of
this client library, see https://console.voxel51.com/docs/api.

To learn how to use this client library to create and run jobs that execute
each of the analytics exposed on the Voxel51 Vision Services Platform, see
https://console.voxel51.com/docs/analytics.


## Quickstart

### Sign-up and Authentication

To use the API, you must first create an account at
[https://console.voxel51.com](https://console.voxel51.com) and download an API
token.

> Keep your API token private; it is your access key to the API.

Each API request you make must be authenticated by your token. To activate your
token, set the `VOXEL51_API_TOKEN` environment variable in your shell to point
to your API token file:

```shell
export VOXEL51_API_TOKEN="/path/to/your/api-token.json"
```

Alternatively, you can permanently activate a token by executing the following
Python commands:

```py
from voxel51.auth import activate_token

activate_token("/path/to/your/api-token.json")
```

In the latter case, your token is copied to `~/.voxel51/` and will be
automatically used in all future sessions. A token can be deactivated via the
`voxel51.auth.deactivate_token()` method.

After you have activated an API token, you have full access to the API.

### Creating an API Session

To initialize an API session, issue the following Python commands:

```py
import json
from voxel51.api import API

api = API()

# Convenience function to view JSON outputs
def pprint(obj):
    print(json.dumps(obj, indent=4))
```

### Analytics

List available analytics:

```py
pprint(api.list_analytics())
```

Get documentation for the analytic with the given ID:

```py
# ID of the analytic
analytic_id = "XXXXXXXX"

pprint(api.get_analytic_doc(analytic_id))
```

### Data

Upload data to the cloud storage:

```py
# Local path to the data
upload_data_path = "/path/to/video.mp4"

pprint(api.upload_data(upload_data_path))
```

List uploaded data:

```py
pprint(api.list_data())
```

### Jobs

List the jobs you have created:

```py
pprint(api.list_jobs())
```

Create a job request to perform an analytic on a data, where `<analytic>` is
the name of the analytic to run, `<data-id>` is the ID of the data to process,
and any `<param#>` values are set as necessary to configre the analytic:

```py
from voxel51.jobs import JobRequest

job_request = JobRequest("<analytic>")
job_request.set_input("<input>", data_id="<data-id>")
job_request.set_parameter("<param1>", val1)
job_request.set_parameter("<param2>", val2)

print(job_request)
```

Upload a job request:

```py
pprint(api.upload_job_request(job_request, "<job-name>"))
```

Start a job:

```py
# ID of the job
job_id = "XXXXXXXX"

api.start_job(job_id)
```

Wait until a job is complete and then download its output:

```py
# Local path to which to download the output
job_output_path = "/path/to/output.zip"

api.wait_until_job_completes(job_id)
api.download_job_output(job_id, job_output_path)
```

Get the status of a job:

```py
pprint(api.get_job_status(job_id))
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
bash docs/generate_docs.bash
```

To view the documentation, open the `docs/build/html/index.html` file in
your browser.


## Copyright

Copyright 2017-2019, Voxel51, Inc.<br>
[voxel51.com](https://voxel51.com)
