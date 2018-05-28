'''
Job request creation and manipulation library for the Voxel51 Vision Services
API.

Copyright 2017-2018, Voxel51, LLC
voxel51.com
'''
import voxel51.utils as voxu


DATA_ID_FIELD = "data-id"
SIGNED_URL_FIELD = "signed-url"


class JobRequest(voxu.Serializable):
    '''Class encapsulating a job request for the API.

    Attributes:
        analytic (str): the ID of the analytic to run
        inputs (dict): a dictionary mapping input names to RemoteDataPath
            instances
        parameters (dict): a dictionary mapping parameter names to values
    '''

    def __init__(self, analytic_id):
        '''Initializes a JobRequest instance for the given analytic.

        Args:
            analytic_id (str): the ID of the analytic to run
        '''
        self.analytic = analytic_id
        self.inputs = {}
        self.parameters = {}

    def set_input(self, name, path=None, **kwargs):
        '''Sets the input of the given name.

        The input value can be specified either as a RemoteDataPath instance
        or as valid keyword arguments to construct one.

        Args:
            name (str): the input name to set
            path (RemoteDataPath): a RemoteDataPath instance. If not specified,
                valid kwargs must be provided
            **kwargs: valid argument(s) for RemoteDataPath()
        '''
        self.inputs[name] = path or RemoteDataPath(**kwargs)

    def set_data_parameter(self, name, path=None, **kwargs):
        '''Sets the data parameter of the given name.

        Data parameters are parameters that are defined by a RemoteDataPath
        instance and are read from cloud storage at runtime by the Vision
        Engine. The parameter can be specified either as a RemoteDataPath
        instance or as valid keyword arguments to construct one.

        Args:
            name (str): the input name to set
            path (RemoteDataPath): a RemoteDataPath instance. If not specified,
                valid kwargs must be provided
            **kwargs: valid argument(s) for RemoteDataPath()
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
        job_request = cls(d["analytic"])

        # Set inputs
        for name, val in d["inputs"].items():
            job_request.set_input(name, path=RemoteDataPath.from_dict(val))

        # Set parameters
        for name, val in d["parameters"].items():
            if RemoteDataPath.is_remote_path_dict(val):
                # Data parameter
                job_request.set_data_parameter(
                    name, path=RemoteDataPath.from_dict(val))
            else:
                # Non-data parameter
                job_request.set_parameter(name, val)
        return job_request


class RemoteDataPath(voxu.Serializable):
    '''Class enapsulating a remote data path.

    Attributes:
        data_id (str): the ID of the data in cloud storage
        signed_url (str): a signed URL with access to the data of interest
            in third-party cloud storage
    '''

    def __init__(self, data_id=None, signed_url=None):
        '''Creates a RemoteDataPath instance defined by the given information.

        Exactly one keyword value must be supplied to this constructor.

        Args:
            data_id (str): the ID of the data in cloud storage
            signed_url (str): a signed URL with access to the data of interest
                in third-party cloud storage

        Raises:
            RemoteDataPathError if the instance creation failed
        '''
        self.data_id = data_id
        self.signed_url = signed_url
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

    @classmethod
    def from_signed_url(cls, signed_url):
        '''Creates a RemoteDataPath instance defined by the given signed URL.

        Args:
            signed_url (str): a signed URL with access to the data of interest
                in third-party cloud storage

        Returns:
            a RemoteDataPath instance with the given signed URL
        '''
        return cls(signed_url=signed_url)

    @property
    def has_data_id(self):
        '''Determines whether this RemoteDataPath instance has a data ID.

        Returns:
            True if this instance has a data ID, and False otherwise
        '''
        return self.data_id is not None

    @property
    def has_signed_url(self):
        '''Determines whether this RemoteDataPath instance has a signed URL.

        Returns:
            True if this instance has a signed URL, and False otherwise
        '''
        return self.signed_url is not None

    @property
    def is_valid(self):
        '''Determines whether this RemoteDataPath instance is valid.

        Returns:
            True if this instance is valid, and False otherwise
        '''
        return self.has_data_id ^ self.has_signed_url

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
        return (
            isinstance(val, dict) and RemoteDataPath.from_dict(val).is_valid
        )

    @classmethod
    def from_dict(cls, d):
        '''Constructs a RemoteDataPath instance from a JSON dictionary.

        Args:
            d (dict): a JSON dictionary defining a RemoteDataPath instance

        Returns:
            a RemoteDataPath instance
        '''
        if DATA_ID_FIELD in d:
            return cls(data_id=d[DATA_ID_FIELD])
        elif SIGNED_URL_FIELD in d:
            return cls(signed_url=d[SIGNED_URL_FIELD])
        raise RemoteDataPathError("Invalid RemoteDataPath dict: %s" % str(d))

    def _attributes(self):
        if self.has_data_id:
            return {"data_id": DATA_ID_FIELD}
        elif self.has_signed_url:
            return {"signed_url": SIGNED_URL_FIELD}
        raise RemoteDataPathError("Invalid RemoteDataPath")


class RemoteDataPathError(Exception):
    pass
