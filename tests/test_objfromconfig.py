#!/usr/bin/env python

"""Tests for `objfromconfig` package."""

import pytest
from objfromconfig.objfromconfig import ObjFromConfig

class C1(ObjFromConfig):
    def __init__(self, a, *b, x=1, v=2, **kwargs):
        print(locals())
        self.store_config(locals())
        self.a = a
        self.b = b
        self.x = x
        self.v = v
        self.kwargs = kwargs


def test_content():
    """Test basic functionality"""
    c1 = C1(12, 13, 14)
    conf = c1.get_config()
    c1new = ObjFromConfig.from_config(conf)
    assert isinstance(c1new, C1)
    assert c1.a == c1new.a

