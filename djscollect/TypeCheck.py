# -*- coding: utf-8 -*-
# @Time    : 2020/6/13 15:14
# @Author  : Hochikong
# @FileName: TypeCheck.py

import inspect
from typing import Callable


def parameters_type_check(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Callable:
        annotations = inspect.getmembers(func)[0][1]

        if len(annotations) > 0:
            if len(args) > 0:
                for index, arg in enumerate(args):
                    parameter_name = list(annotations.keys())[index]
                    data_type = annotations[list(annotations.keys())[index]]
                    if not isinstance(arg, data_type):
                        raise TypeError(
                            "Parameter `{}` require type {}.".format(
                                parameter_name, data_type))

            if len(kwargs) > 0:
                for key in kwargs:
                    data_type = annotations[key]
                    if not isinstance(kwargs[key], data_type):
                        raise TypeError(
                            "Parameter {} require type {}.".format(
                                key, data_type))

        return func(*args, **kwargs)

    return wrapper


def c_parameters_type_check(func: Callable) -> Callable:
    def wrapper(self, *args, **kwargs) -> Callable:
        annotations = inspect.getmembers(func)[0][1]

        if len(annotations) > 0:
            if len(args) > 0:
                for index, arg in enumerate(args):
                    parameter_name = list(annotations.keys())[index]
                    data_type = annotations[list(annotations.keys())[index]]
                    if not isinstance(arg, data_type):
                        raise TypeError(
                            "Parameter `{}` require type {}.".format(
                                parameter_name, data_type))

            if len(kwargs) > 0:
                for key in kwargs:
                    data_type = annotations[key]
                    if not isinstance(kwargs[key], data_type):
                        raise TypeError(
                            "Parameter {} require type {}.".format(
                                key, data_type))

        return func(self, *args, **kwargs)

    return wrapper
