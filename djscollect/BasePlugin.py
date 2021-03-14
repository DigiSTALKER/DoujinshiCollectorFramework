# -*- coding: utf-8 -*-
# @Time    : 2020/6/14 1:22
# @Author  : Hochikong
# @FileName: BasePlugin.py

from abc import ABCMeta, abstractmethod
from requests import Response


class AnalyseError(Exception):
    pass


class AbstractPlugin(metaclass=ABCMeta):
    """
    Doujinshi Collector Plugin Abstract Class
    """

    def __init__(self):
        pass

    @abstractmethod
    def save_urls_from_input(self, urls: list) -> bool:
        pass

    @abstractmethod
    def get_ids_from_urls(self) -> list:
        pass

    @abstractmethod
    def next_book(self) -> bool:
        pass

    @abstractmethod
    def prepare_for_analyse(self, raw: Response) -> bool:
        pass

    @abstractmethod
    def analyse_title(self) -> tuple:
        pass

    @abstractmethod
    def analyse_metadata(self) -> dict:
        pass

    @abstractmethod
    def analyse_pic_urls(self) -> list:
        pass
