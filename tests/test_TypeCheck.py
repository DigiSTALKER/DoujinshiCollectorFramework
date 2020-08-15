# -*- coding: utf-8 -*-
# @Time    : 2020/6/13 15:55
# @Author  : Hochikong
# @FileName: test_TypeCheck.py
import pytest

from djscollect.TypeCheck import *


@parameters_type_check
def foo(num: int) -> str:
    return str(num)


@parameters_type_check
def foo1(num: int, desc: str) -> str:
    return str(num) + ":" + desc


@parameters_type_check
def foo2(desc: str, contents: list) -> str:
    return desc + ":" + ''.join(contents)


class People:
    @c_parameters_type_check
    def __init__(self, name: str):
        self.name = name


def test_foo():
    for i in range(10):
        assert foo(i) == str(i)

    with pytest.raises(TypeError) as excinfo:
        foo('s')

    assert "Parameter `num` require type <class 'int'>" in str(excinfo.value)
    assert excinfo.type is TypeError


def test_foo1():
    num = range(5)
    desc = ['a', 'b', 'c', 'd', 'e']
    for i in num:
        assert foo1(num=i, desc=desc[i])

    with pytest.raises(TypeError) as excinfo:
        foo1('s', 1)
    assert "Parameter `num` require type <class 'int'>" in str(excinfo.value)
    assert excinfo.type is TypeError

    with pytest.raises(TypeError) as excinfo:
        foo1(1, 1)
    assert "Parameter `desc` require type <class 'str'>" in str(excinfo.value)
    assert excinfo.type is TypeError


def test_foo2():
    assert foo2('a', ['a', 'b']) == 'a:ab'

    with pytest.raises(TypeError) as excinfo:
        foo2('a', 1)

    assert "Parameter `contents` require type <class 'list'>" in str(
        excinfo.value)
    assert excinfo.type is TypeError


def test_people():
    with pytest.raises(TypeError) as excinfo:
        p = People(1)

    assert "Parameter `name` require type <class 'str'>"
    assert excinfo.type is TypeError
