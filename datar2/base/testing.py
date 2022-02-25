"""Testing functions in R"""

# all_equal, all_equal_numeric, ...
# all, any
# is_true, is_false
# is_finite, is_infinite, is_nan
# is_function, is_atomic, is_vector, is_array, is_character, is_complex,
# is_data_frame, is_double, is_element, (is_factor, is_ordered in base.factor)
# is_integer, is_list, is_logical, is_numeric
# is_unsorted, (is_qr in base.qr)
import builtins
from typing import Any, Callable, Iterable, Sequence, Type, Union

import numpy as np
from pandas.api.types import is_scalar
from pandas.core.groupby import GroupBy
from pandas.core.generic import NDFrame
from pandas.api.types import (
    is_integer_dtype,
    is_float_dtype,
    is_numeric_dtype,
)
from pipda import register_func

from ..core.contexts import Context

TypeOrSeq = Union[Type, Sequence[Type]]
BoolOrSeq = Union[bool, Sequence[bool]]


def _register_type_testing(
    name: str,
    scalar_types: TypeOrSeq,
    dtype_checker: Callable[[Iterable], bool],
    doc: str = "",
) -> Callable:
    """Register type testing function"""

    @register_func(None, context=Context.EVAL)
    def _testing(x: Any) -> bool:
        """Type testing"""
        if is_scalar(x):
            return isinstance(x, scalar_types)
        if hasattr(x, "dtype"):
            return dtype_checker(x)
        return all(isinstance(elem, scalar_types) for elem in x)

    _testing.__name__ = name
    _testing.__doc__ = doc
    return _testing


is_numeric = _register_type_testing(
    "is_numeric",
    scalar_types=(int, float, complex, np.number),
    dtype_checker=is_numeric_dtype,
    doc="""Test if a value is numeric

    Args:
        x: The value to be checked

    Returns:
        True if the value is numeric; with a numeric dtype;
        or all elements are numeric
    """,
)

is_integer = _register_type_testing(
    "is_integer",
    scalar_types=(int, np.integer),
    dtype_checker=is_integer_dtype,
    doc="""Test if a value is integers

    Alias `is_int`

    Args:
        x: The value to be checked

    Returns:
        True if the value is an integer or integers; False otherwise.
    """,
)

is_int = is_integer

is_double = _register_type_testing(
    "is_double",
    scalar_types=(float, np.float_),
    dtype_checker=is_float_dtype,
    doc="""Test if a value is integers

    Alias `is_float`

    Args:
        x: The value to be checked

    Returns:
        True if the value is an integer or integers; False otherwise.
    """,
)

is_float = is_double


@register_func(None, context=Context.EVAL)
def is_atomic(x: Any) -> bool:
    """Check if x is an atomic or scalar value

    Args:
        x: The value to be checked

    Returns:
        True if x is atomic otherwise False
    """
    return is_scalar(x)


@register_func(None, context=Context.EVAL)
def is_element(x: Any, elems: Iterable[Any]) -> BoolOrSeq:
    """R's `is.element()` or `%in%`.

    Alias `is_in()`

    We can't do `a %in% b` in python (`in` behaves differently), so
    use this function instead
    """
    if isinstance(x, GroupBy):
        return x.transform(np.in1d, ar2=elems)
    if isinstance(x, NDFrame):
        return x.isin(elems)

    out = np.in1d(x, elems)
    if is_scalar(out):
        return bool(out)
    return out


is_in = is_element


all = register_func(None, context=Context.EVAL)(
    # can't set attributes to builtins.all, so wrap it.
    lambda arg: builtins.all(arg)
)
any = register_func(None, context=Context.EVAL)(
    lambda arg: builtins.any(arg)
)
