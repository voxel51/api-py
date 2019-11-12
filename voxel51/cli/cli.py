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
# pragma pylint: enable=redefined-builtin
# pragma pylint: enable=unused-wildcard-import
# pragma pylint: enable=wildcard-import

import argparse
import json
import sys

from tabulate import tabulate

from voxel51.users.api import API
import voxel51.users.auth as voxa
from voxel51.users.jobs import JobRequest
from voxel51.users.query import AnalyticsQuery, DataQuery, JobsQuery


MAX_NAME_COLUMN_WIDTH = 51
TABLE_FORMAT = "simple"


class Command(object):
    '''Interface for defining commands for the `voxel51` CLI.'''

    @staticmethod
    def setup(parser):
        '''Setup the command-line arguments for the command.

        Args:
            parser: an argparse.ArgumentParser instance
        '''
        raise NotImplementedError("subclass must implement setup()")

    @staticmethod
    def run(args):
        '''Execute the command on the given args.

        args:
            args: an argparse.Namespace instance containing the arguments
                for the command
        '''
        raise NotImplementedError("subclass must implement run()")


class AuthenticationCommand(Command):
    '''Command-line tool for authentication.

    Examples:
        # Show info about the active API token
        voxel51 auth --show

        # Activate API token
        voxel51 auth --activate '/path/to/token.json'

        # Deactivate active API token, if any
        voxel51 auth --clean
    '''

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "-s", "--show", action="store_true",
            help="show info about the active API token")
        parser.add_argument(
            "-a", "--activate", help="activate the API token")
        parser.add_argument(
            "-c", "--clean", action="store_true",
            help="Deactivate active API token, if any")

    @staticmethod
    def run(args):
        # Show active token
        if args.show:
            _print_active_token_info()

        # Activate token
        if args.activate:
            voxa.activate_token(args.activate)

        # Deactivate all tokens
        if args.clean:
            voxa.deactivate_token()


class DataCommand(Command):
    '''Command-line tool for working with data.

    Examples:
        # List data
        voxel51 data --list [<num>]
            [--search [<field>:][<str>]]
            [--sort-by <field>] [--ascending]
            [--count]

        # Get info about data
        voxel51 data --info <id> [...]

        # Upload data
        voxel51 data --upload '/path/to/video.mp4' [...]

        # Download data
        voxel51 data --download <id> [--path '/path/for/video.mp4']

        # Generate signed URL to download data
        voxel51 data --download-url <id>

        # Delete data
        voxel51 data --delete <id> [...]
    '''

    @staticmethod
    def setup(parser):
        listing = parser.add_argument_group("listing arguments")
        listing.add_argument(
            "-l", "--list", nargs="?", metavar="NUM", const=-1,
            help="list number of data")
        listing.add_argument(
            "--search", metavar="[FIELD:]STR",
            help="search to limit results when listing data")
        listing.add_argument(
            "--sort-by", metavar="FIELD",
            help="field to sort by when listing data")
        listing.add_argument(
            "--ascending", action="store_true",
            help="whether to sort in ascending order")
        listing.add_argument(
            "-c", "--count", action="store_true",
            help="whether to show the number of data in the list")

        download = parser.add_argument_group("download arguments")
        download.add_argument(
            "-d", "--download", metavar="ID", help="data to download")
        download.add_argument(
            "-p", "--path", metavar="PATH", help="path to download data")

        parser.add_argument(
            "-i", "--info", nargs="+", metavar="ID",
            help="get info about data")
        parser.add_argument(
            "-u", "--upload", nargs="+", metavar="PATH", help="upload data")
        parser.add_argument(
            "--download-url", metavar="ID",
            help="generate signed URL to download data")
        parser.add_argument(
            "--delete", nargs="+", metavar="ID", help="delete data")

    @staticmethod
    def run(args):
        api = API()

        # List data
        if args.list:
            limit = int(args.list)
            sort_field = args.sort_by if args.sort_by else "upload_date"
            descending = not args.ascending
            query = (DataQuery()
                .add_all_fields()
                .sort_by(sort_field, descending=descending))
            if limit >= 0:
                query = query.set_limit(limit)
            if args.search is not None:
                query = query.add_search_direct(args.search)
            data = api.query_data(query)["data"]
            _print_data_table(data, show_count=args.count)

        # Print data details
        if args.info:
            data = [api.get_data_details(data_id) for data_id in args.info]
            _print_data_table(data)

        # Upload data
        if args.upload:
            uploads = []
            for path in args.upload:
                print("Uploading data '%s'" % path)
                data_id = api.upload_data(path)
                uploads.append({"id": data_id, "path": path})
            _print_table(uploads)

        # Download data
        if args.download:
            data_id = args.download
            output_path = args.path if args.path else None
            output_path = api.download_data(data_id, output_path=output_path)
            print("Downloaded '%s' to '%s'" % (data_id, output_path))

        # Generate data download URL
        if args.download_url:
            data_id = args.download_url
            url = api.get_data_download_url(data_id)
            print(url)

        # Delete data
        if args.delete:
            for data_id in args.delete:
                api.delete_data(data_id)
                print("Data '%s' deleted" % data_id)


class JobsCommand(Command):
    '''Command-line tool for working with jobs.

    Examples:
        # List jobs
        voxel51 jobs --list [<num>]
            [--search [<field>:][<str>]]
            [--sort-by <field>] [--ascending]
            [--count]

        # Shorthand for listing jobs in a particular state
        voxel51 jobs --ready
        voxel51 jobs --queued
        voxel51 jobs --scheduled
        voxel51 jobs --running
        voxel51 jobs --complete
        voxel51 jobs --failed

        # Get info about jobs
        voxel51 jobs --info <id> [...]

        # Upload job
        voxel51 jobs --upload '/path/to/video.mp4'
            --name <job-name> [--auto-start]

        # Start jobs
        voxel51 jobs --start <id> [...]

        # Archive jobs
        voxel51 jobs --archive <id> [...]

        # Unarchive jobs
        voxel51 jobs --unarchive <id> [...]

        # Get job request
        voxel51 jobs --request <id>

        # Get job status
        voxel51 jobs --status <id>

        # Get job logfile
        voxel51 jobs --log <id>

        # Download job output
        voxel51 jobs --download <id> [--path '/path/for/output.json']

        # Generate signed URL to download job output
        voxel51 jobs --download-url <id>

        # Kill jobs
        voxel51 jobs --kill <id> [...]

        # Delete jobs
        voxel51 jobs --delete <id> [...]
    '''

    @staticmethod
    def setup(parser):
        listing = parser.add_argument_group("listing arguments")
        listing.add_argument(
            "-l", "--list", nargs="?", metavar="NUM", const=-1,
            help="list number of jobs")
        listing.add_argument(
            "--search", metavar="[FIELD:]STR",
            help="search to limit results when listing jobs")
        listing.add_argument(
            "--sort-by", metavar="FIELD",
            help="field to sort by when listing jobs")
        listing.add_argument(
            "--ascending", action="store_true",
            help="whether to sort in ascending order")
        listing.add_argument(
            "-c", "--count", action="store_true",
            help="whether to show the number of jobs in the list")

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

        upload = parser.add_argument_group("upload arguments")
        upload.add_argument(
            "-u", "--upload", metavar="PATH", help="upload job")
        upload.add_argument(
            "-n", "--name", metavar="NAME", help="job name")
        upload.add_argument(
            "--auto-start", action="store_true",
            help="whether to automatically start job")

        download = parser.add_argument_group("download arguments")
        download.add_argument(
            "-d", "--download", metavar="ID", help="job to download")
        download.add_argument(
            "-p", "--path", metavar="PATH", help="path to download job output")

        parser.add_argument(
            "-i", "--info", nargs="+", metavar="ID",
            help="get info about jobs")
        parser.add_argument(
            "--start", nargs="+", metavar="ID", help="start jobs")
        parser.add_argument(
            "--archive", nargs="+", metavar="ID", help="archive jobs")
        parser.add_argument(
            "--unarchive", nargs="+", metavar="ID",
            help="unarchive jobs")
        parser.add_argument(
            "--request", metavar="ID", help="get request for job")
        parser.add_argument(
            "--status", metavar="ID", help="get status for job")
        parser.add_argument(
            "--log", metavar="ID", help="get logfile for job")
        parser.add_argument(
            "--download-url", metavar="ID",
            help="generate signed URL to download job output")
        parser.add_argument(
            "--delete", nargs="+", metavar="ID", help="delete jobs")
        parser.add_argument(
            "--kill", nargs="+", metavar="ID", help="kill jobs")

    @staticmethod
    def run(args):
        api = API()

        # Handle explicit state arguments
        states = []
        if args.ready:
            states.append("READY")
        elif args.queued:
            states.append("QUEUED")
        elif args.scheduled:
            states.append("SCHEDULED")
        elif args.running:
            states.append("RUNNING")
        elif args.complete:
            states.append("COMPLETE")
        elif args.failed:
            states.append("FAILED")
        if states and args.list is None:
            args.list = -1

        # List jobs
        if args.list:
            limit = int(args.list)
            sort_field = args.sort_by if args.sort_by else "upload_date"
            descending = not args.ascending
            query = (JobsQuery()
                .add_all_fields()
                .sort_by(sort_field, descending=descending))
            if limit >= 0:
                query = query.set_limit(limit)
            if states:
                query = query.add_search_or("state", states)
            if args.search is not None:
                query = query.add_search_direct(args.search)
            if args.search is None or not args.search.startswith("archived:"):
                query = query.add_search("archived", False)
            jobs = api.query_jobs(query)["jobs"]
            _print_jobs_table(jobs, show_count=args.count)

        # Print job details
        if args.info:
            jobs = [api.get_job_details(job_id) for job_id in args.info]
            _print_jobs_table(jobs)

        # Upload job
        if args.upload:
            request = JobRequest.from_json(args.upload)
            job_id = api.upload_job_request(
                request, args.name, auto_start=args.auto_start)
            print("Created job '%s'" % job_id)

        # Download job output
        if args.download:
            job_id = args.download
            output_path = args.path
            api.download_job_output(job_id, output_path)
            print("Downloaded '%s' to '%s'" % (job_id, output_path))

        # Start jobs
        if args.start:
            for job_id in args.start:
                api.start_job(job_id)
                print("Job '%s' started" % job_id)

        # Archive jobs
        if args.archive:
            for job_id in args.archive:
                api.archive_job(job_id)
                print("Job '%s' archived" % job_id)

        # Unarchive jobs
        if args.unarchive:
            for job_id in args.unarchive:
                api.unarchive_job(job_id)
                print("Job '%s' unarchived" % job_id)

        # Get job request
        if args.request:
            job_id = args.request
            request = api.get_job_request(job_id)
            print(request)

        # Get job status
        if args.status:
            job_id = args.status
            status = api.get_job_status(job_id)
            _print_dict_as_json(status)

        # Get job logfile
        if args.log:
            job_id = args.log
            logfile = api.download_job_logfile(job_id)
            print(logfile)

        # Generate job output download URL
        if args.download_url:
            job_id = args.download_url
            url = api.get_job_output_download_url(job_id)
            print(url)

        # Delete jobs
        if args.delete:
            for job_id in args.delete:
                api.delete_job(job_id)
                print("Job '%s' deleted" % job_id)

        # Kill jobs
        if args.kill:
            for job_id in args.kill:
                api.kill_job(job_id)
                print("Job '%s' killed" % job_id)


class AnalyticsCommand(Command):
    '''Command-line tool for working with analytics.

    Examples:
        # List analytics
        voxel51 analytics --list [<num>]
            [--all-versions]
            [--search [<field>:][<str>]]
            [--sort-by <field>] [--ascending]
            [--count]

        # Get analytic documentation
        voxel51 analytics --docs <id>

        # Upload documentation for analytic
        voxel51 analytics --upload-docs '/path/to/docs.json'
            [--analytic-type TYPE]

        # Upload analytic image
        voxel51 analytics --upload-image <id>
            --image-path '/path/to/image.tar.gz' --image-type cpu|gpu

        # Delete analytics
        voxel51 analytics --delete <id> [...]
    '''

    @staticmethod
    def setup(parser):
        listing = parser.add_argument_group("listing arguments")
        listing.add_argument(
            "-l", "--list", nargs="?", metavar="NUM", const=-1,
            help="list number of analytics")
        listing.add_argument(
            "-a", "--all-versions", action="store_true",
            help="whether to include all versions of analytics")
        listing.add_argument(
            "--search", metavar="[FIELD:]STR",
            help="search to limit results when listing analytics")
        listing.add_argument(
            "--sort-by", metavar="FIELD",
            help="field to sort by when listing analytics")
        listing.add_argument(
            "--ascending", action="store_true",
            help="whether to sort in ascending order")
        listing.add_argument(
            "-c", "--count", action="store_true",
            help="whether to show the number of jobs in the list")

        upload = parser.add_argument_group("upload arguments")
        upload.add_argument(
            "--upload-docs", metavar="PATH", help="analytic docs to upload")
        upload.add_argument(
            "--analytic-type", help="type of analytic")
        upload.add_argument(
            "--upload-image", metavar="ID",
            help="analytic ID to upload image for")
        upload.add_argument(
            "--image-path", metavar="PATH", help="analytic image to upload")
        upload.add_argument(
            "--image-type", help="type of image being uploaded")

        parser.add_argument(
            "-d", "--docs", metavar="ID",
            help="get documentation for analytic")
        parser.add_argument(
            "--delete", nargs="+", metavar="ID", help="delete analytics")

    @staticmethod
    def run(args):
        api = API()

        # List analytics
        if args.list:
            limit = int(args.list)
            sort_field = args.sort_by if args.sort_by else "upload_date"
            descending = not args.ascending
            all_versions = args.all_versions
            query = (AnalyticsQuery()
                .add_all_fields()
                .set_all_versions(all_versions)
                .sort_by(sort_field, descending=descending))
            if limit >= 0:
                query = query.set_limit(limit)
            if args.search is not None:
                query = query.add_search_direct(args.search)
            print(query)
            analytics = api.query_analytics(query)["analytics"]
            _print_analytics_table(analytics, show_count=args.count)

        # Upload analytic documentation
        if args.upload_docs:
            docs_path = args.upload_docs
            analytic_type = args.analytic_type
            metadata = api.upload_analytic(
                docs_path, analytic_type=analytic_type)
            _print_dict_as_table(metadata)

        # Upload analytic image
        if args.upload_image:
            analytic_id = args.upload_image
            image_tar_path = args.image_path
            image_type = args.image_type
            api.upload_analytic_image(analytic_id, image_tar_path, image_type)
            print(
                "%s image for analytic %s uploaded" %
                (image_type.upper(), analytic_id))

        # Get analytic documentation
        if args.docs:
            analytic_id = args.docs
            docs = api.get_analytic_doc(analytic_id)
            _print_dict_as_json(docs)

        # Delete analytic
        if args.delete:
            for analytic_id in args.delete:
                api.delete_analytic(analytic_id)
                print("Analytic '%s' deleted" % analytic_id)


def _print_active_token_info():
    token_path = voxa.get_active_token_path()
    token = voxa.load_token(token_path=token_path)
    contents = [
        ("id", token.id),
        ("path", token_path),
        ("creation date", token.creation_date),
    ]
    table_str = tabulate(contents, tablefmt="plain")
    print(table_str)


def _print_data_table(data, show_count=False):
    records = [
        (
            d["id"], _parse_name(d["name"]), d["size"], d["type"],
            d["upload_date"], d["expiration_date"]
        ) for d in data]

    table_str = tabulate(
        records,
        headers=[
            "id", "name", "size bytes", "type", "upload date",
            "expiration date"],
        tablefmt=TABLE_FORMAT)

    print(table_str)
    if show_count:
        print("\nFound %d data\n" % len(records))


def _print_jobs_table(jobs, show_count=False):
    records = [
        (
            j["id"], _parse_name(j["name"]), j["state"], j["archived"],
            j["upload_date"], j["expiration_date"]
        ) for j in jobs]

    table_str = tabulate(
        records,
        headers=[
            "id", "name", "state", "archived", "upload date",
            "expiration date"],
        tablefmt=TABLE_FORMAT)

    print(table_str)
    if show_count:
        print("\nFound %d jobs\n" % len(records))


def _print_analytics_table(analytics, show_count=False):
    records = [
        (
            a["id"], a["name"], a["version"], a["scope"],
            bool(a["supports_cpu"]), bool(a["supports_gpu"]),
            bool(a["pending"]), a["upload_date"],
        ) for a in analytics]

    table_str = tabulate(
        records,
        headers=[
            "id", "name", "version", "type", "supports cpu", "supports gpu",
            "pending", "upload date"],
        tablefmt=TABLE_FORMAT)

    print(table_str)
    if show_count:
        print("\nFound %d analytics\n" % len(records))


def _print_table(records):
    table_str = tabulate(records, headers="keys", tablefmt=TABLE_FORMAT)
    print(table_str)


def _print_dict_as_json(d):
    s = json.dumps(d, indent=4)
    print(s)


def _print_dict_as_table(d):
    contents = list(d.items())
    table_str = tabulate(contents, tablefmt="plain")
    print(table_str)


def _parse_name(name):
    if len(name) > MAX_NAME_COLUMN_WIDTH:
        name = name[:(MAX_NAME_COLUMN_WIDTH - 4)] + " ..."
    return name


def _register_command(cmd, cls):
    parser = subparsers.add_parser(
        cmd, help=cls.__doc__.splitlines()[0],
        description=cls.__doc__.rstrip(),
        formatter_class=argparse.RawTextHelpFormatter)
    parser.set_defaults(run=cls.run)
    cls.setup(parser)


# Main setup
parser = argparse.ArgumentParser(
    description="Voxel51 Platform API command-line interface.")
parser.add_argument(
    "-v", "--version", action="version", version="0.1.0",
    help="show version info")
subparsers = parser.add_subparsers(title="available commands")


# Register commands
_register_command("auth", AuthenticationCommand)
_register_command("data", DataCommand)
_register_command("jobs", JobsCommand)
_register_command("analytics", AnalyticsCommand)


def main():
    '''Executes the `voxel51` tool with the given command-line args.'''
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    args.run(args)
