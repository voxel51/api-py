# Client Library Walkthrough

This guide will cover step-by-step how to utilize the full power of the Voxel51
Platform using this handy Python Client Library and Command Line Interface (CLI)

<img src="https://drive.google.com/uc?id=1j0S8pLsopAqF1Ik3rf-CdyAIU4kA0sOP" alt="voxel51-logo.png" width="40%"/>


## Installation

Installing this library is very simple and has few dependencies.

### Dependencies

 - Python 3 (or 2.7): https://www.python.org/downloads/
 - pip (which installs with Python)

Verify your system has the expected packages:

```sh
python --version
pip --version
```

### Installation

You can install the API client library on your system python packages, or in a
virtual environment.

(optional) Create and activate your virtual environment:

```sh
virtualenv venv
source venv/bin/activate
```

(required) Clone and install the package:

```sh
git clone https://github.com/voxel51/api-py.git
cd api-py
pip install -e .
```

Check your installation with the CLI:

```sh
voxel51 --version
```

### Optional Resources

Sample video [Download](https://drive.google.com/open?id=12wvTci0sWljhNQKT-Wld2Edzhg893yNh)  
Copy this file to a location local to where you will be following
this walkthrough.

## Using the Client Library and CLI

The client library allows a Platform User to perform actions, view data,
perform queries, request jobs, download output and more! All actions on the
Platform must be done as a user, meaning the requests must be authenticated.


### Step 1: Authenticate

[Docs](https://voxel51.com/docs/api/?python#authentication)

First you must obtain an API Token from your Platform Console:
 - Login at https://console.voxel51.com/login
 - Navigate to your Account Tokens page https://console.voxel51.com/account/tokens
 - Click `Create Token` and save the file

Tokens are only able to be downloaded once. You may delete and create tokens
at any time.

In order to use the API, you must activate a token, which can be done in a
number of ways. For a full description of the available methods, see the
[API Documentation](https://voxel51.com/docs/api/?python#authentication).

In this walkthrough, we will activate a token with the CLI.

```sh
voxel51 auth activate api-token.json
```

Review your activated token with:

```sh
voxel51 auth show
```

There are other ways to activate a token, here is an example using the library:

```python
from voxel51.users.auth import activate_token

activate_token("/path/to/your/api-token.json")
```

See more ways to authenticate with the [API Documentation](https://voxel51.com/docs/api/?python#authentication).

### Step 2: Create an API instance

[Docs](https://voxel51.com/docs/api/?python#authentication)

All actions are performed on an API instance which provides all of the methods
that communicate with the API directly.

```python
from voxel51.users.api import API

api = API() # uses default authentication

print(api.list_analytics()) # See what analytics you have access to
print(api.list_data()) # See what data you have uploaded
print(api.list_jobs()) # See what jobs you have requested
```

The CLI uses the same underlying logic to perform the same actions:

```sh
voxel51 analytics list
voxel51 data list
voxel51 jobs list
```

Any listing, queries, and basic API operations are supported via the CLI.

#### Optional note: Pretty printing

If you choose to follow along with the python client library, you may want to 
setup pretty printing:

```python
import pprint
pp = pprint.PrettyPrinter(indent=2).pprint
```

Call `pp()` on anything you wish to print, as there will be nested objects to 
unpack and investigate.

### Step 3: Data

[Docs](https://voxel51.com/docs/api/?python#data)

Uploading our first Data:

```python
data = api.upload_data("video1.mp4")
data_id = data["id"]
```

The upload function blocks and returns with the response from the Platform of
the assigned Data ID.  This ID is important to store and reference in later
requests.

Data ID's can always be found by listing or querying our data.

```python
# Show all Data for our user
api.list_data()
```

Now with queries:

```python
from voxel51.users.query import DataQuery

# Review the fields we can use for searching, sorting and filtering
print(DataQuery.SUPPORTED_FIELDS)

# Build a Query
query = DataQuery()
query.add_field("id") # Return only id's
query.add_search("name", "video1.mp4") # search for Data with name="video1.mp4"
query.sort_by("upload_date", descending=True) # sort for latest
results = api.query_data(query)
print(results)

data_id = results["data"][0]["id"] # Get the data ID of the first result
```

Here we are querying our Data for the most recent data we uploaded by name.
There is plenty more we can do with queries, for Data, Jobs, and Analytics!

#### TTL and expiration

All Data will expire; this expiration time can be adjusted at upload time or
updated at any later time. TTL (Time to live) parameters accept ISO date
strings or `datetime` objects.

```python
from datetime import datetime, timedelta

date_to_expire = datetime.today() + timedelta(days=3)

data_id = api.upload_data("video1.mp4", ttl=date_to_expire)["id"]

query = DataQuery()
query.add_fields(["id", "name", "expiration_date"])
query.add_search("id", data)
data = api.query_data(query)["data"][0]
print(data)

# Or update TTL on data already uploaded!

api.update_data_ttl(data_id, days=5)

data = api.query_data(query)["data"][0]
print(data)
```

Special note: Updating the expiration date to a date in the past will result in
the Data being deleted!

```python
api.update_data_ttl(data_id, days=-10)
query = DataQuery()
query.add_search("id", data_id)
api.query_data(query) # No Results!
```

#### Deleting Data

Deleting data is better done with the delete method:

```python
data_id = api.list_data()[0]["id"]
api.delete_data(data_id)
```

### Step 4: Analytics

[Docs](https://voxel51.com/docs/api/?python#analytics)

Analytics are what Jobs run. Before we can make a `JobRequest` we need Data and
an Analytic!

```python
api.list_analytics()
```

Analytics have versions; the latest version is shown by default. Older versions
can also be retrieved:

```python
api.list_analytics(all_versions=True)
```

Analytics also are queryable:

```python
from voxel51.users.query import AnalyticsQuery

ANALYTIC_NAME = "voxel51/vehicle-sense"

query = AnalyticsQuery()
query.add_field("id")
query.add_search("name", ANALYTIC_NAME) # Search for an analytic by name
results = api.query_analytics(query)
analytic_id = results["analytics"][0]["id"]
details = api.get_analytic_details(analytic_id)
```

Analytics also have specifications for their inputs, parameters, and outputs.
Let's fetch them so we know how to build our `JobRequest`.

```python
doc = api.get_analytic_doc(analytic_id)
inputs = doc["inputs"]
parameters = doc["parameters"]
outputs = doc["outputs"]
```

`Inputs` specifies what kind of data we can supply to a job with this analytic.
`Parameters` give us ability to customize some things about how the analytic performs. `Outputs` tell us what the Analytic will produce as the result of a
Job. For more details,
[check out the docs!](https://voxel51.com/docs/api/?python#analytics-download-documentation)


### Step 5: Jobs

[Docs](https://voxel51.com/docs/api/?python#jobs)

Things you need for a `JobRequest`:
 - analytic name (optional: version)
 - data_id (for Data that matches input type)

```python
from voxel51.users.jobs import JobRequest
data_id = api.upload_data("video1.mp4")["id"]
job_req = JobRequest(analytic=ANALYTIC_NAME)
job_req.set_input("video", data_id=data_id)
job_req.set_parameter("accel", 1.0)
job = api.upload_job_request(job_req, "customJobName")
```

This uploads the job request, but does not start it. A job can be started two
ways:

```python
api.upload_job_request(job_req, "autoStartMe", auto_start=True)
```

Or

```python
job = api.upload_job_request(job_req, "customJobName")
api.start_job(job["id"])
```

Jobs can also be given a preference of compute to use for the Analytic, if supported.

```python
from voxel51.users.jobs import JobComputeMode, JobRequest

job_req = JobRequest(ANALYTIC_NAME, compute_mode=JobComputeMode.GPU)
job_req.set_input("video", data_id=data_id)
api.upload_job_request(job_request=job_req, job_name="GPUjob")
```

View your jobs:

```python
api.list_jobs()
```

Or query:

```python
from voxel51.users.query import JobsQuery
query = JobsQuery()
query.add_fields(["name", "state"])
query.sort_by("state", descending=False)
results = api.query_jobs(query)
print(results)
```

Jobs enter different `states` throughout their lifetime. Job outputs can not be
downloaded until the job state is `COMPLETED`.
[More about job states](https://voxel51.com/docs/api/?python#jobs)


### Step 6: Workflow

Suppose we have data we want to process with an Analytic and download the
output all in one script. Let's see what that would look like:

```python
import voxel51.users.api as vapi
import voxel51.users.jobs as vjob

api = vapi.API()
data_id = api.upload_data("video1.mp4")["id"]
job_request = vjob.JobRequest(ANALYTIC_NAME)
job_request.set_input("video", data_id=data_id)
job_id = api.upload_job_request(job_request, "jobName", auto_start=True)["id"]
api.wait_until_job_completes(job_id) # This blocks until the job completes
api.download_job_output(job_id, "labels.json")
```

We can take this essential flow and scale it up!

```python
from voxel51.users.api import API
from voxel51.users.jobs import JobRequest
import os

input_data_dir = "input/dir"
job_output_dir = "output/dir"

ANALYTIC_NAME = "voxel51/vehicle-sense"

api = API()

def upload_and_run(input_data):
    print("Uploading", input_data)
    data = api.upload_data(input_data)
    data_id = data["id"]
    print("Uploaded", input_data)
    print("Starting job for", input_data)
    job_request = JobRequest(ANALYTIC_NAME)
    job_request.set_input("video", data_id=data_id)
    job = api.upload_job_request(job_request, ANALYTIC_NAME + "-test",
                                 auto_start=True)
    print("Job started for", input_data)
    return job["id"]


def wait_and_download(args):
    job_id = args[0]
    job_output_path = args[1]
    print("Waiting for job", job_id)
    api.wait_until_job_completes(job_id)
    print("Job Complete! Downloading", job_id)
    api.download_job_output(job_id, job_output_path)
    print("Downloaded", job_id)


# Create list of data
datas = [os.path.join(input_data_dir, file) for file in
         os.listdir(input_data_dir)]

# Spawn pool of threads on function to run on list
job_ids = list(api.thread_map(upload_and_run, datas, max_workers=4))

# Create tuples of job-id and download path pairs
job_outputs = [os.path.join(job_output_dir, j_id + ".json") for j_id in job_ids]
input_args = tuple(zip(job_ids, job_outputs))

# Spawn pool of threads to wait for job completion and download
api.thread_map(wait_and_download, input_args, max_workers=4)

print("Complete!")
```
