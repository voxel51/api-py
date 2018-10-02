# Voxel51 API Python Client Library

This package defines a Python client library for accessing the Voxel51 Vision
Services API.


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


## Sign-up and Authentication

To use the API, you must first create an account at
[https://console.voxel51.com](https://console.voxel51.com) and download an API
token.

> Keep your API token private; it is your access key to the API

Each API request you make must be authenticated by your token. To activate your
token, set the `VOXEL51_API_TOKEN` environment variable in your shell to point
to your API token file:

```shell
export VOXEL51_API_TOKEN="/path/to/your/api-token.json"
```

Alternatively, you can permanently activate a token with below `Python` code. Run this code in `python REPL` :

```py
from voxel51.auth import activate_token

activate_token("/path/to/your/api-token.json")
```

In the latter case, your token is copied to `~/.voxel51/` and will be
automatically used in all future sessions. A token can be
deactivated via the `voxel51.auth.deactivate_token()` method.

After you have activated an API token, you have full access to the API.


## Example Usage

To initialize an API session, issue the following commands in Python:

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

Get documentation for an analytic. Asign certain `Analytic Id` as argument for the parameter `analytic_id`:

```py
pprint(api.get_analytic_doc(analytic_id))
```

### Data

Upload data to the cloud. Give path to the file along with filename to `upload_data_path`:

```py
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

Create a job request to run on certain data. Assign an `Analytic-Name`(Type of analytics) as `<analytic>`, particular `Data Id` as `dataId`, data type `video` or `image` to `<input>` and related parameters & values based on analytic type you choose to run. For more information on `input` and `parameters` refer to the method `get_analytic_doc()`.
:

```py
from voxel51.jobs import JobRequest

job_request = JobRequest("<analytic>")
job_request.set_input("<input>", data_id=data_id)
job_request.set_parameter("<param1>", val1)
job_request.set_parameter("<param2>", val2)

print(job_request)
```

Upload a job request:

```py
pprint(api.upload_job_request(job_request, "test-job"))
```

Start a job:

```py
api.start_job(job_id)
```

Wait until a job is complete and then download its output:

```py
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
bash generate_docs.bash
```

To view the documentation, open the `build/html/index.html` file in
your browser.


## Copyright

Copyright 2018, Voxel51, LLC<br>
[voxel51.com](https://voxel51.com)

Brian Moore, brian@voxel51.com<br>
David Hodgson, david@voxel51.com
