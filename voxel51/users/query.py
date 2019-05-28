'''
Query interface for the Voxel51 Platform API.

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

try:
    from urllib.parse import urlencode  # Python 3
except ImportError:
    from urllib import urlencode  # Python 2


class BaseQuery(object):
    '''Base class for API queries.

    Provides support for queries with fully-customizable return fields,
    sorting, substring searching, and record offset/limits.

    Attributes:
        fields (list): the list of fields to include in the returned records
        search (list): a list of `field:search_str` search strings to apply
        sort (str): a `field:asc/desc` string describing a sorting scheme
        offset (int): an offset index for the returned records list
        limit (int): the maximum number of records to return
    '''

    def __init__(self, supported_fields):
        self._supported_fields = supported_fields
        self.fields = []
        self.search = []
        self.sort = None
        self.offset = None
        self.limit = None

    def __str__(self):
        return self.to_str()

    def add_field(self, field):
        '''Adds the given field to the query.

        Args:
            field (str): a query field to add

        Returns:
            the updated query instance
        '''
        if self._is_supported_field(field):
            self.fields.append(field)
        return self

    def add_fields(self, fields):
        '''Adds the given fields to the query.

        Args:
            field (list): a list of query fields to add

        Returns:
            the updated query instance
        '''
        for field in fields:
            self.add_field(field)
        return self

    def add_all_fields(self):
        '''Adds all supported fields to the query.

        Returns:
            the updated query instance
        '''
        self.add_fields(self._supported_fields)
        return self

    def add_search(self, field, search_str):
        '''Adds the given search to the query.

        Args:
            field (str): the query field on which to search
            search_str (str): the search string

        Returns:
            the updated query instance
        '''
        if self._is_supported_field(field):
            self.search.append("%s:%s" % (field, search_str))
        return self

    def add_search_or(self, field, search_strs):
        '''Adds the given "OR" search to the query.

        Args:
            field (str): the query field on which to search
            search_strs (list): a list of search strings to form an "or" query

        Returns:
            the updated query instance
        '''
        return self.add_search(field, "|".join(search_strs))

    def sort_by(self, field, descending=True):
        '''Adds the given search to the query.

        Args:
            field (str): the field on which to sort
            descending (bool, optional): whether to sort in descending order

        Returns:
            the updated query instance
        '''
        if self._is_supported_field(field):
            self.sort = "%s:%s" % (field, "desc" if descending else "asc")
        return self

    def set_offset(self, offset):
        '''Sets the record offset of the query.

        Args:
            offset (int): the desired record offset

        Returns:
            the updated query instance
        '''
        if isinstance(offset, int) and offset >= 0:
            self.offset = offset
        return self

    def set_limit(self, limit):
        '''Sets the record limit of the query.

        Args:
            limit (int): the desired record limit

        Returns:
            the updated query instance
        '''
        if isinstance(limit, int) and limit > 0:
            self.limit = limit
        return self

    def to_dict(self):
        '''Converts the query instance into a dict suitable for passing to the
        `requests` package.

        Returns:
            the query dict
        '''
        obj = {}
        for key in vars(self):
            val = getattr(self, key)
            if not key.startswith("_") and val:
                obj[key] = val
        return obj

    def to_str(self):
        '''Converts the query instance into a string.

        Returns:
            the query string
        '''
        return urlencode(self.to_dict())

    def _is_supported_field(self, field):
        return field in self._supported_fields


class AnalyticsQuery(BaseQuery):
    '''Class representing an analytics query for the API.

    Provides support for queries with fully-customizable return fields,
    sorting, substring searching, and record offset/limits.

    Attributes:
        fields (list): the list of fields to include in the returned records.
            The supported query fields are `id`, `name`, `version`,
            `upload_date`, `description`, `scope`, `supports_cpu`,
            `supports_gpu`, and `pending`
        search (list): a list of `field:search_str` search strings to apply
        sort (str): a `field:asc/desc` string describing a sorting scheme
        offset (int): an offset index for the returned records list
        limit (int): the maximum number of records to return
        all_versions (bool): whether to include all versions of each analytic
            in the query response. By default, this is False
    '''

    def __init__(self):
        '''Initializes an AnalyticsQuery instance.'''
        super(AnalyticsQuery, self).__init__([
            "id", "name", "version", "upload_date", "description",
            "scope", "supports_cpu", "supports_gpu", "pending"])
        self.all_versions = False

    def set_all_versions(self, all_versions):
        '''Sets the `all_versions` parameter of the query.

        Args:
            all_versions (bool): whether to include all versions of each
                analytic in the query

        Returns:
            the updated query instance
        '''
        self.all_versions = all_versions
        return self


class DataQuery(BaseQuery):
    '''Class representing a data query for the API.

    Provides support for queries with fully-customizable return fields,
    sorting, substring searching, and record offset/limits.

    Attributes:
        fields (list): the list of fields to include in the returned records.
            The supported query fields are `id`, `name`, `encoding`, `type`,
            `size`, `upload_date`, and `expires`
        search (list): a list of `field:search_str` search strings to apply
        sort (str): a `field:asc/desc` string describing a sorting scheme
        offset (int): an offset index for the returned records list
        limit (int): the maximum number of records to return
    '''

    def __init__(self):
        '''Initializes a DataQuery instance.'''
        super(DataQuery, self).__init__([
            "id", "name", "encoding", "type", "size", "upload_date",
            "expiration_date"])


class JobsQuery(BaseQuery):
    '''Class representing a jobs query for the API.

    Provides support for queries with fully-customizable return fields,
    sorting, substring searching, and record offset/limits.

    Attributes:
        fields (list): the list of fields to include in the returned records.
            The supported query fields are `id`, `name`, `state`, `archived`,
            `upload_date`, `analytic_id`, `auto_start`, `compute_mode`,
            `start_date`, `completion_date`, `fail_date`, and `failure_type`
        search (list): a list of `field:search_str` search strings to apply
        sort (str): a `field:asc/desc` string describing a sorting scheme
        offset (int): an offset index for the returned records list
        limit (int): the maximum number of records to return
    '''

    def __init__(self):
        '''Initializes a JobsQuery instance.'''
        super(JobsQuery, self).__init__([
            "id", "name", "state", "archived", "upload_date", "analytic_id",
            "auto_start", "compute_mode", "start_date", "completion_date",
            "fail_date", "failure_type"])
