'''
Job request creation and manipulation library for the Voxel51 Platform API.

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

from collections import OrderedDict

import voxel51.users.utils as voxu


DATA_ID_FIELD = "data-id"


class JobComputeMode(object):
    '''Enum describing the possible compute modes of a job.'''

    CPU = "CPU"
    GPU = "GPU"
    BEST = "BEST"


class JobState(object):
    '''Enum describing the possible states of a job.'''

    READY = "READY"
    QUEUED = "QUEUED"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class JobFailureType(object):
    '''Enum describing the possible failure types of a job.'''

    USER = "USER"
    ANALYTIC = "ANALYTIC"
    PLATFORM = "PLATFORM"
    NONE = "NONE"


class JobExecutionError(Exception):
    '''Error raised when there is a problem with the execution of a job.'''
    pass


class JobRequest(voxu.Serializable):
    '''Class encapsulating a job request for the API.

    Attributes:
        analytic (str): the name of the analytic to run
        version (str): the version of the analytic to run
        compute_mode (JobComputeMode): the compute mode for the job
        inputs (dict): a dictionary mapping input names to
            :class:`voxel51.users.utils.RemoteDataPath` instances
        parameters (dict): a dictionary mapping parameter names to values
    '''

    def __init__(self, analytic, version=None, compute_mode=None):
        '''Creates a JobRequest instance.

        Args:
            analytic (str): the name of the analytic to run
            version (str, optional): the version of the analytic to run. If not
                specified, the latest available version is used
            compute_mode (JobComputeMode, optional): the compute mode to use
                for the job. By default, JobComputeMode.BEST is used
        '''
        self.analytic = analytic
        self.version = version
        self.compute_mode = compute_mode
        self.inputs = {}
        self.parameters = {}

    def set_input(self, name, path=None, **kwargs):
        '''Sets the input of the given name.

        The input value can be specified either as a
        :class:`voxel51.users.utils.RemoteDataPath` instance or as valid
        keyword arguments to construct one.

        Args:
            name (str): the input name to set
            path (RemoteDataPath, optional): a
                :class:`voxel51.users.utils.RemoteDataPath` instance. If not
                specified, valid kwargs must be provided
            **kwargs: valid constructor argument(s) for
                :class:`voxel51.users.utils.RemoteDataPath`
        '''
        self.inputs[name] = path or RemoteDataPath(**kwargs)

    def set_data_parameter(self, name, path=None, **kwargs):
        '''Sets the data parameter of the given name.

        Data parameters are parameters that are defined by a
        :class:`voxel51.users.utils.RemoteDataPath` instance and are read from
        cloud storage at runtime by the job. The parameter can be specified
        either as a :class:`voxel51.users.utils.RemoteDataPath` instance or as
        valid keyword arguments to construct one.

        Args:
            name (str): the input name to set
            path (RemoteDataPath, optional): a RemoteDataPath instance. If not
                specified, valid kwargs must be provided
            **kwargs: valid constructor argument(s) for
                :class:`voxel51.users.utils.RemoteDataPath`
        '''
        self.parameters[name] = path or RemoteDataPath(**kwargs)

    def set_parameter(self, name, val):
        '''Sets the (non-data) parameter of the given name.

        Non-data parameters are parameters whose values are defined directly by
        a value that is JSON serializable.

        Args:
            name (str): the input name to set
            val: the parameter value, which must be JSON serializable
        '''
        self.parameters[name] = val

    @classmethod
    def from_dict(cls, d):
        '''Constructs a JobRequest instance from a JSON dictionary.

        Args:
            d (dict): a JSON dictionary defining a JobRequest instance

        Returns:
            a JobRequest instance
        '''
        analytic = d.get("analytic", None)
        version = d.get("version", None)
        compute_mode = d.get("compute_mode", None)
        job_request = cls(analytic, version=version, compute_mode=compute_mode)

        # Set inputs
        for name, val in iteritems(d.get("inputs", {})):
            job_request.set_input(name, path=RemoteDataPath.from_dict(val))

        # Set parameters
        for name, val in iteritems(d.get("parameters", {})):
            if RemoteDataPath.is_remote_path_dict(val):
                # Data parameter
                job_request.set_data_parameter(
                    name, path=RemoteDataPath.from_dict(val))
            else:
                # Non-data parameter
                job_request.set_parameter(name, val)

        return job_request

    def _attributes(self):
        attrs = OrderedDict()
        attrs["analytic"] = "analytic"
        if self.version is not None:
            attrs["version"] = "version"
        if self.compute_mode is not None:
            attrs["compute_mode"] = "compute_mode"
        attrs["inputs"] = "inputs"
        attrs["parameters"] = "parameters"
        return attrs


class RemoteDataPath(voxu.Serializable):
    '''Class enapsulating a remote data path.

    Attributes:
        data_id (str): the ID of the data in cloud storage
    '''

    def __init__(self, data_id=None):
        '''Creates a RemoteDataPath instance.

        Args:
            data_id (str): the ID of the data in cloud storage

        Raises:
            :class:`RemoteDataPathError` if the instance creation failed
        '''
        self.data_id = data_id
        if not self.is_valid:
            raise RemoteDataPathError("Invalid RemoteDataPath")

    @classmethod
    def from_data_id(cls, data_id):
        '''Creates a RemoteDataPath instance defined by the given data ID.

        Args:
            data_id (str): the ID of the data in cloud storage

        Returns:
            a RemoteDataPath instance with the given data ID
        '''
        return cls(data_id=data_id)

    @property
    def has_data_id(self):
        '''Determines whether this RemoteDataPath instance has a data ID.

        Returns:
            True if this instance has a data ID, and False otherwise
        '''
        return self.data_id is not None

    @property
    def is_valid(self):
        '''Determines whether this RemoteDataPath instance is valid.

        Returns:
            True if this instance is valid, and False otherwise
        '''
        return self.has_data_id

    @staticmethod
    def is_remote_path_dict(val):
        '''Determines whether the given value defines a valid RemoteDataPath
        dictionary.

        Args:
            val: either a JSON dictionary representation of a RemoteDataPath
                instance or another arbitrary value

        Returns:
            True if val is a valid RemoteDataPath JSON dictionary, and False
            otherwise
        '''
        try:
            RemoteDataPath.from_dict(val)
            return True
        except:
            return False

    @classmethod
    def from_dict(cls, d):
        '''Constructs a RemoteDataPath instance from a JSON dictionary.

        Args:
            d (dict): a JSON dictionary defining a RemoteDataPath instance

        Returns:
            a RemoteDataPath instance

        Raises:
            :class:`RemoteDataPathError` if the instance creation failed
        '''
        if DATA_ID_FIELD in d:
            return cls.from_data_id(d[DATA_ID_FIELD])
        raise RemoteDataPathError("Invalid RemoteDataPath dict: %s" % str(d))

    def _attributes(self):
        if self.has_data_id:
            return {"data_id": DATA_ID_FIELD}
        raise RemoteDataPathError("Invalid RemoteDataPath")


class RemoteDataPathError(Exception):
    '''Error raised when an invalid :class:`RemoteDataPath` instance is
    found.
    '''
    pass
