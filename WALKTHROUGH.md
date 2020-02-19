# Client Library Walkthrough

This guide provides a simple step-by-step walkthrough of utilizing the full
power of the Voxel51 Platform using this handy Python Client Library and
Command Line Interface (CLI).

<img src="https://user-images.githubusercontent.com/3719547/74191434-8fe4f500-4c21-11ea-8d73-555edfce0854.png" alt="voxel51-logo.png" width="40%"/>


## Installation

Installing this library is very simple and has few dependencies.

### Dependencies

- Python 3 (or 2.7): https://www.python.org/downloads
- pip (installed with Python)

Verify your system has the expected packages:

```shell
python --version
pip --version
```

### Installation

*(optional)* Create and activate your virtual environment for this installation:

```shell
virtualenv venv
source venv/bin/activate
```

*(required)* Clone and install the package:

```shell
git clone https://github.com/voxel51/api-py.git
cd api-py
pip install -e .
```

Verify that the installation was successful by issuing a CLI command:

```shell
voxel51 --version
```

### Resources

This walkthrough assumes you have a video called `video1.mp4` in your current
working directory.

Feel free to use a video of your own, but, if desired, you can download a
sample video [here](https://drive.google.com/open?id=12wvTci0sWljhNQKT-Wld2Edzhg893yNh).


## Walkthrough

The client library allows a `Platform User` to perform actions, view data,
perform queries, run jobs, download their outputs, and more! All actions on the
platform are done as a user, meaning the requests must be authenticated.


### Step 1: Authenticating [(Docs)](https://voxel51.com/docs/api/?python#authentication)

First you must obtain an `API Token` from your Platform Console:

- Login to your Console Account at https://console.voxel51.com/login
- Navigate to your Account Tokens page at
https://console.voxel51.com/account/tokens
- Click `Create Token`
- Save the downloaded file as `api-token.json` in your working directory

Tokens can only be downloaded once, at creation. You may delete tokens and
create new tokens at any time.

In order to use the API, you must activate a token, which can be done in a
number of ways. For a full description of the available methods, see the
[Authentication Documentation](https://voxel51.com/docs/api/?python#authentication).

In this walkthrough, we will activate a token with the CLI:

```shell
voxel51 auth activate api-token.json
```

You can view details about your activate token with:

```shell
voxel51 auth show
```

### Step 2: Create an API instance [(Docs)](https://voxel51.com/docs/api/?python#authentication)

Before getting started with Python commands, we recommend using pretty-print
to make the outputs easier to digest:

```py
from pprint import pprint as print  # replaces the builtin `print`!
```

All actions are performed on an API instance which provides all of the methods
that communicate with the API directly.

```py
from voxel51.users.api import API

api = API()  # implicitly loads and uses your active token

print(api.list_analytics())  # see what analytics you have access to
print(api.list_data())  # see what data you have uploaded
print(api.list_jobs())  # see what jobs you have requested
```

The CLI uses the same underlying logic to perform the same actions:

```
voxel51 analytics list
voxel51 data list
voxel51 jobs list
```

Any listing, queries, and basic API operations are supported via the CLI. Type
`voxel51 --help` to see the full list of available CLI commands, and explore
the subcommands via `voxel51 <command> --help`.

### Step 3: Data [(Docs)](https://voxel51.com/docs/api/?python#data)

Upload your first `Data` to the Platform:

```py
data = api.upload_data("video1.mp4")
print(data)
data_id = data["id"]
```

The upload function blocks and returns with the response from the Platform of
the assigned data ID.  This ID is important to store and reference in later
requests.

Data IDs can always be found by listing or querying our data.

```py
# Show all data for our user
print(api.list_data())
```

At any time, you can query the Platform to return fine-grained information
about your data:

```py
from voxel51.users.query import DataQuery

# Review the fields we can use for searching, sorting and filtering
print(DataQuery.SUPPORTED_FIELDS)

# Build a Query
query = DataQuery()
query.add_field("id")  # return the IDs of the data
query.add_search("name", "video1.mp4")  # search for data with name "video1.mp4"
query.sort_by("upload_date", descending=True)  # most recent first
results = api.query_data(query)
print(results)

data_id = results["data"][0]["id"]  # get the ID of the first result
```

Here we are querying our data for the most recent data we uploaded by name.
There is plenty more we can do with queries, for data, jobs, and analytics!

Data can also be posted to the platform via signed URL. For more information,
[see the docs](https://voxel51.com/docs/api/?python#data-post-data-as-url).

#### TTL and expiration

All data on the Platform will expire at its `expiration date`. By default, this
is 3 days after upload. However, this date can be customized at upload time or
updated later. TTL (time to live) parameters accept ISO date strings or
`datetime` objects.

```py
from datetime import datetime, timedelta

# Upload data and specify its expiration date
date_to_expire = datetime.today() + timedelta(days=3)

data_id = api.upload_data("video1.mp4", ttl=date_to_expire)["id"]

query = DataQuery()
query.add_fields(["id", "name", "expiration_date"])
query.add_search("id", data_id)
data = api.query_data(query)["data"][0]
print(data)

# Update the expiration date of existing data
api.update_data_ttl(data_id, days=5)

data = api.query_data(query)["data"][0]
print(data)
```

Note that setting the expiration date of data to the past will result in the
data being deleted!

```py
api.update_data_ttl(data_id, days=-10)
query = DataQuery()
query.add_search("id", data_id)
print(api.query_data(query))  # no results!
```

#### Deleting Data

Manually deleting data is best done with the delete method:

```py
data_id = api.list_data()[0]["id"]
api.delete_data(data_id)
```

### Step 4: Analytics [(Docs)](https://voxel51.com/docs/api/?python#analytics)

`Analytics` are the processing modules on the Platform that define what kinds
of jobs you can run on your data. In order to run a job, we need to choose an
analytic:

```py
print(api.list_analytics())
```

Analytics have `names` and `versions`; unless otherwise specified, the latest
version of each analytic is used. However, older versions of analytics can also
be accessed:

```py
print(api.list_analytics(all_versions=True))
```

In this walkthrough, we'll use the `VehicleSense` analytic:

```py
ANALYTIC_NAME = "voxel51/vehicle-sense"
```

Like data, analytics are queryable:

```py
from voxel51.users.query import AnalyticsQuery

query = AnalyticsQuery()
query.add_field("id")
query.add_search("name", ANALYTIC_NAME)  # search for an analytic by name
results = api.query_analytics(query)
analytic_id = results["analytics"][0]["id"]
details = api.get_analytic_details(analytic_id)
print(details)
```

Analytics have `inputs`, `parameters, and `outputs`. Fetch the documentation
about an analytic so you know how to run jobs with it:

```py
doc = api.get_analytic_doc(analytic_id)
print(doc["inputs"])
print(doc["parameters"])
print(doc["outputs"])
```

Inputs specify the data that you want to process through the analytic.
Parameters allow you to customize things about how the analytic performs.
Outputs specify what the analytic will produce after processing its inputs.
For more details, [see the docs](https://voxel51.com/docs/api/?python#analytics-download-documentation).


### Step 5: Jobs [(Docs)](https://voxel51.com/docs/api/?python#jobs)

`Jobs` allow you to run analytics on your data. You run a job on the Platform
by creating a `Job Request`, which specifies:
 - the name (and optional version) of the analytic to run
 - the ID of the data(s) to process

You can create a job request as follows:

```py
from voxel51.users.jobs import JobRequest

data_id = api.upload_data("video1.mp4")["id"]
job_request = JobRequest(analytic=ANALYTIC_NAME)
job_request.set_input("video", data_id=data_id)
job_request.set_parameter("accel", 1.0)
job = api.upload_job_request(job_request, "your-job-name")
print(job)
```

This uploads the job request, but does not start it.

A job can be started two ways; either by automatically starting it when you
upload the job request:

```py
api.upload_job_request(job_request, "auto-start-me", auto_start=True)
```

or by starting a previously uploaded (but currently unstarted) job:

```py
job = api.upload_job_request(job_request, "your-job-name")
api.start_job(job["id"])
```

You can customize the compute type used to execute your jobs, depending on the
compute types supported by the analytic that you are running:

```py
from voxel51.users.jobs import JobComputeMode, JobRequest

job_request = JobRequest(ANALYTIC_NAME, compute_mode=JobComputeMode.GPU)
job_request.set_input("video", data_id=data_id)
api.upload_job_request(job_request=job_request, job_name="GPUjob")
```

View your jobs:

```py
print(api.list_jobs())
```

As usual, jobs are queryable:

```py
from voxel51.users.query import JobsQuery

query = JobsQuery()
query.add_fields(["name", "state"])
query.sort_by("state", descending=False)
results = api.query_jobs(query)
print(results)
```

Jobs enter different `states` throughout their lifetime. Job outputs can not be
downloaded until the job state is `COMPLETED`. For a complete description of
job states, [see the docs](https://voxel51.com/docs/api/?python#jobs).


### Step 6: Workflows

Suppose we have data we want to process with an analytic and download the
output all in one script. Let's see what that would look like:

```py
from voxel51.users.api import API
from voxel51.users.jobs import JobRequest

api = API()

# Upload data
data_id = api.upload_data("video1.mp4")["id"]

# Run job
job_request = JobRequest(ANALYTIC_NAME)
job_request.set_input("video", data_id=data_id)
job_id = api.upload_job_request(job_request, "jobName", auto_start=True)["id"]

# Download output of the completed job
api.wait_until_job_completes(job_id)  # this blocks until the job completes
api.download_job_output(job_id, "labels.json")
```

Now lets take this basic workflow and scale it up!

```py
import os

from voxel51.users.api import API
from voxel51.users.jobs import JobRequest

ANALYTIC_NAME = "voxel51/vehicle-sense"  # the analytic to run
INPUT_DATA_DIR = "/path/to/input/dir"  # directory of data to process
JOB_OUTPUT_DIR = "/path/to/output/dir"  # directory to write job outputs

api = API()


def upload_and_run(input_data):
    # Upload data
    print("Uploading %s" % input_data)
    data = api.upload_data(input_data)
    data_id = data["id"]
    print("Uploaded %s" % input_data)

    # Run job
    print("Starting job for %s" % input_data)
    job_request = JobRequest(ANALYTIC_NAME)
    job_request.set_input("video", data_id=data_id)
    job = api.upload_job_request(
        job_request, ANALYTIC_NAME + "-test", auto_start=True)
    print("Job started for %s" % input_data)
    return job["id"]


def wait_and_download(args):
    job_id, job_output_path = args

    # Wait until job completes
    print("Waiting for job %s" % job_id)
    api.wait_until_job_completes(job_id)

    # Download the output
    print("Job Complete! Downloading %s" % job_id)
    api.download_job_output(job_id, job_output_path)
    print("Downloaded " % job_id)


# Create list of data to process
datas = [os.path.join(INPUT_DATA_DIR, file)
         for file in os.listdir(INPUT_DATA_DIR)]

# Run jobs on data using a pool of threads
job_ids = list(api.thread_map(upload_and_run, datas, max_workers=4))

# Create list of (job ID, download path) tuples
job_outputs = [os.path.join(JOB_OUTPUT_DIR, j_id + ".json") for j_id in job_ids]
input_args = tuple(zip(job_ids, job_outputs))

# Download the outputs of the completed jobs using a pool of threads
api.thread_map(wait_and_download, input_args, max_workers=4)

print("Complete!")
```
