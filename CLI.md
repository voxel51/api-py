# Command-Line Interface Quickstart

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

To use the CLI, you must activate an API token. This can be done in a variety
of ways; for a full description, see the
[Authentication Documentation](https://voxel51.com/docs/api/#authentication).

A simple approach is to set the `VOXEL51_API_TOKEN` environment variable in
your shell to point to your API token file:

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
-------------  ---------------------------------------------------
token id       2649113c-e5ca-4008-a2f3-a24a9db806b9
creation date  2018-11-30 01:12:28 EST
private key    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyYW5kIj ...
base api url   https://api.voxel51.com
path           /path/to/your/api-token.json
```

A token can be deactivated via `voxel51 auth deactivate`.

After you have activated an API token, you have full access to the API.


## Tab completion

To enable tab completion in `bash`, add the following line to your `~/.bashrc`:

```shell
eval "$(register-python-argcomplete voxel51)"
```

To enable tab completion in `zsh`, add these lines to your `~/.zshrc`:

```shell
autoload bashcompinit
bashcompinit
eval "$(register-python-argcomplete voxel51)"
```

To enable tab completion in `tcsh`, add these lines to your `~/.tcshrc`:

```shell
eval `register-python-argcomplete --shell tcsh voxel51`
```


## Usage

The following usage information was generated via `voxel51 --all-help`:

```
*******************************************************************************
usage: voxel51 [-h] [-v] [--all-help] {auth,data,jobs,analytics,status} ...

Voxel51 Platform command-line interface.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show version info
  --all-help            show help recurisvely and exit

available commands:
  {auth,data,jobs,analytics,status}
    auth                Tools for configuring API tokens.
    data                Tools for working with data.
    jobs                Tools for working with jobs.
    analytics           Tools for working with analytics.
    status              Tools for checking the status of the platform.


*******************************************************************************
usage: voxel51 auth [-h] [--all-help] {show,activate,deactivate} ...

Tools for configuring API tokens.

optional arguments:
  -h, --help            show this help message and exit
  --all-help            show help recurisvely and exit

available commands:
  {show,activate,deactivate}
    show                Show info about the active API token.
    activate            Activate an API token.
    deactivate          Deletes the active API token, if any.


*******************************************************************************
usage: voxel51 auth show [-h]

Show info about the active API token.

    Examples:
        # Print info about active token
        voxel51 auth show

optional arguments:
  -h, --help  show this help message and exit


*******************************************************************************
usage: voxel51 auth activate [-h] token

Activate an API token.

    Examples:
        # Activate API token
        voxel51 auth activate '/path/to/token.json'

positional arguments:
  token       path to API token to activate

optional arguments:
  -h, --help  show this help message and exit


*******************************************************************************
usage: voxel51 auth deactivate [-h]

Deletes the active API token, if any.

optional arguments:
  -h, --help  show this help message and exit


*******************************************************************************
usage: voxel51 data [-h] [--all-help]
                    {list,info,upload,post-url,download,ttl,delete} ...

Tools for working with data.

optional arguments:
  -h, --help            show this help message and exit
  --all-help            show help recurisvely and exit

available commands:
  {list,info,upload,post-url,download,ttl,delete}
    list                List data uploaded to the platform.
    info                Get information about data uploaded to the platform.
    upload              Upload data to the platform.
    post-url            Posts data via URL to the platform.
    download            Download data from the platform.
    ttl                 Update TTL of data on the platform.
    delete              Delete data from the platform.


*******************************************************************************
usage: voxel51 data list [-h] [-l LIMIT] [-s SEARCH] [--sort-by FIELD]
                         [--ascending] [-a] [-c]

List data uploaded to the platform.

    Examples:
        # List data according to the given query
        voxel51 data list \
            [--limit <limit>] \
            [--search [<field>:]<str>[,...]] \
            [--sort-by <field>] \
            [--ascending] \
            [--all-fields] \
            [--count]

        # List the last 10 data uploaded to the platform
        voxel51 data list --limit 10 --sort-by upload_date

        # List data whose filenames contain "test", in ascending order of size
        voxel51 data list --search name:test --sort-by size --ascending

    Search syntax:
        The generic search syntax is:

            --search [<field>:]<str>[,...]

        where:
            <field>    an optional field name on which to search
            <str>      the search string

        The supported fields for data searches are `id`, `name`, and `type`.

        If `<field>:` is omitted, the search will match any records for which
        any field contains the given search string.

        Multiple searches can be specified as a comma-separated list. Records
        must match all searches in order to appear in the search results.

        You can include special characters `,` and `:` in search strings by
        escaping them with `\`.

        Fields are case insensitive, and underscores can be used in-place of
        spaces.

optional arguments:
  -h, --help            show this help message and exit
  -l LIMIT, --limit LIMIT
                        limit the number of data listed
  -s SEARCH, --search SEARCH
                        search to limit results when listing data
  --sort-by FIELD       field to sort by when listing data
  --ascending           whether to sort in ascending order
  -a, --all-fields      whether to print all available fields
  -c, --count           whether to show the number of data in the list


*******************************************************************************
usage: voxel51 data info [-h] [-a] ID [ID ...]

Get information about data uploaded to the platform.

    Examples:
        # Get data info
        voxel51 data info <id> [...]

        # Get all available fields for data
        voxel51 data info --all-fields <id> [...]

positional arguments:
  ID                the data ID(s) of interest

optional arguments:
  -h, --help        show this help message and exit
  -a, --all-fields  whether to print all available fields


*******************************************************************************
usage: voxel51 data upload [-h] [--print-id] PATH [PATH ...]

Upload data to the platform.

    Examples:
        # Upload data
        voxel51 data upload '/path/to/video.mp4' [...]

positional arguments:
  PATH        the file(s) to upload

optional arguments:
  -h, --help  show this help message and exit
  --print-id  whether to print only the ID(s) of the uploaded data


*******************************************************************************
usage: voxel51 data post-url [-h] -u URL -f NAME -m TYPE -s SIZE -e DATE
                             [--print-id]

Posts data via URL to the platform.

    Examples:
        # Post data via URL
        voxel51 data post-url \
            --url <url> \
            --filename <filename> \
            --mime-type <mime-type> \
            --size <size-bytes> \
            --expiration-date <expiration-date>

optional arguments:
  -h, --help            show this help message and exit
  --print-id            whether to print only the ID of the uploaded data

required arguments:
  -u URL, --url URL     the data URL
  -f NAME, --filename NAME
                        the data filename
  -m TYPE, --mime-type TYPE
                        the data MIME type
  -s SIZE, --size SIZE  the data size, in bytes
  -e DATE, --expiration-date DATE
                        the data expiration date


*******************************************************************************
usage: voxel51 data download [-h] [-p PATH] [-u] ID

Download data from the platform.

    Examples:
        # Download data to default location
        voxel51 data download <id>

        # Download data to specific location
        voxel51 data download <id> --path '/path/for/video.mp4'

        # Generate signed URL to download data
        voxel51 data download <id> --url

positional arguments:
  ID                    data to download

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  path to download data
  -u, --url             generate signed URL to download data


*******************************************************************************
usage: voxel51 data ttl [-h] [--days DAYS] [--date DATE] [-a] [-f] [--dry-run]
                        [ID [ID ...]]

Update TTL of data on the platform.

    Examples:
        # Extend TTL of data by specified number of days
        voxel51 data ttl --days <days> <id> [...]

        # Set expiration date of data to given date
        voxel51 data ttl --date <date> <id> [...]

positional arguments:
  ID           the data ID(s) to update

optional arguments:
  -h, --help   show this help message and exit
  --days DAYS  the number of days by which to extend the TTL of the data
  --date DATE  new expiration date for the data
  -a, --all    whether to update all data
  -f, --force  whether to force update all without confirmation
  --dry-run    whether to print data IDs that would be updated rather than actually performing the action


*******************************************************************************
usage: voxel51 data delete [-h] [-a] [-f] [--dry-run] [ID [ID ...]]

Delete data from the platform.

    Examples:
        # Delete data
        voxel51 data delete <id> [...]

        # Delete all data
        voxel51 data delete --all

positional arguments:
  ID           the data ID(s) to delete

optional arguments:
  -h, --help   show this help message and exit
  -a, --all    whether to delete all data
  -f, --force  whether to force delete all without confirmation
  --dry-run    whether to print data IDs that would be deleted rather than actually performing the action


*******************************************************************************
usage: voxel51 jobs [-h] [--all-help]
                    {list,info,upload,start,archive,unarchive,ttl,request,status,log,download,kill,delete}
                    ...

Tools for working with jobs.

optional arguments:
  -h, --help            show this help message and exit
  --all-help            show help recurisvely and exit

available commands:
  {list,info,upload,start,archive,unarchive,ttl,request,status,log,download,kill,delete}
    list                List jobs on the platform.
    info                Get information about jobs on the platform.
    upload              Upload job requests to the platform.
    start               Start jobs on the platform.
    archive             Archive jobs on the platform.
    unarchive           Unarchive jobs on the platform.
    ttl                 Update TTL of jobs on the platform.
    request             Download job requests.
    status              Download job statuses.
    log                 Download job logfiles.
    download            Download job outputs.
    kill                Kill jobs on the platform.
    delete              Delete jobs on the platform.


*******************************************************************************
usage: voxel51 jobs list [-h] [-l LIMIT] [-s SEARCH] [--sort-by FIELD]
                         [--ascending] [-a] [-c] [--ready] [--queued]
                         [--scheduled] [--running] [--complete] [--failed]
                         [--include-archived] [--exclude-archived]
                         [--archived-only] [--include-expired]
                         [--exclude-expired] [--expired-only]

List jobs on the platform.

    Notes:
        Unless overridden, only unarchived jobs are listed.

    Examples:
        # List jobs according to the given query
        voxel51 jobs list \
            [--limit <limit>] \
            [--search [<field>:]<str>[,...]] \
            [--sort-by <field>] \
            [--ascending] \
            [--all-fields] \
            [--count]

        # Flags for jobs in a particular state
        voxel51 jobs list --ready
        voxel51 jobs list --queued
        voxel51 jobs list --scheduled
        voxel51 jobs list --running
        voxel51 jobs list --complete
        voxel51 jobs list --failed

        # Flags for jobs with a particular archival state
        # These flags are ignored when a search containing `archived` is found
        voxel51 jobs list --include-archived
        voxel51 jobs list --exclude-archived    (default behavior)
        voxel51 jobs list --archived-only

        # Flags for jobs with a particular expiration status
        voxel51 jobs list --include-expired     (default behavior)
        voxel51 jobs list --exclude-expired
        voxel51 jobs list --expired-only

        # List the last 10 jobs completed on the platform
        voxel51 jobs list --complete --limit 10 --sort-by upload_date

        # List jobs whose filenames contain "test", in alphabetical order
        voxel51 jobs list --search name:test --sort-by name --ascending

    Search syntax:
        The generic search syntax is:

            --search [<field>:]<str>[,...]

        where:
            <field>    an optional field name on which to search
            <str>      the search string

        The supported fields for jobs searches are `id`, `name`, `state`, and
        `archived`.

        If `<field>:` is omitted, the search will match any records for which
        any field contains the given search string.

        Multiple searches can be specified as a comma-separated list. Records
        must match all searches in order to appear in the search results.

        You can include special characters `,` and `:` in search strings by
        escaping them with `\`.

        Fields are case insensitive, and underscores can be used in-place of
        spaces.

optional arguments:
  -h, --help            show this help message and exit
  -l LIMIT, --limit LIMIT
                        limit the number of jobs listed
  -s SEARCH, --search SEARCH
                        search to limit results when listing jobs
  --sort-by FIELD       field to sort by when listing jobs
  --ascending           whether to sort in ascending order
  -a, --all-fields      whether to print all available fields
  -c, --count           whether to show the number of jobs in the list

state arguments:
  --ready               jobs in READY state
  --queued              jobs in QUEUED state
  --scheduled           jobs in SCHEDULED state
  --running             jobs in RUNNING state
  --complete            jobs in COMPLETE state
  --failed              jobs in FAILED state

archival arguments:
  --include-archived    include archived jobs
  --exclude-archived    exclude archived jobs (default behavior)
  --archived-only       only archived jobs

expiration arguments:
  --include-expired     include expired jobs (default behavior)
  --exclude-expired     exclude expired jobs
  --expired-only        only expired jobs


*******************************************************************************
usage: voxel51 jobs info [-h] [-a] ID [ID ...]

Get information about jobs on the platform.

    Examples:
        # Get job(s) info
        voxel51 jobs info <id> [...]

        # Get all available fields for jobs
        voxel51 jobs info --all-fields <id> [...]

positional arguments:
  ID                the job ID(s) of interest

optional arguments:
  -h, --help        show this help message and exit
  -a, --all-fields  whether to print all available fields


*******************************************************************************
usage: voxel51 jobs upload [-h] -r PATH -n NAME [--auto-start] [--print-id]

Upload job requests to the platform.

    Examples:
        # Upload job request
        voxel51 jobs upload --request '/path/to/request.json' \
            --name <job-name> [--auto-start]

optional arguments:
  -h, --help            show this help message and exit
  --auto-start          whether to automatically start job
  --print-id            whether to print only the ID(s) of the job

required arguments:
  -r PATH, --request PATH
                        path to job request to upload
  -n NAME, --name NAME  job name


*******************************************************************************
usage: voxel51 jobs start [-h] [-a] [-f] [--dry-run] [ID [ID ...]]

Start jobs on the platform.

    Examples:
        # Start specific jobs
        voxel51 jobs start <id> [...]

        # Start all eligible (unstarted) jobs
        voxel51 jobs start --all

positional arguments:
  ID           the job ID(s) to start

optional arguments:
  -h, --help   show this help message and exit
  -a, --all    whether to start all eligible (unstarted) jobs
  -f, --force  whether to force start all without confirmation
  --dry-run    whether to print job IDs that would be started rather than actually performing the action


*******************************************************************************
usage: voxel51 jobs archive [-h] [-a] [-f] [--dry-run] [ID [ID ...]]

Archive jobs on the platform.

    Examples:
        # Archive specific jobs
        voxel51 jobs archive <id> [...]

        # Archive all jobs
        voxel51 jobs archive --all

positional arguments:
  ID           the job ID(s) to archive

optional arguments:
  -h, --help   show this help message and exit
  -a, --all    whether to archive all jobs
  -f, --force  whether to force archive all without confirmation
  --dry-run    whether to print job IDs that would be archived rather than actually performing the action


*******************************************************************************
usage: voxel51 jobs unarchive [-h] [-a] [-f] [--dry-run] [ID [ID ...]]

Unarchive jobs on the platform.

    Examples:
        # Unarchive specific jobs
        voxel51 jobs unarchive <id> [...]

        # Unarchive all eligible (unexpired) jobs
        voxel51 jobs unarchive --all

positional arguments:
  ID           the job ID(s) to unarchive

optional arguments:
  -h, --help   show this help message and exit
  -a, --all    whether to unarchive all eligible (unexpired) jobs
  -f, --force  whether to force unarchive all without confirmation
  --dry-run    whether to print job IDs that would be unarchived rather than actually performing the action


*******************************************************************************
usage: voxel51 jobs ttl [-h] [--days DAYS] [--date DATE] [-a] [-f] [--dry-run]
                        [ID [ID ...]]

Update TTL of jobs on the platform.

    Examples:
        # Extend TTL of jobs by given number of days
        voxel51 jobs ttl --days <days> <id> [...]

        # Set expiration date of jobs to given date
        voxel51 jobs ttl --date <date> <id> [...]

positional arguments:
  ID           the job ID(s) to update

optional arguments:
  -h, --help   show this help message and exit
  --days DAYS  the number of days by which to extend the TTL of the jobs
  --date DATE  new expiration date for the jobs
  -a, --all    whether to update all eligible (unexpired) jobs
  -f, --force  whether to force update all without confirmation
  --dry-run    whether to print job IDs that would be updated rather than actually performing the action


*******************************************************************************
usage: voxel51 jobs request [-h] [-p PATH] ID

Download job requests.

    Example:
        # Print job request
        voxel51 jobs request <id>

        # Download job request to disk
        voxel51 jobs request <id> --path '/path/for/request.json'

positional arguments:
  ID                    the job ID of interest

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  path to write request JSON


*******************************************************************************
usage: voxel51 jobs status [-h] [-p PATH] ID

Download job statuses.

    Example:
        # Print job status
        voxel51 jobs status <id>

        # Download job status to disk
        voxel51 jobs status <id> --path '/path/for/status.json'

positional arguments:
  ID                    the job ID of interest

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  path to write status JSON


*******************************************************************************
usage: voxel51 jobs log [-h] [-p PATH] [-u] ID

Download job logfiles.

    Example:
        # Print job logfile
        voxel51 jobs log <id>

        # Download job logfile to disk
        voxel51 jobs log <id> --path '/path/for/job.log'

        # Generate signed URL to download job logfile
        voxel51 jobs log <id> --url

positional arguments:
  ID                    the job ID of interest

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  path to write logfile
  -u, --url             generate signed URL to download job logfile


*******************************************************************************
usage: voxel51 jobs download [-h] [-p PATH] [-u] ID

Download job outputs.

    Examples:
        # Download job output to default location
        voxel51 jobs download <id>

        # Download job output to specific location
        voxel51 jobs download <id> --path '/path/for/job/output.json'

        # Generate signed URL to download job output
        voxel51 jobs download <id> --url

positional arguments:
  ID                    job output to download

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  path to write output
  -u, --url             generate signed URL to download job output


*******************************************************************************
usage: voxel51 jobs kill [-h] [-a] [-f] [--dry-run] [ID [ID ...]]

Kill jobs on the platform.

    Examples:
        # Kill specific jobs
        voxel51 jobs kill <id> [...]

        # Kill all eligible (queued or scheduled) jobs
        voxel51 jobs kill --all

positional arguments:
  ID           job ID(s) to kill

optional arguments:
  -h, --help   show this help message and exit
  -a, --all    whether to kill all eligible (queued or scheduled) jobs
  -f, --force  whether to force kill all without confirmation
  --dry-run    whether to print job IDs that would be killed rather than actually performing the action


*******************************************************************************
usage: voxel51 jobs delete [-h] [-a] [-f] [--dry-run] [ID [ID ...]]

Delete jobs on the platform.

    Examples:
        # Delete specific jobs
        voxel51 jobs delete <id> [...]

        # Delete all eligible (unstarted) jobs
        voxel51 jobs delete --all

positional arguments:
  ID           job ID(s) to delete

optional arguments:
  -h, --help   show this help message and exit
  -a, --all    whether to delete all eligible (unstarted) jobs
  -f, --force  whether to force delete all without confirmation
  --dry-run    whether to print job IDs that would be deleted rather than actually performing the action


*******************************************************************************
usage: voxel51 analytics [-h] [--all-help]
                         {list,info,doc,upload,upload-image,delete} ...

Tools for working with analytics.

optional arguments:
  -h, --help            show this help message and exit
  --all-help            show help recurisvely and exit

available commands:
  {list,info,doc,upload,upload-image,delete}
    list                List analytics on the platform.
    info                Get information about analytics on the platform.
    doc                 Get documentation about analytics.
    upload              Upload analytics to the platform.
    upload-image        Upload analytic images to the platform.
    delete              Delete analytics from the platform.


*******************************************************************************
usage: voxel51 analytics list [-h] [-l LIMIT] [-s SEARCH] [--sort-by FIELD]
                              [--ascending] [--all-versions] [-a] [-c]
                              [--public] [--user] [--include-pending]
                              [--exclude-pending] [--pending-only]

List analytics on the platform.

    Notes:
        Unless overridden, only the latest version of each analytic is listed,
        and pending analytics are included.

    Examples:
        # List analytics according to the given query
        voxel51 analytics list \
            [--limit <limit>] \
            [--search [<field>:]<str>[,...]] \
            [--sort-by <field>] \
            [--ascending] \
            [--all-versions] \
            [--all-fields] \
            [--count]

        # Flags for analytics with particular scopes
        voxel51 analytics list --public
        voxel51 analytics list --user

        # Flags for analytics with particular pending states
        # These flags are ignored when a search containing `pending` is found
        voxel51 analytics list --include-pending    (default behavior)
        voxel51 analytics list --exclude-pending
        voxel51 analytics list --only-pending

        # List the last 10 analytics of any version uploaded to the platform
        voxel51 analytics list --all-versions --limit 10 --sort-by upload_date

        # List public analytics whose names contain "sense"
        voxel51 analytics list --public --search name:sense

    Search syntax:
        The generic search syntax is:

            --search [<field>:]<str>[,...]

        where:
            <field>    an optional field name on which to search
            <str>      the search string

        The supported fields for analytics searches are `id`, `name`, `version`
        and `type`.

        If `<field>:` is omitted, the search will match any records for which
        any field contains the given search string.

        Multiple searches can be specified as a comma-separated list. Records
        must match all searches in order to appear in the search results.

        You can include special characters `,` and `:` in search strings by
        escaping them with `\`.

        Fields are case insensitive, and underscores can be used in-place of
        spaces.

optional arguments:
  -h, --help            show this help message and exit
  -l LIMIT, --limit LIMIT
                        limit the number of analytics listed
  -s SEARCH, --search SEARCH
                        search to limit results when listing analytics
  --sort-by FIELD       field to sort by when listing analytics
  --ascending           whether to sort in ascending order
  --all-versions        whether to include all versions of analytics
  -a, --all-fields      whether to print all available fields
  -c, --count           whether to show the number of analytics in the list

scope arguments:
  --public              public analytics
  --user                user analytics

pending arguments:
  --include-pending     include pending analytics (default behavior)
  --exclude-pending     exclude pending analytics
  --pending-only        only pending analytics


*******************************************************************************
usage: voxel51 analytics info [-h] [-a] ID [ID ...]

Get information about analytics on the platform.

    Examples:
        # Get analytic(s) info
        voxel51 analytics info <id> [...]

        # Get all available fields for analytics
        voxel51 analytics info --all-fields <id> [...]

positional arguments:
  ID                the analytic ID(s) of interest

optional arguments:
  -h, --help        show this help message and exit
  -a, --all-fields  whether to print all available fields


*******************************************************************************
usage: voxel51 analytics doc [-h] [-p PATH] ID

Get documentation about analytics.

    Examples:
        # Print documentation for analytic
        voxel51 analytics doc <id>

        # Write documentation for analytic to disk
        voxel51 analytics doc <id> --path '/path/for/doc.json'

positional arguments:
  ID                    the analytic ID

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  path to write doc JSON


*******************************************************************************
usage: voxel51 analytics upload [-h] [-t ANALYTIC_TYPE] [--print-id] PATH

Upload analytics to the platform.

    Examples:
        # Upload analytic
        voxel51 analytics upload '/path/to/doc.json' [--analytic-type TYPE]

positional arguments:
  PATH                  analytic documentation

optional arguments:
  -h, --help            show this help message and exit
  -t ANALYTIC_TYPE, --analytic-type ANALYTIC_TYPE
                        type of analytic (PLATFORM|IMAGE_TO_VIDEO). The default is PLATFORM
  --print-id            whether to print only the ID of the uploaded analytic


*******************************************************************************
usage: voxel51 analytics upload-image [-h] -i ID -p PATH -t TYPE

Upload analytic images to the platform.

    Examples:
        # Upload image for analytic
        voxel51 analytics upload-image \
            --id <id> --path '/path/to/image.tar.gz' --image-type TYPE

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -i ID, --id ID        analytic ID
  -p PATH, --path PATH  analytic image tarfile to upload
  -t TYPE, --image-type TYPE
                        type of image (CPU|GPU)


*******************************************************************************
usage: voxel51 analytics delete [-h] [-f] ID [ID ...]

Delete analytics from the platform.

    Example:
        # Delete analytics
        voxel51 analytics delete <id> [...]

positional arguments:
  ID           the analytic ID(s) to delete

optional arguments:
  -h, --help   show this help message and exit
  -f, --force  whether to force delete without confirmation


*******************************************************************************
usage: voxel51 status [-h] [-p] [-j]

Tools for checking the status of the platform.

    Examples:
        # Check status of all platform services
        voxel51 status

        # Check whether platform is up
        voxel51 status --platform

        # Check whether jobs cluster is up
        voxel51 status --jobs-cluster

optional arguments:
  -h, --help          show this help message and exit
  -p, --platform      check if platform is up
  -j, --jobs-cluster  check if jobs cluster is up
```


## Copyright

Copyright 2017-2019, Voxel51, Inc.<br>
[voxel51.com](https://voxel51.com)
