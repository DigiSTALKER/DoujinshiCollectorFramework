# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 15:49
# @Author  : Hochikong
# @FileName: ReadConfig.py

import os
import re
from configparser import RawConfigParser
from platform import platform

from djscollect.TypeCheck import parameters_type_check, c_parameters_type_check

# This program is use for reading configure file
WINDOWS = "Windows"
LINUX = "Linux"


@parameters_type_check
def convert_raw_cookie2dict(raw_cookie: str) -> dict:
    """
    Convert cookie string which copied from browser
    :param raw_cookie: string
    :return: dict
    """
    return {i.split("=")[0]: i.split("=")[-1] for i in raw_cookie.split("; ")}


class PathTypeError(Exception):
    pass


class PathError(Exception):
    pass


class CFG:
    """
    Platform relative
    """

    def __init__(self, filename: str):
        self.__default_path_win = r"\nh_download"
        self.__default_path_lin = r"/nh_download"
        self.__platform = WINDOWS if WINDOWS in platform() else LINUX
        self.__filename = filename
        self.__cf = RawConfigParser()
        self.__cf.read(filename, encoding='utf-8')
        self.__ENABLE_PROXY = False
        self.__PROXY_CFG = {}
        self.__ENABLE_COOKIES = False
        self.__COOKIES = None
        self.__PLUGINS = []

        # with default values
        self.__AGENT = None
        self.__CUSTOM_WORKERS = 1
        self.__CUSTOM_OUTPUT_DIR = None
        self.__WELCOME = {
            'Chinese': '欢迎使用本子归档爬虫程序v2.0，这个程序能实现你的深邃黑暗幻想，可键入help查看帮助信息。 \n',
            'English': 'Welcome to use Doujinshi Scraper. It can fulfill your deep dark fantasies. Enter '
                       '"help" for useful information. \n'}
        self.__DEFAULT_TIMEOUT = 10
        self.__set_default_custom_output_dir()

    def __set_default_custom_output_dir(self):
        current = os.getcwd()
        default_path = self.__default_path_win if self.__platform is WINDOWS else self.__default_path_lin
        split_str = "\\" if self.__platform is WINDOWS else '/'
        if current.endswith(split_str):
            self.__CUSTOM_OUTPUT_DIR = current + default_path.strip(split_str)

    @property
    def runtime_platform(self) -> str:
        return self.__platform

    def get_cfg_from_file(self, section: str, title: str) -> str:
        """
        Get content from configuration file from a specific section and title
        :param section: ini section, e.g., [Proxy] --> "Proxy" is section
        :param title: ini title, e.g., [Proxy]\n enable_proxy=True --> "enable_proxy" is title
        :return: content or false
        """
        return self.__cf[section].get(title)

    def get_cfg_name(self) -> str:
        """
        Return configure file's name
        :return:
        """
        return self.__filename

    @c_parameters_type_check
    def set_proxy(self, status: bool, cfg: dict):
        """
        Set proxy
        :param status: True or False
        :param cfg: a dict which contains 'http' and 'https', these two keys it's required when use socks5 proxy
        :return:
        """
        self.__ENABLE_PROXY = status
        self.__PROXY_CFG = cfg

    @c_parameters_type_check
    def set_cookies(self, status: bool, content: str):
        """
        Set cookies
        :param status: True or False
        :param content: a dict contains cookie settings
        :return:
        """
        self.__COOKIES = content
        self.__ENABLE_COOKIES = status

    @c_parameters_type_check
    def set_user_agent(self, agent: str):
        """
        Set user agent
        :param agent: string
        :return:
        """
        self.__AGENT = agent

    @c_parameters_type_check
    def set_workers(self, workers: int):
        """
        Set workers for concurrent.futures
        :param workers: number, usually it smaller than 5 is enough
        :return:
        """
        self.__CUSTOM_WORKERS = workers

    @c_parameters_type_check
    def set_plugins(self, plugins: list):
        """
        Set plugins
        :param plugins: list
        :return:
        """
        self.__PLUGINS = plugins

    @c_parameters_type_check
    def set_download_dir(self, path: str):
        """
        Set download path
        :param path: string
        :return:
        """
        self.__CUSTOM_OUTPUT_DIR = path

    @c_parameters_type_check
    def set_timeout(self, timeout: int):
        """
        Set requests timeout
        :param timeout: number, when timeout is 10, it means waiting for 10 seconds
        :return:
        """
        self.__DEFAULT_TIMEOUT = timeout

    def get_proxy(self) -> tuple:
        """
        When you change the status of CFG, use this function to fetch the contents
        :return: Erlang style tuple, e.g. (DESCRIPTION(string), ENABLE/DISABLE(bool), CONFIG(dict))
        """
        if self.__ENABLE_PROXY:
            return ('proxy_enable', self.__ENABLE_PROXY, self.__PROXY_CFG)
        else:
            return ('proxy_disable', self.__ENABLE_PROXY)

    def get_cookies(self) -> tuple:
        """
        When you change the status of CFG, use this function to fetch the contents
        :return: Erlang style tuple, e.g. (DESCRIPTION(string), ENABLE/DISABLE(bool), CONFIG(dict))
        """
        if self.__ENABLE_COOKIES:
            return ('cookies', self.__ENABLE_COOKIES, self.__COOKIES)
        else:
            return ('cookies', self.__ENABLE_COOKIES)

    def get_agent(self) -> tuple:
        """
        When you change the status of CFG, use this function to fetch the contents
        :return: Erlang style tuple, e.g. (DESCRIPTION(string), AGENT(string))
        """
        return ('user_agent', self.__AGENT)

    def get_workers(self) -> tuple:
        """
        When you change the status of CFG, use this function to fetch the contents
        :return: Erlang style tuple, e.g. (DESCRIPTION(string), WORKERS_COUNT(int))
        """
        return ('workers', self.__CUSTOM_WORKERS)

    def get_plugins(self) -> tuple:
        """
        When you change the status of CFG, use this function to fetch the contents
        :return: Erlang style tuple, e.g. (DESCRIPTION(string), PLUGINS(list))
        """
        return ('plugins', self.__PLUGINS)

    def get_dir(self) -> tuple:
        """
        When you change the status of CFG, use this function to fetch the contents
        :return: Erlang style tuple, e.g. (DESCRIPTION(string), PATH(string))
        """
        return ('path', self.__CUSTOM_OUTPUT_DIR)

    def get_timeout(self) -> tuple:
        """
        When you change the status of CFG, use this function to fetch the contents
        :return: Erlang style tuple, e.g. (DESCRIPTION(string), TIMEOUT(int))
        """
        return ('timeout', self.__DEFAULT_TIMEOUT)


@parameters_type_check
def check_proxy_cfg(obj: CFG):
    """
    Check config file and write user custom proxy
    :param obj: CFG object
    :return:
    """
    section = 'Proxy'
    http_pattern = re.compile(
        r'(socks5)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
    https_pattern = re.compile(
        r'(socks5h)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
    try:
        use_proxy = obj.get_cfg_from_file(section, 'enable_proxy')
        http_cfg = obj.get_cfg_from_file(section, 'http')
        https_cfg = obj.get_cfg_from_file(section, 'https')
    except KeyError:
        return
    if use_proxy == 'True':
        http_url_format_correct = http_pattern.match(http_cfg)
        https_url_format_correct = https_pattern.match(https_cfg)
        if http_url_format_correct and https_url_format_correct:
            obj.set_proxy(
                status=True,
                cfg={
                    'http': http_url_format_correct.group(),
                    'https': https_url_format_correct.group()})
    return


@parameters_type_check
def check_header_cfg(obj: CFG):
    """
    Check config file and write user custom headers
    :param obj: CFG object
    :return:
    """
    backup_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                   '(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    section = 'Headers'
    try:
        use_cookie = obj.get_cfg_from_file(section, 'cookies')
        use_agent = obj.get_cfg_from_file(section, 'user_agent')
    except KeyError:
        return
    if use_cookie:
        obj.set_cookies(True, use_cookie)
    if use_agent:
        obj.set_user_agent(use_agent)
    else:
        obj.set_user_agent(backup_agent)
    return


@parameters_type_check
def check_main_cfg(obj: CFG):
    """
    Check timeout, workers and download path and write
    :param obj: CFG object
    :return:
    """
    section = 'Main'
    try:
        have_workers = obj.get_cfg_from_file(section, 'max_workers')
        have_output_dir = obj.get_cfg_from_file(section, 'output_dir')
        have_timeout = obj.get_cfg_from_file(section, 'timeout')
        have_plugins = obj.get_cfg_from_file(section, 'plugins')
    except KeyError:
        return
    if have_workers:
        obj.set_workers(int(have_workers))
    if have_output_dir:
        if "\\" in have_output_dir and obj.runtime_platform == WINDOWS:
            obj.set_download_dir(have_output_dir)
        elif "/" in have_output_dir and obj.runtime_platform == LINUX:
            obj.set_download_dir(have_output_dir)
        else:
            raise PathTypeError(
                "Wrong output_dir type, check your config.ini and OS type.")
    if have_timeout:
        obj.set_timeout(int(have_timeout))
    if have_plugins:
        if len(have_plugins) > 0:
            plugs = [plug.strip() for plug in have_plugins.split(",")]
            obj.set_plugins(plugs)
