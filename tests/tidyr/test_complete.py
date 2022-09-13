# tests grabbed from:
# https://github.com/tidyverse/tidyr/blob/HEAD/tests/testthat/test-complete.R
import pytest  # noqa
from datar.core.backends.pandas.testing import assert_frame_equal
from datar.datasets import mtcars
from datar import f
from datar.base import c, NA, nrow, ncol, factor, NULL
from datar.dplyr import group_by, group_vars
from datar.tidyr import complete
from datar.tibble import tibble

from ..conftest import assert_iterable_equal

def test_complete_with_no_vars_return_data_asis():
    assert_frame_equal(complete(mtcars), mtcars)

def test_basic_invocation_works():
    df = tibble(x=c[1:3], y=c[1:3], z=c[3:5])
    out = complete(df, f.x, f.y)
    assert nrow(out) == 4
    assert_iterable_equal(out.z, [3, NA, NA, 4])

def test_preserves_grouping():
    df = tibble(x=c[1:3], y=c[1:3], z=c[3:5]) >> group_by(f.x)
    out = complete(df, f.x, f.y)
    assert group_vars(out) == group_vars(df)

def test_expands_empty_factors():
    ff = factor(levels=c("a", "b", "c"))
    df = tibble(one=ff, two=ff)
    compl = complete(df, f.one, f.two)
    assert nrow(compl) == 9
    assert ncol(compl) == 2

def test_empty_expansion_returns_original():
    df = tibble(x=[])
    rs = complete(df, y=NULL)
    assert_frame_equal(rs, df)

    df = tibble(x=c[1:4])
    rs = complete(df, y=NULL)
    assert_frame_equal(rs, df)

def test_not_drop_unspecified_levels_in_complete():
    df = tibble(
        x=c[1:4],
        y=c[1:4],
        z=c("a", "b", "c")
    )
    df2 = df >> complete(z=c("a", "b"))

    exp = df[['z', 'x', 'y']]
    assert_frame_equal(df2, exp)
