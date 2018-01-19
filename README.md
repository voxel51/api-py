# Voxel51, LLC API Python Client Library

This project provides a Python client library for accessing the Voxel51 API's
core functionality. Visit Voxel51's main repository for more information on
the video analytic services they can provide. The Python library can be
imported and a new class instance created. This instance stores the target
base url of the api as well any generated API authentication token.

## Sign-up and Authentication
To gain access to the API, please visit the [Voxel51 API website](http://api.voxel51.com)
to create a new account. After validating this account, get a
[valid authentication token](http://api.voxel51.com/authenticate). **Save this
API token in a secure location!** This token permits access to the rest of the
API functionality.

## Usage
More details on the client library's function can be found in the included
documentation. To use the module:

```python
from voxel51/api import API

api = API() #creates new API instance

res = api.get_home_page() # your first API call
pprint.pprint(res) # print the HTTP response
```

By default, the class constructor will check for the existence of an
environment variable, `VOXEL51_API_TOKEN`, which should contain the API
authentication token from above. If this environment variable is
undefined, the class constructor checks for a file `.api-token.txt`.
This file should just contain the saved authentication token.
An error will be thrown if neither of these two options are used.
