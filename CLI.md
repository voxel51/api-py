# Voxel51 Platform API Command-Line Interface Quickstart

Installing the Python Client Library automatically installs `voxel51`, a
command-line interface (CLI) for interacting with the Voxel51 Platform.

This document provides a brief overview of using the CLI.

<img src="https://drive.google.com/uc?id=1j0S8pLsopAqF1Ik3rf-CdyAIU4kA0sOP" alt="voxel51-logo.png" width="40%"/>


## Documentation

For full documentation of using the CLI, see the
[API Documentation](https://voxel51.com/docs/api).

For end-to-end examples of using the CLI to create and run jobs on the Voxel51
Platform, see the
[Analytics Documentation](https://voxel51.com/docs/analytics).


## Quickstart

To use the CLI, you must activate an API token. You can do so either by
setting the `VOXEL51_API_TOKEN` environment variable in your shell to point
to your API token file:

```shell
export VOXEL51_API_TOKEN=/path/to/your/api-token.json
```

Alternatively, you can permanently activate a token by executing the following
commands:

```shell
voxel51 auth activate /path/to/your/api-token.json
```

In the latter case, your token is copied to `~/.voxel51/` and will be
automatically used in all future sessions.

To show information about your active token, you can execute:

```shell
$ voxel51 auth show
API token
-------------  ------------------------------------
id             2649113c-e5ca-4008-a2f3-a24a9db806b9
creation date  2018-11-30 01:12:28 EST
base api url   https://api.voxel51.com
path           /path/to/your/api-token.json
```

A token can be deactivated via `voxel51 auth deactivate`.

After you have activated an API token, you have full access to the API.


## Usage

The following usage information was generated via `voxel51 --all-help`:

```

```


## Copyright

Copyright 2017-2019, Voxel51, Inc.<br>
[voxel51.com](https://voxel51.com)
