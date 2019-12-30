'''
Core module that defines the functionality of the `voxel51` command-line
interface (CLI) for the Voxel51 Platform API.

| Copyright 2017-2019, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
# pragma pylint: disable=redefined-builtin
# pragma pylint: disable=unused-wildcard-import
# pragma pylint: disable=wildcard-import
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import *
from future.utils import iteritems
# pragma pylint: enable=redefined-builtin
# pragma pylint: enable=unused-wildcard-import
# pragma pylint: enable=wildcard-import

import argparse
import json
import logging
import sys

import dateutil.parser
from tabulate import tabulate
from tzlocal import get_localzone

import voxel51.constants as voxc
from voxel51.users.api import API
import voxel51.users.auth as voxa
from voxel51.users.jobs import JobRequest, JobState
from voxel51.users.query import AnalyticsQuery, DataQuery, JobsQuery
import voxel51.users.utils as voxu


logger = logging.getLogger(__name__)


MAX_NAME_COLUMN_WIDTH = 51
TABLE_FORMAT = "simple"


class Command(object):
    '''Interface for defining commands.

    Command instances must implement the `setup()` method, and they should
    implement the `run()` method if they perform any functionality beyond
    defining subparsers.
    '''

    @staticmethod
    def setup(parser):
        '''Setup the command-line arguments for the command.

        Args:
            parser: an `argparse.ArgumentParser` instance
        '''
        raise NotImplementedError("subclass must implement setup()")

    @staticmethod
    def run(args):
        '''Execute the command on the given args.

        args:
            args: an `argparse.Namespace` instance containing the arguments
                for the command
        '''
        pass


class Voxel51Command(Command):
    '''Voxel51 Platform API command-line interface.'''

    @staticmethod
    def setup(parser):
        subparsers = parser.add_subparsers(title="available commands")
        _register_command(subparsers, "auth", AuthCommand)
        _register_command(subparsers, "data", DataCommand)
        _register_command(subparsers, "jobs", JobsCommand)
        _register_command(subparsers, "analytics", AnalyticsCommand)


class AuthCommand(Command):
    '''Tools for configuring API tokens.'''

    @staticmethod
    def setup(parser):
        subparsers = parser.add_subparsers(title="available commands")
        _register_command(subparsers, "show", ShowAuthCommand)
        _register_command(subparsers, "activate", ActivateAuthCommand)
        _register_command(subparsers, "deactivate", DeactivateAuthCommand)


class ShowAuthCommand(Command):
    '''Show info about the active API token.

    Examples:
        # Print info about active token
        voxel51 auth show
    '''

    @staticmethod
    def setup(parser):
        pass

    @staticmethod
    def run(args):
        _print_active_token_info()


class ActivateAuthCommand(Command):
    '''Activate an API token.

    Examples:
        # Activate API token
        voxel51 auth activate '/path/to/token.json'
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "activate", help="path to API token to activate")

    @staticmethod
    def run(args):
        voxa.activate_token(args.activate)


class DeactivateAuthCommand(Command):
    '''Deletes the active API token, if any.'''

    @staticmethod
    def setup(parser):
        pass

    @staticmethod
    def run(args):
        voxa.deactivate_token()


class DataCommand(Command):
    '''Tools for working with data.'''

    @staticmethod
    def setup(parser):
        subparsers = parser.add_subparsers(title="available commands")
        _register_command(subparsers, "list", ListDataCommand)
        _register_command(subparsers, "info", InfoDataCommand)
        _register_command(subparsers, "upload", UploadDataCommand)
        _register_command(subparsers, "download", DownloadDataCommand)
        _register_command(subparsers, "ttl", TTLDataCommand)
        _register_command(subparsers, "delete", DeleteDataCommand)


class ListDataCommand(Command):
    '''List data uploaded to the platform.

    Examples:
        # List data according to the given query
        voxel51 data list
            [--limit <limit>]
            [--search [<field>:]<str>[,...]]
            [--sort-by <field>]
            [--ascending]
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
        escaping them with `\\`.

        Fields are case insensitive, and underscores can be used in-place of
        spaces.
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "-l", "--limit", metavar="LIMIT", type=int, default=-1,
            help="limit the number of data listed")
        parser.add_argument(
            "-s", "--search", metavar="SEARCH",
            help="search to limit results when listing data")
        parser.add_argument(
            "-c", "--count", action="store_true",
            help="whether to show the number of data in the list")
        parser.add_argument(
            "--sort-by", metavar="FIELD",
            help="field to sort by when listing data")
        parser.add_argument(
            "--ascending", action="store_true",
            help="whether to sort in ascending order")

    @staticmethod
    def run(args):
        api = API()

        query = DataQuery().add_all_fields()

        if args.limit >= 0:
            query = query.set_limit(args.limit)

        sort_field = args.sort_by if args.sort_by else "upload_date"
        descending = not args.ascending
        query = query.sort_by(sort_field, descending=descending)

        if args.search is not None:
            query = query.add_search_direct(args.search)

        data = api.query_data(query)["data"]
        _print_data_table(data, show_count=args.count)


class InfoDataCommand(Command):
    '''Get information about data uploaded to the platform.

    Examples:
        # Get data info
        voxel51 data info <id> [...]
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="+", metavar="ID", help="the data ID(s) of interest")

    @staticmethod
    def run(args):
        api = API()

        data = [api.get_data_details(data_id) for data_id in args.ids]
        _print_data_table(data)


class UploadDataCommand(Command):
    '''Upload data to the platform.

    Examples:
        # Upload data
        voxel51 data upload '/path/to/video.mp4' [...]
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "paths", nargs="+", metavar="PATH", help="the file(s) to upload")

    @staticmethod
    def run(args):
        api = API()

        uploads = []
        for path in args.paths:
            logger.info("Uploading data '%s'", path)
            metadata = api.upload_data(path)
            uploads.append({"id": metadata["id"], "path": path})

        table_str = tabulate(uploads, headers="keys", tablefmt=TABLE_FORMAT)
        logger.info("\n" + table_str + "\n")


class DownloadDataCommand(Command):
    '''Download data from the platform.

    Examples:
        # Download data to default location
        voxel51 data download <id>

        # Download data to specific location
        voxel51 data download <id> --path '/path/for/video.mp4'

        # Generate signed URL to download data
        voxel51 data download <id> --url
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument("id", metavar="ID", help="data to download")
        parser.add_argument(
            "-p", "--path", metavar="PATH", help="path to download data")
        parser.add_argument(
            "-u", "--url", metavar="ID",
            help="generate signed URL to download data")

    @staticmethod
    def run(args):
        api = API()

        data_id = args.id

        if args.url:
            url = api.get_data_download_url(data_id)
            logger.info(url)
            return

        output_path = api.download_data(data_id, output_path=args.path)
        logger.info("Downloaded '%s' to '%s'", data_id, output_path)


class TTLDataCommand(Command):
    '''Update TTL of data on the platform.

    Examples:
        # Update TTL of data
        voxel51 data ttl --days <days> <id> [...]

        # Update TTL of all data
        voxel51 data ttl --days <days> --all
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="*", metavar="ID", help="the data ID(s) to update")
        parser.add_argument(
            "-d", "--days", metavar="DAYS", type=float,
            help="the number of days by which to extend the TTL of the data")
        parser.add_argument(
            "-a", "--all", action="store_true",
            help="whether to update all data")
        parser.add_argument(
            "-f", "--force", action="store_true",
            help="whether to force update all without confirmation")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="whether to print data IDs that would be updated rather than"
            "actually performing the action")

    @staticmethod
    def run(args):
        api = API()

        if not args.days:
            return

        if args.all:
            data_ids = [data["id"] for data in api.list_data()]
        else:
            data_ids = args.ids or []

        if args.dry_run:
            for data_id in data_ids:
                logger.info(data_id)
            return

        num_data = len(data_ids)

        if args.all:
            logger.info("Found %d data to update TTL", num_data)
            if num_data > 0 and not args.force:
                _abort_if_requested()

        if num_data == 0:
            return

        failures = _get_batch_failures(
            api.batch_update_data_ttl(data_ids, args.days))
        if not failures:
            logger.info("Data TTL(s) updated")
        else:
            for data_id, message in failures.items():
                logger.warning(
                    "Failed to update TTL of data '%s': %s", data_id, message)


class DeleteDataCommand(Command):
    '''Delete data from the platform.

    Examples:
        # Delete data
        voxel51 data delete <id> [...]

        # Delete all data
        voxel51 data delete --all
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="*", metavar="ID", help="the data ID(s) to delete")
        parser.add_argument(
            "-a", "--all", action="store_true",
            help="whether to delete all data")
        parser.add_argument(
            "-f", "--force", action="store_true",
            help="whether to force delete all without confirmation")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="whether to print data IDs that would be deleted rather than"
            "actually performing the action")

    @staticmethod
    def run(args):
        api = API()

        if args.all:
            data_ids = [data["id"] for data in api.list_data()]
        else:
            data_ids = args.ids or []

        if args.dry_run:
            for data_id in data_ids:
                logger.info(data_id)
            return

        num_data = len(data_ids)

        if args.all:
            logger.info("Found %d data to delete", num_data)
            if num_data > 0 and not args.force:
                _abort_if_requested()

        if num_data == 0:
            return

        failures = _get_batch_failures(api.batch_delete_data(data_ids))
        if not failures:
            logger.info("Data deleted")
        else:
            for data_id, message in failures.items():
                logger.warning(
                    "Failed to delete data '%s': %s", data_id, message)


class JobsCommand(Command):
    '''Tools for working with jobs.'''

    @staticmethod
    def setup(parser):
        subparsers = parser.add_subparsers(title="available commands")
        _register_command(subparsers, "list", ListJobsCommand)
        _register_command(subparsers, "info", InfoJobsCommand)
        _register_command(subparsers, "upload", UploadJobsCommand)
        _register_command(subparsers, "start", StartJobsCommand)
        _register_command(subparsers, "archive", ArchiveJobsCommand)
        _register_command(subparsers, "unarchive", UnarchiveJobsCommand)
        _register_command(subparsers, "ttl", TTLJobsCommand)
        _register_command(subparsers, "request", RequestJobsCommand)
        _register_command(subparsers, "status", StatusJobsCommand)
        _register_command(subparsers, "log", LogJobsCommand)
        _register_command(subparsers, "download", DownloadJobsCommand)
        _register_command(subparsers, "kill", KillJobsCommand)
        _register_command(subparsers, "delete", DeleteJobsCommand)


class ListJobsCommand(Command):
    '''List jobs on the platform.

    Examples:
        # List jobs according to the given query
        voxel51 jobs list
            [--limit <limit>]
            [--search [<field>:]<str>[,...]]
            [--sort-by <field>]
            [--archived]
            [--ascending]
            [--count]

        # Flags for jobs in a particular state
        voxel51 jobs list --ready
        voxel51 jobs list --queued
        voxel51 jobs list --scheduled
        voxel51 jobs list --running
        voxel51 jobs list --complete
        voxel51 jobs list --failed

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
        escaping them with `\\`.

        Fields are case insensitive, and underscores can be used in-place of
        spaces.
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "-l", "--limit", metavar="LIMIT", type=int, default=-1,
            help="limit the number of jobs listed")
        parser.add_argument(
            "-s", "--search", metavar="SEARCH",
            help="search to limit results when listing jobs")
        parser.add_argument(
            "-c", "--count", action="store_true",
            help="whether to show the number of jobs in the list")
        parser.add_argument(
            "--sort-by", metavar="FIELD",
            help="field to sort by when listing jobs")
        parser.add_argument(
            "--ascending", action="store_true",
            help="whether to sort in ascending order")
        parser.add_argument(
            "--archived", action="store_true",
            help="whether to list archived jobs")

        states = parser.add_argument_group("state arguments")
        states.add_argument(
            "--ready", action="store_true", help="jobs in READY state")
        states.add_argument(
            "--queued", action="store_true", help="jobs in QUEUED state")
        states.add_argument(
            "--scheduled", action="store_true", help="jobs in SCHEDULED state")
        states.add_argument(
            "--running", action="store_true", help="jobs in RUNNING state")
        states.add_argument(
            "--complete", action="store_true", help="jobs in COMPLETE state")
        states.add_argument(
            "--failed", action="store_true", help="jobs in FAILED state")

    @staticmethod
    def run(args):
        api = API()

        query = JobsQuery().add_all_fields()

        if args.limit >= 0:
            query = query.set_limit(args.limit)

        sort_field = args.sort_by if args.sort_by else "upload_date"
        descending = not args.ascending
        query = query.sort_by(sort_field, descending=descending)

        states = []
        if args.ready:
            states.append(JobState.READY)
        if args.queued:
            states.append(JobState.QUEUED)
        if args.scheduled:
            states.append(JobState.SCHEDULED)
        if args.running:
            states.append(JobState.RUNNING)
        if args.complete:
            states.append(JobState.COMPLETE)
        if args.failed:
            states.append(JobState.FAILED)
        if states:
            query = query.add_search_or("state", states)

        if args.search is not None:
            query = query.add_search_direct(args.search)

        if (args.archived or args.search is None or
                not "archived:" in args.search):
            query = query.add_search("archived", args.archived)

        jobs = api.query_jobs(query)["jobs"]
        _print_jobs_table(jobs, show_count=args.count)


class InfoJobsCommand(Command):
    '''Get information about jobs on the platform.

    Examples:
        # Get job(s) info
        voxel51 jobs info <id> [...]
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="+", metavar="ID", help="the job ID(s) of interest")

    @staticmethod
    def run(args):
        api = API()

        jobs = [api.get_job_details(job_id) for job_id in args.ids]
        _print_jobs_table(jobs)


class UploadJobsCommand(Command):
    '''Upload job requests to the platform.

    Examples:
        # Upload job request
        voxel51 jobs upload '/path/to/request.json'
            --name <job-name> [--auto-start]
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "path", metavar="PATH", help="job request to upload")
        parser.add_argument(
            "-n", "--name", metavar="NAME", help="job name")
        parser.add_argument(
            "--auto-start", action="store_true",
            help="whether to automatically start job")

    @staticmethod
    def run(args):
        api = API()

        request = JobRequest.from_json(args.path)
        job_id = api.upload_job_request(
            request, args.name, auto_start=args.auto_start)
        if args.auto_start:
            logger.info("Created and started job '%s'", job_id)
        else:
            logger.info("Created job '%s'", job_id)


class StartJobsCommand(Command):
    '''Start jobs on the platform.

    Examples:
        # Start specific jobs
        voxel51 jobs start <id> [...]

        # Start all eligible (i.e., unstarted) jobs
        voxel51 jobs start --all
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="*", metavar="ID", help="the job ID(s) to start")
        parser.add_argument(
            "-a", "--all", action="store_true",
            help="whether to start all eligible jobs")
        parser.add_argument(
            "-f", "--force", action="store_true",
            help="whether to force start all without confirmation")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="whether to print job IDs that would be started rather than"
            "actually performing the action")

    @staticmethod
    def run(args):
        api = API()

        if args.all:
            query = (JobsQuery()
                .add_all_fields()
                .add_search("state", JobState.READY)
                .add_search("archived", False)
                .sort_by("upload_date", descending=False))
            jobs = api.query_jobs(query)["jobs"]
            job_ids = [job["id"] for job in jobs]
        else:
            job_ids = args.ids

        if args.dry_run:
            for job_id in job_ids:
                logger.info(job_id)
            return

        num_jobs = len(job_ids)

        if args.all:
            logger.info("Found %d job(s) to start", num_jobs)
            if num_jobs > 0 and not args.force:
                _abort_if_requested()

        if num_jobs == 0:
            return

        failures = _get_batch_failures(api.batch_start_jobs(job_ids))
        if not failures:
            logger.info("Job(s) started")
        else:
            for job_id, message in failures.items():
                logger.warning("Failed to start job '%s': %s", job_id, message)


class ArchiveJobsCommand(Command):
    '''Archive jobs on the platform.

    Examples:
        # Archive specific jobs
        voxel51 jobs archive <id> [...]

        # Archive all jobs
        voxel51 jobs archive --all
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="*", metavar="ID", help="the job ID(s) to archive")
        parser.add_argument(
            "-a", "--all", action="store_true",
            help="whether to archive all jobs")
        parser.add_argument(
            "-f", "--force", action="store_true",
            help="whether to force archive all without confirmation")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="whether to print job IDs that would be archived rather than"
            "actually performing the action")

    @staticmethod
    def run(args):
        api = API()

        if args.all:
            query = (JobsQuery()
                .add_all_fields()
                .add_search("archived", False)
                .sort_by("upload_date", descending=False))
            jobs = api.query_jobs(query)["jobs"]
            job_ids = [job["id"] for job in jobs]
        else:
            job_ids = args.ids

        if args.dry_run:
            for job_id in job_ids:
                logger.info(job_id)
            return

        num_jobs = len(job_ids)

        if args.all:
            logger.info("Found %d job(s) to archive", num_jobs)
            if num_jobs > 0 and not args.force:
                _abort_if_requested()

        if num_jobs == 0:
            return

        failures = _get_batch_failures(api.batch_archive_jobs(job_ids))
        if not failures:
            logger.info("Job(s) archived")
        else:
            for job_id, message in failures.items():
                logger.warning(
                    "Failed to archive job '%s': %s", job_id, message)


class UnarchiveJobsCommand(Command):
    '''Unarchive jobs on the platform.

    Examples:
        # Unarchive specific jobs
        voxel51 jobs unarchive <id> [...]

        # Unarchive all eligible (i.e., unexpired) jobs
        voxel51 jobs unarchive --all
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="*", metavar="ID", help="the job ID(s) to unarchive")
        parser.add_argument(
            "-a", "--all", action="store_true",
            help="whether to unarchive all eligible jobs")
        parser.add_argument(
            "-f", "--force", action="store_true",
            help="whether to force unarchive all without confirmation")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="whether to print job IDs that would be unarchived rather "
            "than actually performing the action")

    @staticmethod
    def run(args):
        api = API()

        if args.all:
            query = (JobsQuery()
                .add_all_fields()
                .add_search("archived", True)
                .sort_by("upload_date", descending=False))
            jobs = api.query_jobs(query)["jobs"]

            # Exclude expired jobs
            job_ids = [
                job["id"] for job in jobs if not api.is_job_expired(job=job)]
        else:
            job_ids = args.ids

        if args.dry_run:
            for job_id in job_ids:
                logger.info(job_id)
            return

        num_jobs = len(job_ids)

        if args.all:
            logger.info("Found %d job(s) to unarchive", num_jobs)
            if num_jobs > 0 and not args.force:
                _abort_if_requested()

        if num_jobs == 0:
            return

        failures = _get_batch_failures(api.batch_unarchive_jobs(job_ids))
        if not failures:
            logger.info("Job(s) unarchived")
        else:
            for job_id, message in failures.items():
                logger.warning(
                    "Failed to unarchive job '%s': %s", job_id, message)


class TTLJobsCommand(Command):
    '''Update TTL of jobs on the platform.

    Examples:
        # Update TTL of jobs
        voxel51 jobs ttl --days <days> <id> [...]

        # Update TTL of all eligible (i.e., unexpired) jobs
        voxel51 jobs ttl --days <days> --all
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="*", metavar="ID", help="the job ID(s) to update")
        parser.add_argument(
            "-d", "--days", metavar="DAYS", type=float,
            help="the number of days by which to extend the TTL of the jobs")
        parser.add_argument(
            "-a", "--all", action="store_true",
            help="whether to update all eligible jobs")
        parser.add_argument(
            "-f", "--force", action="store_true",
            help="whether to force update all without confirmation")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="whether to print job IDs that would be updated rather than"
            "actually performing the action")

    @staticmethod
    def run(args):
        api = API()

        if not args.days:
            return

        if args.all:
            query = (JobsQuery()
                .add_all_fields()
                .sort_by("upload_date", descending=False))
            jobs = api.query_jobs(query)["jobs"]

            # Exclude expired jobs
            job_ids = [
                job["id"] for job in jobs if not api.is_job_expired(job=job)]
        else:
            job_ids = args.ids

        if args.dry_run:
            for job_id in job_ids:
                logger.info(job_id)
            return

        num_jobs = len(job_ids)

        if args.all:
            logger.info("Found %d jobs to update TTL", num_jobs)
            if num_jobs > 0 and not args.force:
                _abort_if_requested()

        if num_jobs == 0:
            return

        failures = _get_batch_failures(
            api.batch_update_jobs_ttl(job_ids, args.days))
        if not failures:
            logger.info("Job TTL(s) updated")
        else:
            for job_id, message in failures.items():
                logger.warning(
                    "Failed to update TTL of job '%s': %s", job_id, message)


class RequestJobsCommand(Command):
    '''Download job requests.

    Example:
        # Print job request
        voxel51 jobs request <id>

        # Download job request to disk
        voxel51 jobs request <id> --path '/path/for/request.json'
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument("id", metavar="ID", help="the job ID of interest")
        parser.add_argument(
            "-p", "--path", metavar="PATH", help="path to write request JSON")

    @staticmethod
    def run(args):
        api = API()

        request = api.get_job_request(args.id)

        if args.path:
            request.to_json(args.path)
            logger.info(
                "Request for job '%s' written to '%s'", args.id, args.path)
        else:
            logger.info(request)


class StatusJobsCommand(Command):
    '''Download job statuses.

    Example:
        # Print job status
        voxel51 jobs status <id>

        # Download job status to disk
        voxel51 jobs status <id> --path '/path/for/status.json'
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument("id", metavar="ID", help="the job ID of interest")
        parser.add_argument(
            "-p", "--path", metavar="PATH", help="path to write status JSON")

    @staticmethod
    def run(args):
        api = API()

        status = api.get_job_status(args.id)

        if args.path:
            voxu.write_json(status, args.path)
            logger.info(
                "Status for job '%s' written to '%s'", args.id, args.path)
        else:
            _print_dict_as_json(status)


class LogJobsCommand(Command):
    '''Download job logfiles.

    Example:
        # Print job logfile
        voxel51 jobs log <id>

        # Download job logfile to disk
        voxel51 jobs log <id> --path '/path/for/job.log'
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument("id", metavar="ID", help="the job ID of interest")
        parser.add_argument(
            "-p", "--path", metavar="PATH", help="path to write logfile")

    @staticmethod
    def run(args):
        api = API()

        if args.path:
            api.download_job_logfile(args.id, output_path=args.path)
            logger.info(
                "Logfile for job '%s' written to '%s'", args.id, args.path)
        else:
            logfile = api.download_job_logfile(args.id, output_path=args.path)
            logger.info(logfile)


class DownloadJobsCommand(Command):
    '''Download job outputs.

    Examples:
        # Download job output to default location
        voxel51 jobs download <id>

        # Download job output to specific location
        voxel51 jobs download <id> --path '/path/for/job/output.json'

        # Generate signed URL to download job output
        voxel51 jobs download <id> --url
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "download", metavar="ID", help="job output to download")
        parser.add_argument(
            "-p", "--path", metavar="PATH", help="path to write output")
        parser.add_argument(
            "-u", "--url", metavar="ID",
            help="generate signed URL to download job output")

    @staticmethod
    def run(args):
        api = API()

        job_id = args.download

        if args.url:
            url = api.get_job_output_download_url(job_id)
            logger.info(url)
            return

        output_path = api.download_job_output(job_id, output_path=args.path)
        logger.info("Downloaded '%s' to '%s'", job_id, output_path)


class KillJobsCommand(Command):
    '''Kill jobs on the platform.

    Examples:
        # Kill specific jobs
        voxel51 jobs kill <id> [...]

        # Kill all eligible (i.e., queued or scheduled) jobs
        voxel51 jobs kill --all
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="*", metavar="ID", help="job ID(s) to kill")
        parser.add_argument(
            "-a", "--all", action="store_true",
            help="whether to kill all eligible jobs")
        parser.add_argument(
            "-f", "--force", action="store_true",
            help="whether to force kill all without confirmation")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="whether to print job IDs that would be killed rather than"
            "actually performing the action")

    @staticmethod
    def run(args):
        api = API()

        if args.all:
            query = (JobsQuery()
                .add_all_fields()
                .add_search("archived", False)
                .add_search_or("state", [JobState.QUEUED, JobState.SCHEDULED])
                .sort_by("upload_date", descending=False))
            jobs = api.query_jobs(query)["jobs"]
            job_ids = [job["id"] for job in jobs]
        else:
            job_ids = args.ids

        if args.dry_run:
            for job_id in job_ids:
                logger.info(job_id)
            return

        num_jobs = len(job_ids)

        if args.all:
            logger.info("Found %d job(s) to kill", num_jobs)
            if num_jobs > 0 and not args.force:
                _abort_if_requested()

        if num_jobs == 0:
            return

        failures = _get_batch_failures(api.batch_kill_jobs(job_ids))
        if not failures:
            logger.info("Job(s) killed")
        else:
            for job_id, message in failures.items():
                logger.warning("Failed to kill job '%s': %s", job_id, message)


class DeleteJobsCommand(Command):
    '''Delete jobs on the platform.

    Examples:
        # Delete specific jobs
        voxel51 jobs delete <id> [...]

        # Delete all eligible (i.e., unstarted) jobs
        voxel51 jobs delete --all
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="*", metavar="ID", help="job ID(s) to delete")
        parser.add_argument(
            "-a", "--all", action="store_true",
            help="whether to delete all eligible jobs")
        parser.add_argument(
            "-f", "--force", action="store_true",
            help="whether to force delete all without confirmation")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="whether to print job IDs that would be deleted rather than"
            "actually performing the action")

    @staticmethod
    def run(args):
        api = API()

        if args.all:
            query = (JobsQuery()
                .add_all_fields()
                .add_search("archived", False)
                .add_search("state", JobState.READY)
                .sort_by("upload_date", descending=False))
            jobs = api.query_jobs(query)["jobs"]
            job_ids = [job["id"] for job in jobs]
        else:
            job_ids = args.ids

        if args.dry_run:
            for job_id in job_ids:
                logger.info(job_id)
            return

        num_jobs = len(job_ids)

        if args.all:
            logger.info("Found %d job(s) to delete", num_jobs)
            if num_jobs > 0 and not args.force:
                _abort_if_requested()

        if num_jobs == 0:
            return

        failures = _get_batch_failures(api.batch_delete_jobs(job_ids))
        if not failures:
            logger.info("Job(s) deleted")
        else:
            for job_id, message in failures.items():
                logger.warning(
                    "Failed to delete job '%s': %s", job_id, message)


class AnalyticsCommand(Command):
    '''Tools for working with analytics.'''

    @staticmethod
    def setup(parser):
        subparsers = parser.add_subparsers(title="available commands")
        _register_command(subparsers, "list", ListAnalyticsCommand)
        _register_command(subparsers, "info", InfoAnalyticsCommand)
        _register_command(subparsers, "doc", DocAnalyticsCommand)
        _register_command(subparsers, "upload", UploadAnalyticsCommand)
        _register_command(subparsers, "delete", DeleteAnalyticsCommand)


class ListAnalyticsCommand(Command):
    '''List analytics on the platform.

    Examples:
        # List analytics according to the given query
        voxel51 analytics list
            [--limit <limit>]
            [--search [<field>:]<str>[,...]]
            [--sort-by <field>]
            [--all-versions]
            [--ascending]
            [--count]

        # Flags for analytics with particular scopes
        voxel51 analytics list --public
        voxel51 analytics list --user

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
        escaping them with `\\`.

        Fields are case insensitive, and underscores can be used in-place of
        spaces.
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "-l", "--limit", metavar="LIMIT", type=int, default=-1,
            help="limit the number of analytics listed")
        parser.add_argument(
            "-s", "--search", metavar="SEARCH",
            help="search to limit results when listing analytics")
        parser.add_argument(
            "--sort-by", metavar="FIELD",
            help="field to sort by when listing analytics")
        parser.add_argument(
            "-a", "--all-versions", action="store_true",
            help="whether to include all versions of analytics")
        parser.add_argument(
            "--ascending", action="store_true",
            help="whether to sort in ascending order")
        parser.add_argument(
            "-c", "--count", action="store_true",
            help="whether to show the number of analytics in the list")

        scopes = parser.add_argument_group("scope arguments")
        scopes.add_argument(
            "--public", action="store_true", help="public analytics")
        scopes.add_argument(
            "--user", action="store_true", help="user analytics")

    @staticmethod
    def run(args):
        api = API()

        query = AnalyticsQuery().add_all_fields()

        if args.limit >= 0:
            query = query.set_limit(args.limit)

        sort_field = args.sort_by if args.sort_by else "upload_date"
        descending = not args.ascending
        query = query.sort_by(sort_field, descending=descending)

        query = query.set_all_versions(args.all_versions)

        scopes = []
        if args.public:
            scopes.append("public")
        if args.user:
            scopes.append("user")
        if scopes:
            query = query.add_search_or("scope", scopes)

        if args.search is not None:
            query = query.add_search_direct(args.search)

        analytics = api.query_analytics(query)["analytics"]
        _print_analytics_table(analytics, show_count=args.count)


class InfoAnalyticsCommand(Command):
    '''Get information about analytics on the platform.

    Examples:
        # Get analytic(s) info
        voxel51 analytics info <id> [...]
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="+", metavar="ID",
            help="the analytic ID(s) of interest")

    @staticmethod
    def run(args):
        api = API()

        analytics = [
            api.get_analytic_details(analytic_id) for analytic_id in args.ids]
        _print_analytics_table(analytics)


class DocAnalyticsCommand(Command):
    '''Get documentation about analytics.

    Examples:
        # Print documentation for analytic
        voxel51 analytics doc <id>

        # Write documentation for analytic to disk
        voxel51 analytics doc <id> --path '/path/for/doc.json'
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument("id", metavar="ID", help="the analytic ID")
        parser.add_argument(
            "-p", "--path", metavar="PATH", help="path to write doc JSON")

    @staticmethod
    def run(args):
        api = API()

        doc = api.get_analytic_doc(args.id)

        if args.path:
            voxu.write_json(doc, args.path)
            logger.info(
                "Documentation for analytic '%s' written to '%s'",
                args.id, args.path)
        else:
            _print_dict_as_json(doc)


class UploadAnalyticsCommand(Command):
    '''Upload analytics to the platform.

    Examples:
        # Upload documentation for analytic
        voxel51 analytics upload --doc '/path/to/doc.json'
            [--analytic-type TYPE] [--print-id]

        # Upload analytic image
        voxel51 analytics upload --image <id>
            --path '/path/to/image.tar.gz' --image-type cpu|gpu
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "--doc", metavar="PATH", help="analytic documentation to upload")
        parser.add_argument(
            "--analytic-type", help="type of analytic")
        parser.add_argument(
            "--print-id", action="store_true",
            help="whether to print only the ID of the uploaded analytic")
        parser.add_argument(
            "--image", metavar="ID",
            help="analytic ID to upload image for")
        parser.add_argument(
            "--path", metavar="PATH", help="analytic image to upload")
        parser.add_argument(
            "--image-type", help="type of image being uploaded")

    @staticmethod
    def run(args):
        api = API()

        # Upload analytic documentation
        if args.doc:
            metadata = api.upload_analytic(
                args.doc, analytic_type=args.analytic_type)
            if args.print_id:
                logger.info(metadata["id"])
            else:
                _print_dict_as_table(metadata)

        # Upload analytic image
        if args.image:
            analytic_id = args.image
            image_type = args.image_type
            api.upload_analytic_image(analytic_id, args.path, image_type)
            logger.info(
                "%s image for analytic %s uploaded", image_type.upper(),
                analytic_id)


class DeleteAnalyticsCommand(Command):
    '''Delete analytics from the platform.

    Example:
        # Delete analytics
        voxel51 analytics delete <id> [...]
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "ids", nargs="+", metavar="ID",
            help="the analytic ID(s) to delete")
        parser.add_argument(
            "-f", "--force", action="store_true",
            help="whether to force delete without confirmation")

    @staticmethod
    def run(args):
        api = API()

        analytic_ids = args.ids

        num_analytics = len(analytic_ids)
        logger.info("Found %d analytic(s) to delete", num_analytics)
        if num_analytics > 0 and not args.force:
            _abort_if_requested()

        for analytic_id in analytic_ids:
            api.delete_analytic(analytic_id)
            logger.info("Analytic '%s' deleted", analytic_id)


def _print_active_token_info():
    token_path = voxa.get_active_token_path()
    token = voxa.load_token(token_path=token_path)
    contents = [
        ("id", token.id),
        ("creation date", _render_datetime(token.creation_date)),
        ("base API URL", token.base_api_url),
        ("path", token_path),
    ]
    table_str = tabulate(
        contents, headers=["API token", ""], tablefmt=TABLE_FORMAT)
    logger.info(table_str)


def _print_data_table(data, show_count=False):
    records = [
        (
            d["id"], _render_name(d["name"]), _render_bytes(d["size"]),
            d["type"], _render_datetime(d["upload_date"]),
            _render_datetime(d["expiration_date"])
        ) for d in data]

    table_str = tabulate(
        records, headers=[
            "id", "name", "size", "type", "upload date", "expiration date"],
        tablefmt=TABLE_FORMAT)

    logger.info(table_str)
    if show_count:
        total_size = _render_bytes(sum(d["size"] for d in data))
        logger.info("\nShowing %d data, %s\n", len(records), total_size)


def _print_jobs_table(jobs, show_count=False):
    records = [
        (
            j["id"], _render_name(j["name"]), j["state"], j["archived"],
            _render_datetime(j["upload_date"]),
            _render_datetime(j["expiration_date"])
        ) for j in jobs]

    table_str = tabulate(
        records, headers=[
            "id", "name", "state", "archived", "upload date",
            "expiration date"],
        tablefmt=TABLE_FORMAT)

    logger.info(table_str)
    if show_count:
        logger.info("\nShowing %d job(s)\n", len(records))


def _print_analytics_table(analytics, show_count=False):
    records = [
        (
            a["id"], a["name"], a["version"], a["scope"],
            bool(a["supports_cpu"]), bool(a["supports_gpu"]),
            bool(a["pending"]), _render_datetime(a["upload_date"]),
        ) for a in analytics]

    table_str = tabulate(
        records, headers=[
            "id", "name", "version", "scope", "supports cpu", "supports gpu",
            "pending", "upload date"],
        tablefmt=TABLE_FORMAT)

    logger.info(table_str)
    if show_count:
        logger.info("\nFound %d analytic(s)\n", len(records))


def _print_dict_as_json(d):
    s = json.dumps(d, indent=4)
    logger.info(s)


def _print_dict_as_table(d):
    contents = list(d.items())
    table_str = tabulate(contents, tablefmt="plain")
    logger.info(table_str)


def _render_name(name):
    if len(name) > MAX_NAME_COLUMN_WIDTH:
        name = name[:(MAX_NAME_COLUMN_WIDTH - 4)] + " ..."
    return name


def _render_bytes(size):
    if size is None or size < 0:
        return ""
    return voxu.to_human_bytes_str(size)


def _render_datetime(datetime_str):
    dt = dateutil.parser.isoparse(datetime_str)
    return dt.astimezone(get_localzone()).strftime("%Y-%m-%d %H:%M:%S %Z")


def _abort_if_requested():
    should_continue = voxu.query_yes_no(
        "Are you sure you want to continue?", default="no")

    if not should_continue:
        sys.exit(0)


def _register_main_command(command, version=None):
    parser = argparse.ArgumentParser(description=command.__doc__.rstrip())
    if version:
        parser.add_argument(
            "-v", "--version", action="version", version=version,
            help="show version info")

    parser.set_defaults(run=command.run)
    command.setup(parser)
    return parser


def _register_command(parent, name, command):
    parser = parent.add_parser(
        name, help=command.__doc__.splitlines()[0],
        description=command.__doc__.rstrip(),
        formatter_class=argparse.RawTextHelpFormatter)
    parser.set_defaults(run=command.run)
    command.setup(parser)
    return parser


def _get_batch_failures(batch_result):
    return {
        id: status.get("message") for id, status in batch_result.items()
            if not status["success"]
    }


def main():
    '''Executes the `voxel51` tool with the given command-line args.'''
    parser = _register_main_command(Voxel51Command, version=voxc.VERSION_LONG)

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    args.run(args)
