# Voxel51 Platform API Applications Quickstart

The Voxel51 Platform provides an interface through which you can upload and
manage data for your application users and run jobs that process their data
through the video understanding algorithms deployed on the Voxel51 Platform.

In particular, the API exposes routes to manage your application, including
uploading custom analytics, creating and managing users, monitoring the status
of jobs, etc.

This document provides a brief overview of using the Python Client Library
to operate your application on the Voxel51 Platform.

<img src="https://drive.google.com/uc?id=1j0S8pLsopAqF1Ik3rf-CdyAIU4kA0sOP" alt="voxel51-logo.png" width="40%"/>


## Documentation

See the [Applications Documentation](https://voxel51.com/docs/applications) for
detailed documentation on using this client library to operate your application
on the Voxel51 Platform.


## Quickstart

### Sign-up and Authentication

To use the API with your application, you must first login to your application
admin account at https://console.voxel51.com/apps/your-app-name and create an
API token for your application.

> Keep your application API token private; it is your access key to the API.

Each API request you make must be authenticated by your application token. To
activate your application token, set the `VOXEL51_APP_TOKEN` environment
variable in your shell to point to your API token file:

```shell
export VOXEL51_APP_TOKEN=/path/to/your/app-token.json
```

Alternatively, you can permanently activate an application token by executing
the following commands:

```py
from voxel51.apps.auth import activate_application_token

activate_application_token("/path/to/your/app-token.json")
```

In the latter case, your token is copied to `~/.voxel51/` and will be
automatically used in all future sessions. An application token can be
deactivated via the `voxel51.apps.auth.deactivate_application_token()` method.

After you have activated an application API token, you have full access to the
API.

### Creating an Application API Session

To initialize an API session for your application, issue the following
commands:

```py
from voxel51.apps.api import ApplicationAPI

api = ApplicationAPI()
```

### User Management

The application API provides methods to manage the users of your application.

For example, you can list the current users of your application:

```py
usernames = api.list_users()
```

and create a new user:

```py
api.create_user("<username>")
```

### Performing User Actions

To perform actions for a user of your application, you must first activate the
user:

```py
# Activate an application user
api.with_user("<username>")
```

With a user activated, all subsequent API requests will be applied to that
user. To deactivate the user, use the `ApplicationAPI.exit_user()` method.

For example, you can upload data for the user:

```py
# Local path to the data
data_path = "/path/to/video.mp4"

api.upload_data(data_path)
```

And run a job on the user's data:

```py
from voxel51.users.jobs import JobRequest

job_request = JobRequest("<analytic>")
job_request.set_input("<input>", data_id="<data-id>")
job_request.set_parameter("<parameter>", val)
api.upload_job_request(job_request, "<job-name>", auto_start=True)
```


## Copyright

Copyright 2017-2019, Voxel51, Inc.<br>
[voxel51.com](https://voxel51.com)
