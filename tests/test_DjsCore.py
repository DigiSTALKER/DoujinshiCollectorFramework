# -*- coding: utf-8 -*-
# @Time    : 2020/6/15 16:47
# @Author  : Hochikong
# @FileName: test_DjsCore.py
from concurrent.futures import ThreadPoolExecutor

from djscollect.DjsCore import *

normal_headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                 '(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
normal_cookie = '_user_behavior_=83ac17e6-c505-444a-wewew4-9b4bceb0931c; oscid=8OL9erFh4oa3eweMoVA1qULKEM'
proxy = {'http': 'socks5://127.0.0.1:5082',
         'https': 'socks5h://127.0.0.1:5082'}
home = r'C:\Users\ckhoi\PycharmProjects\MetaCollect\PythonBaseTools\doujinshiCollector\tests'


def test__debug():
    lib_normal = Librarian('config.ini')
    lib_wrong = Librarian('config_wrong.ini')
    lib_no_headers_with_proxy = Librarian(
        'config_no_agent_no_ck_has_proxy.ini')
    lib_no_proxy_with_headers = Librarian('config_no_proxy_has_ckag.ini')
    lib_no_proxy_no_ck_with_ag = Librarian('config_no_proxy_no_ck.ini')
    lib_normal.load_cfg()
    tmp = lib_normal.debug_info()
    assert tmp['proxy'] == proxy
    assert tmp['headers']['User-Agent'] == normal_headers
    assert tmp['headers']['Cookie'] == normal_cookie
    assert isinstance(tmp['pool'], ThreadPoolExecutor)
    assert tmp['timeout'] == 5
    assert len(tmp['metadata']) == 0
    assert len(tmp['pic_urls']) == 0
    assert tmp['current_path'] == '.'
    assert tmp['root'] == r'D:\Doujinshi'
    assert tmp['plugins'] == ['demo:requests', 'demo1:bs4']

    lib_wrong.load_cfg()
    tmp = lib_wrong.debug_info()
    assert len(tmp['proxy']) == 0
    assert tmp['headers']['User-Agent'] == normal_headers
    assert tmp['root'] != r'D:\Doujinshi'

    lib_no_headers_with_proxy.load_cfg()
    tmp = lib_no_headers_with_proxy.debug_info()
    assert tmp['proxy'] == proxy
    assert tmp['headers']['User-Agent'] == normal_headers
    assert isinstance(tmp['pool'], ThreadPoolExecutor)
    assert tmp['timeout'] == 5
    assert len(tmp['metadata']) == 0
    assert len(tmp['pic_urls']) == 0
    assert tmp['current_path'] == '.'
    assert tmp['root'] == r'D:\Doujinshi'

    lib_no_proxy_with_headers.load_cfg()
    tmp = lib_no_proxy_with_headers.debug_info()
    assert tmp['proxy'] == {}
    assert tmp['headers']['User-Agent'] == normal_headers
    assert tmp['headers']['Cookie'] == normal_cookie
    assert isinstance(tmp['pool'], ThreadPoolExecutor)
    assert tmp['timeout'] == 5
    assert len(tmp['metadata']) == 0
    assert len(tmp['pic_urls']) == 0
    assert tmp['current_path'] == '.'
    assert tmp['root'] == r'D:\Doujinshi'

    lib_no_proxy_no_ck_with_ag.load_cfg()
    tmp = lib_no_proxy_no_ck_with_ag.debug_info()
    assert tmp['proxy'] == {}
    assert tmp['headers']['User-Agent'] == normal_headers
    assert isinstance(tmp['pool'], ThreadPoolExecutor)
    assert tmp['timeout'] == 5
    assert len(tmp['metadata']) == 0
    assert len(tmp['pic_urls']) == 0
    assert tmp['current_path'] == '.'
    assert tmp['root'] == r'D:\Doujinshi'


def test_has_data():
    assert Librarian.has_data({'demo': 'demo'})
    assert Librarian.has_data({}) is False
    assert Librarian.has_data(1)
    assert Librarian.has_data(0) is False


def test__runtime_change():
    lib = Librarian('config.ini')


def test_enter_sub_dir():
    lib_normal = Librarian('config.ini')
    lib_normal.load_cfg()
    lib_normal.enter_sub_dir("Others")
    assert lib_normal.debug_info()['current_path'] == r"D:\Doujinshi\Others"
    tmp = lib_normal.pop()
    assert lib_normal.debug_info()['root'] == r"D:\Doujinshi"
    os.chdir(home)


def test_pop():
    lib_normal = Librarian('config.ini')
    lib_normal.load_cfg()
    lib_normal.enter_sub_dir("2031")
    assert lib_normal.debug_info()['current_path'] == r"D:\Doujinshi\2031"
    lib_normal.pop()
    assert lib_normal.debug_info()['root'] == r"D:\Doujinshi"
    os.chdir(home)


def test_set_metadata():
    lib_normal = Librarian('config.ini')
    lib_normal.load_cfg()
    demo = {
        'demo': 'content',
        'demo1': [
            1,
            2,
            3],
        'demo2': {
            'name': 'jack',
            'age': 12}}
    tmp = lib_normal.set_metadata(demo)
    assert isinstance(tmp, str)


def test_save_metadata():
    lib_normal = Librarian('config.ini')
    lib_normal.load_cfg()
    demo = {
        'demo': 'content',
        'demo1': [
            1,
            2,
            3],
        'demo2': {
            'name': 'jack',
            'age': 12}}
    lib_normal.set_metadata(demo)
    lib_normal.enter_sub_dir("meta")
    lib_normal.commit_metadata()
    assert os.path.exists('metadata.txt')
    os.chdir(home)


def test_save_pic():
    lib = Librarian('config_no_proxy_no_ck.ini')
    lib.load_cfg()
    url = 'https://oscimg.oschina.net/oscnet/up-411ae0cdd3adf777ab3c800adbf6c964bb1.png'
    lib.enter_sub_dir('Download')
    tmp = lib.save_pic(url, 'oschina.png')
    assert os.path.exists('oschina.png')
    os.chdir(home)


def test_handle_dir_name():
    lib = Librarian('config.ini')
    lib.load_cfg()
    assert lib.handle_dir_name("\\Win") == "\\Win"
    assert lib.handle_dir_name("\\Win\\") == "\\Win"
    assert lib.handle_dir_name("Win\\") == "\\Win"
    assert lib.handle_dir_name("Win") == "\\Win"
    # assert lib.handle_dir_name("/Linux") == "/Linux"
    # assert lib.handle_dir_name("/Linux/") == "/Linux"
    # assert lib.handle_dir_name("Linux/") == "/Linux"
    # assert lib.handle_dir_name("Linux") == "/Linux"


def test_exit_dir():
    lib_normal = Librarian('config.ini')
    lib_normal.load_cfg()
    lib_normal.enter_sub_dir("Others")
    assert lib_normal.debug_info()['current_path'] == r"D:\Doujinshi\Others"
    lib_normal.enter_sub_dir("22222")
    assert lib_normal.debug_info(
    )['current_path'] == r"D:\Doujinshi\Others\22222"
    lib_normal.exit_dir()
    assert lib_normal.debug_info()['current_path'] == r"D:\Doujinshi\Others"
    os.chdir(home)


def test_smart_save_pic():
    lib_normal = Librarian('config.ini')
    lib_normal.load_cfg()
    lib_normal.enter_sub_dir("Others")
    lib_normal.smart_save_pic("https://i.nhentai.net/galleries/1666319/18.jpg")
    assert os.path.exists('18.jpg')
    os.chdir(home)


def test_download_book():
    with open('urls.txt', 'r') as f:
        urls = f.readlines()
    urls = [i.strip() for i in urls]
    lib_normal = Librarian('config.ini')
    lib_normal.load_cfg()
    lib_normal.enter_sub_dir("Others")
    assert lib_normal.download_book(urls)
