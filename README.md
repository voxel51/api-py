# Voxel51 Platform API Python Client Library

A Python client library for the Voxel51 Platform.

Available at
[https://github.com/voxel51/api-py](https://github.com/voxel51/api-py).

<img src="https://drive.google.com/uc?id=1j0S8pLsopAqF1Ik3rf-CdyAIU4kA0sOP" alt="voxel51-logo.png" width="40%"/>


## Installation

To install the library, first clone it:

```shell
git clone https://github.com/voxel51/api-py
```

and then run the install script:

```shell
cd api-py
bash install.bash
```


## Documentation

For full documentation of the Voxel51 Platform API, including usage of this
client library, see the [API Documentation](https://voxel51.com/docs/api).

To learn how to use this client library to create and run jobs that execute
each of the analytics exposed on the Voxel51 Platform, see
the [Analytics Documentation](https://voxel51.com/docs/analytics).

For more information about using the `voxel51` command-line interface that is
provided by this library see the [CLI Quickstart](CLI).

For more information about using the Python Client Library to operate an
application on the Voxel51 Platform, see the
[Applications Quickstart](APPLICATIONS).


## Quickstart

This section provides a brief guide to using the Platform API with your user
account.

### Sign-up and Authentication

To use the API, you must first create an account at https://console.voxel51.com
and download an API token.

> Keep your API token private; it is your access key to the API.

Each API request you make must be authenticated by your token. To activate your
token, set the `VOXEL51_API_TOKEN` environment variable in your shell to point
to your API token file:

```shell
export VOXEL51_API_TOKEN=/path/to/your/api-token.json
```

Alternatively, you can permanently activate a token by executing the following
commands:

```py
from voxel51.users.auth import activate_token

activate_token("/path/to/your/api-token.json")
```

In the latter case, your token is copied to `~/.voxel51/` and will be
automatically used in all future sessions. A token can be deactivated via the
`voxel51.users.auth.deactivate_token()` method.

After you have activated an API token, you have full access to the API.

### Creating an API Session

To initialize an API session, issue the following commands:

```py
from voxel51.users.api import API

api = API()
```

### Analytics

List available analytics:

```py
analytics = api.list_analytics()
```

Get documentation for the analytic with the given ID:

```py
# ID of the analytic
analytic_id = "XXXXXXXX"

doc = api.get_analytic_doc(analytic_id)
```

### Data

List uploaded data:

```py
data = api.list_data()
```

Upload data to the cloud storage:

```py
# Local path to the data
data_path = "/path/to/video.mp4"

api.upload_data(data_path)
```

### Jobs

List the jobs you have created:

```py
jobs = api.list_jobs()
```

Create a job request to perform an analytic on a data, where `<analytic>` is
the name of the analytic to run, `<data-id>` is the ID of the data to process,
and any `<parameter>` values are set as necessary to configre the analytic:

```py
from voxel51.users.jobs import JobRequest

job_request = JobRequest("<analytic>")
job_request.set_input("<input>", data_id="<data-id>")
job_request.set_parameter("<parameter>", val)

print(job_request)
```

Upload a job request:

```py
metadata = api.upload_job_request(job_request, "<job-name>")
job_id = metadata["id"]
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
# Local path to which to download the output
output_path = "/path/to/labels.json"

api.download_job_output(job_id, output_path=output_path)
```


## Improving Request Efficiency

A common pattern when interacting with the platform is to perform an operation
to a list of data or jobs. In such cases, you can dramatically increase the
efficiency of your code by using multiple threads. This library exposes a
thread pool that provides an easy way to distribute work among multiple
threads.

For example, the following code will run VehicleSense on a list of videos
using 8 threads to parallelize the upload of each video + job:

```py
from voxel51.users.api import API
from voxel51.users.jobs import JobRequest

api = API()

def run_vehicle_sense(path):
    data = api.upload_data(path)
    job_request = JobRequest("voxel51/vehicle-sense")
    job_request.set_input("video", data_id=data["id"])
    job_name = "vehicle-sense-%s" % data["name"]
    return api.upload_job_request(job_request, job_name, auto_start=True)

# Run VehicleSense on all videos using 16 threads
paths = ["1.mp4", "2.mp4", "3.mp4", ...]
jobs = api.thread_map(run_vehicle_sense, paths, max_workers=8)
```

Or, the following code will start all unstarted jobs on the platform using 16
threads to execute the requests:

```py
from voxel51.users.api import API
from voxel51.users.jobs import JobState
from voxel51.users.query import JobsQuery

api = API()

# Get all unarchived jobs
jobs_query = JobsQuery().add_all_fields().add_search("archived", False)
jobs = api.query_jobs(jobs_query)["jobs"]

def start_job_if_necessary(job):
    if job["state"] == JobState.READY:
        api.start_job(job["id"])

# Start all unstarted jobs
api.thread_map(start_job_if_necessary, jobs, max_workers=16)
```

See `voxel51.users.api.API.thread_map()` for details.


## Generating Documentation

This project uses
[Sphinx-Napoleon](https://pypi.python.org/pypi/sphinxcontrib-napoleon)
to generate its documentation from source.

To generate the documentation, run:

```shell
bash docs/generate_docs.bash
```

To view the documentation, open the `docs/build/html/index.html` file in
your browser.


## Copyright

Copyright 2017-2019, Voxel51, Inc.<br>
[voxel51.com](https://voxel51.com)
