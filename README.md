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
you can either set the `VOXEL51_API_TOKEN` environment variable to point
to your API token file:

```shell
# You can make this permanent by setting this variable
# in your ~/.bashrc or /etc/environment
export VOXEL51_API_TOKEN="/path/to/your/token.json"
```

Alternatively, you can activate your token using the client library:

```python
from voxel51.auth import activate_token

activate_token("/path/to/your/token.json")
```

With this approach, your token is copied to a `.api-token.json` file in your
client library distribution, so you can safely delete/move the original token
file.


## Usage

After you have activated an API token, you have full access to the API.
The following code block demonstrates a simple use case:

```python
from voxel51.api import API
from pprint import pprint

# Create an API instance
api = API()

# Get basic information about the API
res = api.get_home_page()

# Pretty-print the HTTP response
pprint(res)
```

For a complete description of the supported API methods, see the documentation
in the `docs/` directory.
