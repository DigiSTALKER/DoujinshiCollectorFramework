# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 16:24
# @Author  : Hochikong
# @FileName: test_ReadConfig.py
import pytest

from djscollect.ReadConfig import *

cfg = CFG('config.ini')
raw_cookie = '_user_behavior_=83ac17e6-c505-444a-wewew4-9b4bceb0931c; ' \
             'oscid=8OL9erFh4oa3eweMoVA1qULKEM'


def test_convert_raw_cookie2dict():
    result = convert_raw_cookie2dict(raw_cookie)
    assert '_user_behavior_' in result
    assert 'oscid' in result
    assert result['_user_behavior_'] == '83ac17e6-c505-444a-wewew4-9b4bceb0931c'
    assert result['oscid'] == '8OL9erFh4oa3eweMoVA1qULKEM'


def test_check_proxy_cfg():
    assert cfg.get_cfg_name() == 'config.ini'
    assert cfg.get_proxy() == ('proxy_disable', False)
    check_proxy_cfg(cfg)
    assert cfg.get_proxy() == (
        'proxy_enable', True, {
            'http': 'socks5://127.0.0.1:5082', 'https': 'socks5h://127.0.0.1:5082'})


def test_check_header_cfg():
    cfg0 = CFG('config.ini')
    check_header_cfg(cfg0)
    assert cfg0.get_cookies() == ('cookies', True, raw_cookie)
    assert cfg0.get_agent() == ('user_agent',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36')

    cfg1 = CFG('config_no_agent_no_ck_has_proxy.ini')
    check_header_cfg(cfg1)
    assert cfg1.get_cookies() == ('cookies', False)
    assert cfg1.get_agent() == ('user_agent',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36')  # backup


def test_check_main_cfg():
    # windows test
    check_main_cfg(cfg)
    assert cfg.get_workers() == ('workers', 4)
    assert cfg.get_dir() == ('path', r'D:\Doujinshi')
    assert cfg.get_timeout() == ('timeout', 5)
    assert cfg.get_plugins() == ('plugins', ['demo:requests', 'demo1:bs4'])

    ncfg = CFG('config_linux.ini')
    assert ncfg.runtime_platform == 'Windows'
    with pytest.raises(PathTypeError) as excinfo:
        check_main_cfg(ncfg)
    assert "Wrong output_dir type" in str(excinfo.value)
