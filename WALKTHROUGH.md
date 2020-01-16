# Client Library Walkthrough

This guide will cover step-by-step how to utilize the full power of the Voxel51
Platform using this handy Python Client Library!

<img src="https://drive.google.com/uc?id=1j0S8pLsopAqF1Ik3rf-CdyAIU4kA0sOP" alt="voxel51-logo.png" width="40%"/>


## Installation

Installing this library is very simple and has few dependencies.

### Dependencies

 - Python 3 (or 2) https://www.python.org/downloads/
 - pip (which installs with Python)

If you are not sure what is available on your system, ask!

```sh
python --version
pip --version
```

### Install

You can install the API client library on your system python packages, or in a
virtual environment.

Optional: Create and activate your virtual environment.

```sh
virtualenv venv
source venv/bin/activate
```

Required: Clone and install the package

```sh
git clone https://github.com/voxel51/api-py.git
cd api-py
pip install -e .
```

That's it!


## Using the Client Library

The client library allows a Platform User to perform actions, view data, perform
queries, request jobs, download output and more!
All actions on the Platform must be done as a `User` meaning the requests must be
authenticated.
There are several ways we can `Authenticate` ourselves when using the client library.

### Step 1: Authenticating

[Docs](https://voxel51.com/docs/api/?python#authentication)

First you must obtain an API Token which is only available after logging into the
Console.
 - Login to the Console https://console.voxel51.com/login
 - Go to your Account Tokens page https://console.voxel51.com/account/tokens
 - Click `Create Token` and save the file.

Tokens are only able to be downloaded once.  You may delete and create more tokens
at any time.

Save your token to a safe location on your filesystem and copy the path.

```python
from voxel51.users.auth import activate_token

activate_token("/path/to/your/api-token.json")
```
This is one of many ways you can authenticate your client!
More details and alternatives are shown in the
[README](https://github.com/voxel51/api-py#sign-up-and-authentication).


### Step 2: Create API instance

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

### Step 3: Data

[Docs](https://voxel51.com/docs/api/?python#data)

Let's upload our first Data!

```python
data = api.upload_data("video1.mp4")
print(data)
data_id = data["id"]
```

The upload function blocks and returns with the response from the Platform of
the assigned Data ID.  This ID is important to store and reference in later
requests.

Finding the ID again is no problem, we can search for it!

```python
# Show all Data for our user
print(api.list_data())
```

This is one way to find Data, but let's search for it using Querys!

```python
from voxel51.users.query import DataQuery

# Build a Query
query = DataQuery()
# Review the fields we can use for searching, sorting and filtering
print(query.SUPPORTED_FIELDS)

query.add_field("id")
query.add_search("name", "video1.mp4")
query.sort_by("upload_date", descending=True)
results = api.query_data(query)
print(results)
data_id = results["data"][0]["id"]
```

Here we are querying our Data for the most recent data we uploaded by name.
There is plenty more we can do with queries, for Data, Jobs, and Analytics!

### TTL and expiration

All Data will expire, this expiration time can be adjusted at upload time or updated
any time after.
TTL (Time to live) parameters accept ISO date strings or `datetime` objects.

```python
from datetime import datetime, timedelta

date_to_expire = datetime.today() + timedelta(days=3)

data_id = api.upload_data("video1.mp4", ttl=date_to_expire)["id"]

# Or update TTL on data already uploaded!

api.update_data_ttl(data_id, days=5)

query = DataQuery()
query.add_fields(["id", "name", "expiration_date"])
query.sort_by("expiration_date", descending=True)
results = api.query_data(query)
print(results)
```

Updating a TTL to force expiration will result in the Data being deleted!

```python
api.update_data_ttl(data_id, days=-10)
query = DataQuery()
query.add_search("id", data_id)
api.query_data(query) # No Results!
```

Deleting data is better done with the delete method:

```python
data_id = api.list_data()[0]["id"]
api.delete_data(data_id)
```

### Step 5: Analytics

[Docs](https://voxel51.com/docs/api/?python#analytics)

Analytics are what Jobs run.  Before we can make a `JobRequest` we need Data
and an Analytic!

```python
api.list_analytics()
```

Analytics have versions, the latest is shown by default

```python
api.list_analytics(all_versions=True)
```

Analytics also are queryable

```python
from voxel51.users.query import AnalyticsQuery
query = AnalyticsQuery()
query.add_field("id")
query.add_search("name", "vehicle")
results = api.query_analytics(query)
analytic_id = results["analytics"][0]["id"]
details = api.get_analytic_details(analytic_id)
```

Analytics also have specifications for their inputs, parameters, and outputs.
Let's fetch them so we know how to build our JobRequest!

```python
doc = api.get_analytic_doc(analytic_id)
inputs = doc["inputs"]
parameters = doc["parameters"]
outputs = doc["outputs"]
```

Inputs specifies what kind of data we can supply to a job with this analytic.
Parameters give us ability to customize some things about how the analytic performs.
Outputs tell us what the Analytic will produce as the result of a Job.
For more details [Check out the docs!](https://voxel51.com/docs/api/?python#analytics-download-documentation)


### Step 4: Jobs

[Docs](https://voxel51.com/docs/api/?python#jobs)

Now it is time to make a JobRequest!
Things you need for a JobRequest:
 - analytic name (optional: version)
 - data_id (for Data that matches input type)

```python
from voxel51.users.jobs import JobRequest
data_id = api.upload_data("video1.mp4")["id"]
job_req = JobRequest(analytic="voxel51/vehicle-sense")
job_req.set_input("video", data_id=data_id)
job_req.set_parameter("accel", "1.0")
job = api.upload_job_request(job_req, "customJobName")
```

This uploads the job request, but does not start it.
A job can be started 2 ways:

```python
api.upload_job_request(job_req, "autoStartMe", auto_start=True)
```

Or

```python
job = api.upload_job_request(job_req, "customJobName")
api.start_job(job["id"])
```

Jobs can also be given a preference of compute to use for the Analytic (if it supports it!)

```python
from voxel51.users.jobs import JobComputeMode, JobRequest

job_req = JobRequest("voxel51/vehicle-sense", compute_mode=JobComputeMode.GPU)
job_req.set_input("video", data_id=data_id)
api.upload_job_request(job_request=job_req, job_name="GPUjob")
```

You can view your Jobs!

```python
api.list_jobs()
```

And Query!

```python
from voxel51.users.query import JobsQuery
job_query = JobsQuery()
job_query.add_fields(["name", "state"])
job_query.add_search("name", "GPUjob")
print(api.query_jobs(job_query))
```

```python
from voxel51.users.query import JobsQuery
job_query = JobsQuery()
job_query.add_fields(["name", "state"])
job_query.sort_by("state", descending=False)
print(api.query_jobs(job_query))
```

Jobs enter different `states` throughout their lifetime. Job outputs can not be
downloaded until the job state is `COMPLETED`.
[More about job states](https://voxel51.com/docs/api/?python#jobs)


### Step 6: Workflow

Suppose we have data we want to process with an Analytic and download the output
all in one script.  Let's see what that would look like:

```python
import voxel51.users.api as vapi
import voxel51.users.jobs as vjob

api = vapi.API()
data_id = api.upload_data("video1.mp4")["id"]
job_request = vjob.JobRequest("voxel51/vehicle-sense")
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

input_data_dir = "/path/to/dir/of/videos"
job_output_dir = "output/dir"

analytic_name = "voxel51/vehicle-sense"

api = API()

def upload_and_run(input_data):
    print("Uploading", input_data)
    data = api.upload_data(input_data)
    data_id = data["id"]
    print("Uploaded", input_data)

    print("Starting job for", input_data)
    job_request = JobRequest(analytic_name)
    job_request.set_input("video", data_id=data_id)
    job = api.upload_job_request(job_request, analytic_name + "-test",
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
