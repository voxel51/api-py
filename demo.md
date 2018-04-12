# Voxel51 Vision Services API Demo
>
> Copyright 2017-2018, Voxel51, LLC.
>
> Brian Moore, brian@voxel51.com
>
> Last used: April 11, 2018
>
> API revision: `92ade5dc8d2f610419cee7acb92c1375156ac962`
>
> Python client library revision: `8410438a5e15d63083d68803d16478f0db9ed021`
>

The following sections demonstrate end-to-end uses of the Vision Services API
via the Python client library and via simple `curl` requests.


## Python Client Library

### Setup

Activate an API token
```shell
export VOXEL51_API_TOKEN="/Users/Brian/Desktop/api-token.json"
```

Launch python and import packages
```python
import json

from voxel51.api import API
from voxel51.jobs import JobRequest

def pprint(obj):
    print json.dumps(obj, indent=4)
```

Create an API instance
```python
api = API()
```

### Algorithms

List algorithms
```python
pprint(api.list_algorithms())
```

Get algorithm documentation
```python
algo_id = "f6275458-b39b-4933-9dca-58565500eadb"

pprint(api.get_algorithm_doc(algo_id))
```

### Data

List data
```python
pprint(api.list_data())
```

Upload data
```python
data_upload_path = "/Users/Brian/Desktop/water.mp4"

pprint(api.upload_data(data_upload_path))
```

Get data details
```python
data_id = "a29c5943-19b4-4831-859f-c557ee87656e"

pprint(api.get_data_details(data_id))
```

Download data
```python
data_download_path = "/Users/Brian/Desktop/test.mp4"

api.download_data(data_id, data_download_path)
```

Delete data
```python
api.delete_data(data_id)
```

### Jobs

List jobs
```python
pprint(api.list_jobs())
```

Create job request
```python
job_request = JobRequest(algo_id)
job_request.set_input("raw-video", data_id=data_id)
job_request.set_parameter("scale", 0.5)
job_request.set_parameter("fps", 5)

print job_request
```

Upload job request
```python
job_name = "test-job"

pprint(api.upload_job_request(job_request, job_name))
```

Get job details
```python
job_id = "41549249-2291-4b76-9230-6127064464a8"

print api.get_job_details(job_id)
```

Get job request
```python
print api.get_job_request(job_id)
```

Start job
```python
api.start_job(job_id)
```

Get job status
```python
pprint(api.get_job_status(job_id))
```

Download output of a completed job
```python
job_output_path = "/Users/Brian/Desktop/output.zip"

api.download_job_output(job_id, job_output_path)
```


## Curl Requests

### Setup

Activate an API token

```shell
# Private key from API token
export PRIVATE_KEY=XXXXXXXXXXXXXXXXXXXX
```

### Algorithms

List algorithms
```shell
curl -k "https://api.voxel51.com/v1/algo/list" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" | python -m json.tool
```

Get algorithm documentation
```shell
ALGO_ID="f6275458-b39b-4933-9dca-58565500eadb"

curl -k "https://api.voxel51.com/v1/algo/${ALGO_ID}" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" | python -m json.tool
```

**[INTERNAL]** Upload algorithm
```shell
curl -k "https://api.voxel51.com/v1/algo" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" \
    -F "file=@/Users/Brian/Desktop/video-formatter.json" | python -m json.tool
```

### Data

List data
```shell
curl -k "https://api.voxel51.com/v1/data/list" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" | python -m json.tool
```

Upload data
```shell
DATA_UPLOAD_PATH="/Users/Brian/Desktop/water.mp4"

curl -k "https://api.voxel51.com/v1/data" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" -F "file=@${DATA_UPLOAD_PATH}" \
    | python -m json.tool
```

Get data details
```shell
DATA_ID="a29c5943-19b4-4831-859f-c557ee87656e"

curl -k "https://api.voxel51.com/v1/data/${DATA_ID}" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" | python -m json.tool
```

Download data
```shell
DATA_OUTPUT_PATH="/Users/Brian/Desktop/test.mp4"

curl -k "https://api.voxel51.com/v1/data/${DATA_ID}/download" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" > "${DATA_OUTPUT_PATH}"
```

Delete data
```shell
curl -k "https://api.voxel51.com/v1/data/${DATA_ID}" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" -X DELETE | python -m json.tool
```

### Jobs

List jobs
```shell
curl -k "https://api.voxel51.com/v1/job/list" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" | python -m json.tool
```

Create job request
```shell
JOB_REQUEST_PATH="/Users/Brian/Desktop/job.json"

echo '
{
    "algorithm": "f6275458-b39b-4933-9dca-58565500eadb",
    "inputs": {
        "raw-video": {
            "data-id": "a29c5943-19b4-4831-859f-c557ee87656e"
        }
    },
    "parameters": {
        "scale": 0.5,
        "fps": 5
    }
}
' > "${JOB_REQUEST_PATH}"
```

Upload job request
```shell
JOB_NAME="test-job"

curl -k "https://api.voxel51.com/v1/job" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" -F "file=@${JOB_REQUEST_PATH}" \
    -F "job_name=${JOB_NAME}" -F "auto_start=false" | python -m json.tool
```

Get job details
```shell
JOB_ID="41549249-2291-4b76-9230-6127064464a8"

curl -k "https://api.voxel51.com/v1/job/${JOB_ID}" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" | python -m json.tool
```

Get job request
```shell
curl -k "https://api.voxel51.com/v1/job/${JOB_ID}/request" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" | python -m json.tool
```

Start job
```shell
curl -k "https://api.voxel51.com/v1/job/${JOB_ID}/start" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" -X PUT | python -m json.tool
```

Get job status
```shell
curl -k "https://api.voxel51.com/v1/job/${JOB_ID}/status" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" | python -m json.tool
```

Download output of a completed job
```
JOB_OUTPUT_PATH="/Users/Brian/Desktop/output.zip"

curl -k "https://api.voxel51.com/v1/job/${JOB_ID}/output" \
    -H "Authorization: Bearer ${PRIVATE_KEY}" > "${JOB_OUTPUT_PATH}"
```