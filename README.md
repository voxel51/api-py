# Voxel51 API Python Client Library
>
> Copyright 2017-2018, Voxel51, LLC.
>
> Brian Moore, brian@voxel51.com
>
> David Hodgson, david@voxel51.com
>

This package defines a Python client library for accessing the Voxel51 Vision
Services API.

See the `docs/` directory for full documentation of the library.


## Installation

Clone the repository:
```shell
git clone https://github.com/voxel51/api-python
cd api-python
```

and then install the package:
```shell
pip install .
```

## Sign-up and Authentication

To use the API, you must first create an account at [https://api.voxel51.com](
https://api.voxel51.com). Next, download an API authentication token from
[https://api.voxel51.com/authenticate](https://api.voxel51.com/authenticate).
**Keep this token private**---it is your access key to the API.

Each API request you make must be authenticated by your token. To activate your
token, set the `VOXEL51_API_TOKEN` environment variable in your shell to point
to your API token file:

```shell
export VOXEL51_API_TOKEN="/path/to/your/token.json"
```

Alternatively, you can permanently activate a token with:

```python
from voxel51.auth import activate_token

activate_token("/path/to/your/token.json")
```

In the latter case, your token is copied to `~/.voxel51/api-token.json`
and will be automatically used in all future sessions. A token can be
deactivated via the `voxel51.auth.deactivate_token()` method.

After you have activated an API token, you have full access to the API.


## Hello World

The following code block demonstrates a simple use of the API:

```python
from voxel51.api import API

# Start an API session
api = API()

# List algorithms exposed by the API
algo_list = api.list_algorithms()
```


## Additional Usage Examples

The following examples highlights some actions you can take using the API.
For a complete description of the supported methods, see the documentation
in the `docs/` directory.

* Upload data to the Voxel51 cloud:
```python
data_metadata = api.upload_data("/path/to/video.mp4")
```

* List the data you have uploaded:
```python
data_list = api.list_data()
```

* Create a job request:
```python
job_request = JobRequest(algo_id)
job_request.set_input("<input>", data_id=data_id)
job_request.set_parameter("<param1>", val1)
job_request.set_parameter("<param2>", val2)
```

* Upload the job request:
```python
job_metadata = api.upload_job_request(job_request, "test-job")
```

* List the jobs you have created:
```python
job_list = api.list_jobs()
```

* Start a job:
```python
api.start_job(job_id)
```

* Get the status of a job:
```python
job_status = api.get_job_status(job_id)
```

* Download the output of a completed job:
```python
api.download_job_output(job_id, output_path)
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
```

To generate the documentation, run:

```shell
sphinx-apidoc -f -o docs/source .

cd docs
make html
```

To view the documentation, open the `build/html/index.html` file in
your browser.
