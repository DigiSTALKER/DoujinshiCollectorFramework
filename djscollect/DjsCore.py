# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 15:50
# @Author  : Hochikong
# @FileName: DjsCore.py
# This program is the core component of djsc

import concurrent.futures
import json
import time
import requests
from typing import Dict
from pampy import match, _
from djscollect.ReadConfig import *
from tqdm import tqdm

ENABLE = 'enable'
DISABLE = 'disable'
# when use True, match will return the full tuple if lambda one parameter
PATTERN_COOKIES_PASS = ('cookies', True, _)
# when use bool, match will only return the value of bool if lambda one param
PATTERN_COOKIES_FAIL = ('cookies', bool)
PATTERN_AGENT = ('user_agent', _)
PATTERN_PROXY_ENABLE = ('proxy_enable', True, _)
PATTERN_PROXY_DISABLE = ('proxy_disable', bool)


class Librarian:
    """"
    A single doushiji
    """

    def __init__(self, configfile: str):
        """"
        Initial Book
        """
        # configurations from file
        self.__config_file = configfile
        self.cfg = None
        self.__proxy = {}
        self.__headers = {}
        self.pool = None
        self.__timeout = 0
        self.__plugins = ()

        # runtime configurations
        self.__cache = None
        self.__metadata = {}
        self.__pic_urls = []
        self.__current_path = ""
        self.__download_path = None
        self.__dir_stack = []

        self.__platform = None
        self.__split_string = {'Windows': "\\", "Linux": "/"}
        self.__platform_split = None
        self.pic_save_pattern = ''

        self.tqdm_instance: tqdm = None

    def debug_info(self) -> dict:
        return {
            'proxy': self.__proxy,
            'headers': self.__headers,
            'pool': self.pool,
            'timeout': self.__timeout,
            'metadata': self.__metadata,
            'pic_urls': self.__pic_urls,
            'current_path': self.__current_path,
            'root': self.__download_path,
            'platform': self.__platform,
            'split': self.__platform_split,
            'stack': self.__dir_stack,
            'plugins': self.__plugins
        }

    @staticmethod
    def has_data(*args) -> bool:
        for i in args:
            if isinstance(i, int):
                if i < 1:
                    return False
            if isinstance(i, dict):
                if len(i) < 1:
                    return False
        return True

    @c_parameters_type_check
    def load_cfg(self) -> bool:
        """
        Load configurations from CFG
        :return: bool
        """
        self.cfg = CFG(self.__config_file)
        check_proxy_cfg(self.cfg)
        check_header_cfg(self.cfg)
        check_main_cfg(self.cfg)

        # Proxy
        self.__proxy = match(self.cfg.get_proxy(),
                             PATTERN_PROXY_ENABLE, lambda proxy: proxy,
                             PATTERN_PROXY_DISABLE, lambda proxy: {}
                             )

        # Headers
        tmp = match(self.cfg.get_cookies(),
                    PATTERN_COOKIES_PASS, lambda cookie: cookie,
                    PATTERN_COOKIES_FAIL, lambda cookie: {}
                    )
        if len(tmp) > 0:
            self.__headers['Cookie'] = tmp
        self.__headers['User-Agent'] = match(
            self.cfg.get_agent(), PATTERN_AGENT, lambda agent: agent)

        # Others
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=match(
            self.cfg.get_workers(), ('workers', _), lambda count: count))
        self.__timeout = match(
            self.cfg.get_timeout(), ('timeout', _), lambda timeout: timeout)
        self.__download_path = match(
            self.cfg.get_dir(), ('path', _), lambda path: path)
        self.__dir_stack.append(self.__download_path)
        self.__plugins = match(
            self.cfg.get_plugins(), ('plugins', _), lambda plugins: plugins)

        # Platform
        self.__platform = self.cfg.runtime_platform
        self.__platform_split = self.__split_string[self.__platform] if self.__platform else "\\"

        return True

    @c_parameters_type_check
    def _runtime_change(self, attr_name: str, value) -> dict:
        """
        Runtime change attribute of Librarian
        :param attr_name: string
        :param value: any types
        :return: dict
        """
        prefix = "_Librarian"
        setattr(self, prefix + attr_name, value)
        return self.debug_info()

    def handle_dir_name(self, sub_dir: str) -> str:
        """
        Automatically solve different platform path problems
        :param sub_dir: directory name without any "\\" or "/"
        :return: string
        """
        tmp = 1
        if sub_dir.startswith(self.__platform_split):
            tmp = 1
        elif sub_dir.endswith(self.__platform_split):
            tmp = 0
        else:
            return self.__platform_split + sub_dir
        return self.__platform_split + \
               sub_dir.split(self.__platform_split)[tmp]

    def __enter(self) -> bool:
        abs_path = ''.join(self.__dir_stack)
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
            os.chdir(abs_path)
        else:
            os.chdir(abs_path)
        return True

    # def __enter(self) -> bool:
    #     if not os.path.exists(self.__download_path):
    #         os.mkdir(self.__download_path)
    #     os.chdir(self.__download_path)
    #     try:
    #         for sub_dir in self.__dir_stack:
    #             sub_dir = sub_dir.strip(self.__platform_split)
    #             if not os.path.exists(sub_dir):
    #                 os.mkdir(sub_dir)
    #                 os.chdir(sub_dir)
    #             else:
    #                 os.chdir(sub_dir)
    #         if os.getcwd() == ''.join(self.__dir_stack):
    #             return True
    #     except Exception as e:
    #         print(str(e))
    #     finally:
    #         self.__dir_stack.pop()

    @c_parameters_type_check
    def enter_sub_dir(self, dirname: str) -> bool:
        """"
        Push to self.__download_path/dirname
        :param dirname: string, relative path
        :return: string
        """
        handle_result = self.handle_dir_name(dirname)
        self.__dir_stack.append(handle_result)
        try:
            target_path = handle_result.strip(self.__platform_split)
            # try to validate this relative path before next steps
            if not os.path.exists(target_path):
                os.mkdir(target_path)
                os.rmdir(target_path)

            done = self.__enter()
            if not done:
                return False
            self.__current_path = os.getcwd()
            return True
        except Exception:
            self.__dir_stack.pop()
            return False

    def exit_dir(self) -> str:
        """
        Go to father directory, but can't go to __download_path's father directory
        :return:
        """
        if len(
                self.__dir_stack) == 1 and self.__dir_stack[0] == self.__download_path:
            return self.__current_path
        else:
            os.chdir("..")
            self.__dir_stack.pop()
            self.__current_path = os.getcwd()
            return self.__current_path

    @c_parameters_type_check
    def pop(self) -> str:
        """"
        Return to root path
        :return: path
        """
        os.chdir(self.__download_path)
        self.__dir_stack = [self.__download_path, ]
        self.__current_path = os.getcwd()
        return self.__current_path

    @c_parameters_type_check
    def set_metadata(self, content: dict) -> str:
        """"
        Set metadata as json but not yet save
        :param content: dict, content is return from plugins
        :return: str
        """
        self.__metadata = json.dumps(obj=content, indent=4, ensure_ascii=False)
        return self.__metadata

    def commit_metadata(self) -> bool:
        """
        Push to directory and save metadata
        :return: bool
        """
        with open('metadata.txt', 'w', encoding='utf-8') as f:
            f.write(self.__metadata)
        return True

    @c_parameters_type_check
    def smart_get(self, url: str, desc: str) -> tuple:
        """
        Simple wrapper of requests.get()
        :param url: string
        :param desc: string, description
        :return: tuple
        """
        result = match(
            tuple(i if Librarian.has_data(i) else DISABLE for i in (self.__headers, self.__proxy, self.__timeout)),

            (Dict[str, str], Dict[str, str], int),
            lambda x, y, z: requests.get(url, headers=x, proxies=y, timeout=z),

            (Dict[str, str], str, int),
            lambda x, y, z: requests.get(url, headers=x, timeout=z),
        )
        return (result, desc)

    @c_parameters_type_check
    def save_pic(self, pic_url: str, pic_name: str) -> bool:
        """
        Download single picture or something
        :param pic_url: string, url
        :param pic_name: string, name with extension name like `girl.png` or `book.html` is good
        :return: bool
        """
        result = self.smart_get(pic_url, pic_name)
        with open(result[1], 'wb') as f:
            f.write(result[0].content)
        return True

    @c_parameters_type_check
    def smart_save_pic(self, pic_url: str) -> bool:
        """
        Download single picture, file postfix generate automatically
        :param pic_url: string, url
        :return: bool
        """
        pattern = re.compile(self.pic_save_pattern)
        name = pattern.findall(pic_url)[0] if pattern.findall(pic_url) \
            else time.strftime("%Y-%m-%d_%H-%M-%S.jpg", time.localtime())
        if name:
            self.save_pic(pic_url, name)
            # print("Downloading {}".format(name))
        self.tqdm_instance.update(1)
        return False

    @c_parameters_type_check
    def download_book(self, pic_urls: list) -> bool:
        """
        Download a book to book_path
        :param pic_urls: list, [url1, url2, url3 ...]
        :return: bool
        """
        self.tqdm_instance = tqdm(total=len(pic_urls))
        concurrent.futures.wait([self.pool.submit(self.smart_save_pic, single_url)
                                 for single_url in pic_urls], return_when='ALL_COMPLETED')
        self.tqdm_instance.close()
        return True
