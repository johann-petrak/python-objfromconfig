#!/usr/bin/env python

"""Tests for `objfromconfig` package."""

from typing import Any
from objfromconfig.objfromconfig import ObjFromConfig


class C1(ObjFromConfig):
    def __init__(self, a: Any, *b: Any, x: Any = 1, v: Any = 2, **kwargs):
        print(locals())
        self.store_config(locals())
        self.a = a
        self.b = b
        self.x = x
        self.v = v
        self.kwargs = kwargs

    def __eq__(self, other):
        if not isinstance(other, C1):
            return False
        if self.a == other.a and self.b == other.b and self.x == other.x \
                and self.v == other.v and self.kwargs == other.kwargs:
            return True
        return False


def test_basic():
    """Test basic functionality"""
    c1 = C1(12, 13, 14)
    conf = c1.get_config()
    c1new = ObjFromConfig.from_config(conf)
    assert isinstance(c1new, C1)
    assert c1 == c1new


def test_recursive():
    """Test recursive creation"""
    c1 = C1(12, 13, 14)
    c2 = C1("x", x=c1)
    conf = c2.get_config()
    print("\n!!!!!!!!!! conf=", conf)
    c2new = ObjFromConfig.from_config(conf)
    assert isinstance(c2new, C1)
    assert c2 == c2new
