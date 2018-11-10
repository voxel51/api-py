'''
Query interface for the Voxel51 Vision Services API.

| Copyright 2017-2018, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
'''

try:
    from urllib.parse import urlencode  # Python 3
except ImportError:
    from urllib import urlencode  # Python 2


class BaseQuery(object):
    '''Base class for API queries.

    Provides support for queries with fully-customizable return fields,
    sorting, substring searching, and record limits.

    Attributes:
        fields (list): the list of fields to include in the returned records
        search (list): a list of `field:search_str` search strings to apply
        sort (str): a `field:asc/desc` string describing a sorting scheme
        limit (int): the maximum number of records to return
    '''

    def __init__(self, supported_fields):
        self._supported_fields = supported_fields
        self.fields = []
        self.search = []
        self.sort = None
        self.limit = None

    def __str__(self):
        return self.to_string()

    def add_field(self, field):
        if self._is_supported_field(field):
            self.fields.append(field)
        return self

    def add_fields(self, fields):
        for field in fields:
            self.add_field(field)
        return self

    def add_all_fields(self):
        this.add_fields(self._supported_fields)
        return self

    def add_search(self, field, search_str):
        if self._is_supported_field(field):
            this.search.append("%s:%s" % (field, search_str))
        return self

    def sort_by(self, field, descending=True):
        if self._is_supported_field(field):
            self.sort = "%s:%s" % (field, "desc" if descending else "asc")
        return self

    def set_limit(self, limit):
        if isinstance(limit, int) and limit > 0:
            self.limit = limit
        return self

    def to_dict(self):
        obj = {}
        for key in vars(self):
            val = getattr(self, key)
            if not key.startswith("_") and val:
                obj[key] = val
        return obj

    def to_string(self):
        return urlencode(self.to_dict())

    def _is_supported_field(self, field):
        return field in self._supported_fields


class AnalyticsQuery(BaseQuery):
    '''Class representing an analytics query for the API.

    Provides support for queries with fully-customizable return fields,
    sorting, substring searching, and record limits.

    Attributes:
        fields (list): the list of fields to include in the returned records
        search (list): a list of `field:search_str` search strings to apply
        sort (str): a `field:asc/desc` string describing a sorting scheme
        limit (int): the maximum number of records to return
    '''

    def __init__(self):
        super(AnalyticsQuery, self).__init__(
            ["id", "name", "description", "date"])


class DataQuery(BaseQuery):
    '''Class representing a data query for the API.

    Provides support for queries with fully-customizable return fields,
    sorting, substring searching, and record limits.

    Attributes:
        fields (list): the list of fields to include in the returned records
        search (list): a list of `field:search_str` search strings to apply
        sort (str): a `field:asc/desc` string describing a sorting scheme
        limit (int): the maximum number of records to return
    '''

    def __init__(self):
        super(DataQuery, self).__init__(
            ["id", "name", "encoding", "type", "size", "date", "expires"])


class JobsQuery(BaseQuery):
    '''Class representing a jobs query for the API.

    Provides support for queries with fully-customizable return fields,
    sorting, substring searching, and record limits.

    Attributes:
        fields (list): the list of fields to include in the returned records
        search (list): a list of `field:search_str` search strings to apply
        sort (str): a `field:asc/desc` string describing a sorting scheme
        limit (int): the maximum number of records to return
    '''

    def __init__(self):
        super(JobsQuery, self).__init__(
            ["id", "name", "state", "archived", "date"])

