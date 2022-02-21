"""Provide DataFrameGroupBy and DataFrameRowwise"""
from typing import Union
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

from .types import StringOrIter


class DatarGroupBy(DataFrame):
    """A DataFrameGroupBy wrapper with

    1. classmethod `from_groupby()` to make a clone from another
    `DataFrameGroupBy` object
    2. attributes `_html_footer` and `_str_footer` for `pdtypes` to show
    additional information
    3. attribute `_group_vars` is added to keep after `summarise()` for
    rowwise data frame. If not rowwise, they are `grouper.names`
    4. getattr()/getitem() returns a SeriesGroupBy object
    """

    @property
    def _constructor(self):
        return DatarGroupBy

    @classmethod
    def from_groupby(
        cls,
        grouped: Union[DataFrameGroupBy, "DatarGroupBy"],
        group_vars: StringOrIter = None,
    ) -> "DatarGroupBy":
        """Initiate a DatarGroupBy object"""
        if isinstance(grouped, DataFrameGroupBy):
            out = cls(grouped.obj)
            out.attrs["_grouped"] = grouped
            out.attrs["_group_vars"] = group_vars or [
                name for name in grouped.grouper.names if name is not None
            ]
            out.attrs["_html_footer"] = (
                f"<p>Groups: {', '.join(out.attrs['_group_vars'])} "
                f"(n={grouped.grouper.ngroups})</p>"
            )
            out.attrs["_str_footer"] = (
                f"[Groups: {', '.join(out.attrs['_group_vars'])} "
                f"(n={grouped.grouper.ngroups})]"
            )
        else:
            out = cls(grouped)
            out.attrs["_grouped"] = grouped.attrs["_grouped"]
            out.attrs["_group_vars"] = grouped.attrs["_group_vars"]
            out.attrs["_html_footer"] = grouped.attrs["_html_footer"]
            out.attrs["_str_footer"] = grouped.attrs["_str_footer"]

        return out

    def copy(self, deep: bool = True) -> "DatarGroupBy":
        """Make a copy of DatarGroupBy object

        If deep is True, also copy the grouped object (use the grouper object
        to redo the groupby)
        """
        if "_grouepd" not in self.attrs:
            return super().copy(deep=deep)

        if not deep:
            # attrs also copyied
            return self.__class__.from_groupby(self)

        out = self.attrs["_grouped"].obj.copy()
        out = out.groupby(
            self.attrs["_grouped"].grouper,
            observed=self.attrs["_grouped"].observed,
            sort=self.attrs["_grouped"].sort,
        )
        return self.__class__.from_groupby(out, self.attrs["_group_vars"][:])


class DatarRowwise(DatarGroupBy):
    """Rowwise data frame"""

    @property
    def _constructor(self):
        return DatarRowwise

    @classmethod
    def from_groupby(
        cls,
        grouped: Union[DataFrameGroupBy, "DatarRowwise"],
        group_vars: StringOrIter = None,
    ) -> "DatarGroupBy":
        """Initiate a DatarGroupBy object"""
        if isinstance(grouped, DataFrameGroupBy):
            out = cls(grouped.obj)
            out.attrs["_grouped"] = grouped
            out.attrs["_group_vars"] = group_vars or []
            out.attrs["_html_footer"] = (
                f"<p>Rowwise: {', '.join(out.attrs['_group_vars'])} "
                f"(n={out.shape[0]})</p>"
            )
            out.attrs["_str_footer"] = (
                f"[Rowwise: {', '.join(out.attrs['_group_vars'])} "
                f"(n={out.shape[0]})]"
            )
        else:
            out = super().from_groupby(grouped, group_vars)

        return out
