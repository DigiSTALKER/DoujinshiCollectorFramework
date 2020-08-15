# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 15:42
# @Author  : Hochikong
# @FileName: DJSC.py

import yaml
import argparse
from stevedore import driver
from djscollect.DjsCore import *

VERSION = '0.0.3.2'
DL_HEAD = "+" * 3 + "*" * 40 + "+" * 3
DL_TAIL = "-" * 3 + "*" * 40 + "-" * 3
DL_MIDDLE = "#" * 3 + "*" * 40 + "#" * 3
HELP = """
Welcome to use Doujinshi Collector.
All available commands:
help                         -- Check useful information.

load cfg CONFIG.INI          -- Load configuration files, check config_demo.ini for reference.

show plugins                 -- List all registered namespaces and plugins in your configuration file.
                                And what analyzer currently you use.

load plugin NS:PG            -- Load plugin as analyzer by namespace(NS) and plugin name(PG).
                                e.g. "load plugins djscp:manga".

download URL                 -- Download a doujinshi. You must use load plugin before this command.

batch URLS_FILE_PATH         -- Download a bunch of doujinshis by reading a yaml format file.
                                e.g. urls.yml should like this
                                #######################################
                                - author: Author1
                                  urls:
                                  - https://xxxxx

                                - author: Author2
                                  urls:
                                  - https://yyyyy
                                  - https://zzzzz
                                #######################################

pwd                          -- Just pwd.

reset                        -- Reset all configurations.

cd                           -- Change path.

quit                         -- Exit the program.

"""


def dict2table(plugins: dict):
    tmp = []
    max_namespace_len = 0
    max_plugin_len = 0
    for key in plugins:
        if len(key) > max_namespace_len:
            max_namespace_len = len(key)
        if len(plugins[key]) > max_plugin_len:
            max_plugin_len = len(plugins[key])
        tmp.append([key, plugins[key]])
    if max_namespace_len > len("Namespace: "):
        max_namespace_len += max_namespace_len - len("Namespace: ")
    else:
        max_namespace_len -= len("Namespace: ")
    if max_plugin_len > len("| Plugins: "):
        max_plugin_len += max_plugin_len - len("| Plugins: ")
    else:
        max_plugin_len -= len("| Plugins: ")
    table_head_ns = "Namespaces: " + " " * max_namespace_len
    table_head_pg = "| Plugins: " + " " * max_plugin_len
    table_body_ns = "%s"
    table_body_pg = "| %s"
    table_head = table_head_ns + table_head_pg + '\n'
    table_head += "-" * len(table_head) + '\n'
    table_content = [table_body_ns %
                     ele[0] +
                     " " *
                     (len(table_head_ns) -
                      len(ele[0])) +
                     table_body_pg %
                     ele[1] +
                     " " *
                     (len(table_head_pg) -
                      len(ele[1])) +
                     '\n' for ele in tmp]
    table_intro = "All registered namespaces and plugins:"
    table_intro_final = table_intro if len(table_intro) > len(table_head) else \
        table_intro + " " * (len(table_head) - len(table_intro))
    output = table_intro_final + "\n" + table_head
    output += ''.join(table_content)
    return output


class REPR:
    def __init__(self, config_path=None, plugin=None):
        self.help_info = HELP
        self.intro = "Welcome to use Doujinshi Collector v{}. Enter 'help' for useful information. \n".format(
            VERSION)
        self.prompt = "DJSC|{}> "
        self.plugins = None
        self.mgr = None
        self.analyzer = None
        self.info = None
        self.current_analyzer = None
        self.home = os.getcwd()

        if config_path:
            self.load_cfg(config_path)
        if plugin:
            self.load_plugin(plugin)

    @staticmethod
    def done():
        print("Done.\n")

    @staticmethod
    def println(cont=None):
        if cont:
            print(cont + '\n')
        else:
            print("\n")

    def load_cfg(self, path):
        """
        Load configurations from files and initial Librarian class
        :param path: string
        :return:
        """
        if os.path.exists(path):
            self.mgr = Librarian(path)
            if self.mgr.load_cfg():
                self.plugins = self.mgr.debug_info()['plugins']
                tmp = [plug.split(":") for plug in self.plugins]
                result = {}
                for lis in tmp:
                    if not lis[0] in result:
                        result[lis[0]] = []
                    result[lis[0]].append(lis[1])
                self.info = dict2table(result)
                print("Load done.\n")
        else:
            print("Configuration file path not found.\n")

    def help(self):
        """
        Print help
        :return:
        """
        print(self.help_info)

    def list_plugins(self):
        """
        List all available plugins
        :return:
        """
        if self.info is None:
            print("Currently no plugin is available.\n")
        else:
            print(self.info)
            print('\n')
            if self.current_analyzer:
                self.check_analyzer()

    def check_analyzer(self):
        """
        Check
        :return:
        """
        print(
            "Currently use: " +
            self.current_analyzer +
            ' as analyzer.' +
            '\n')

    def load_plugin(self, namespace_plugin):
        """
        Use stevedore to load a specific analyzer class
        :param namespace_plugin: string, like 'djscp:xxx'
        :return:
        """
        if namespace_plugin not in self.plugins:
            print("Plugin {} apply failed\n".format(namespace_plugin))
        else:
            tmp = namespace_plugin.split(":")
            ns = tmp[0]
            pg = tmp[1]
            mgr = driver.DriverManager(
                namespace=ns, name=pg, invoke_on_load=True)
            self.analyzer = mgr.driver
            self.current_analyzer = namespace_plugin
            print("Plugin {} apply done.\n".format(namespace_plugin))

    def _download(self, urls):
        """
        Core download function
        :param urls: list
        :return:
        """
        # analyse doujinshi info
        self.analyzer.save_urls_from_input(urls)
        self.analyzer.get_ids_from_urls()

        for i in range(len(urls)):
            try:
                # start to analyse
                self.analyzer.next_book()
                response = self.mgr.smart_get(
                    self.analyzer.current_book[0][0],
                    self.analyzer.current_book[0][1])
                self.analyzer.prepare_for_analyse(response[0])

                title = self.analyzer.analyse_title()
                metadata = self.analyzer.analyse_metadata()
                pic_urls = self.analyzer.analyse_pic_urls()

                # enter sub dir
                enter = self.mgr.enter_sub_dir(title[-1])
                if not enter:
                    print("Path error, use doujinshi id instead.\n")
                    self.mgr.enter_sub_dir(title[0])

                # save metadata
                self.println("Save to: " + os.getcwd())
                self.mgr.set_metadata(metadata)
                self.mgr.commit_metadata()

                # download
                start = time.time()
                print(
                    "Downloading {} \n".format(
                        self.analyzer.current_book[0][1]))
                pas = self.mgr.download_book(pic_urls)
                end = time.time()
                self.mgr.exit_dir()
                print(
                    "Doujinshi {} download done, cost {} seconds.\n".format(
                        title[0], round(
                            (end - start), 2)))
            except StopIteration:
                self.mgr.pop()
                continue
        return True

    def single_download(self, url):
        """
        Download a single doujinshi. If url not compatible with a current plugin, it won't download anything
        :param url: string
        :return:
        """
        self.println(DL_HEAD)
        try:
            if self.mgr is None or self.analyzer is None:
                print("Download failed, enter `help` for help.")
            else:
                self._download([url, ])
            os.chdir(self.home)
        except Exception as e:
            self.println("Download failed and stopped.")
            print(str(e))
        self.println(DL_TAIL)

    def batch_download(self, yml_path):
        """
        Read yaml file to download more than one doujinshi
        :param yml_path: string, a yaml format file's path
        :return:
        """
        self.println(DL_HEAD)
        if not os.path.exists(yml_path):
            print("Urls file not found\n")
        else:
            with open(yml_path, 'r', encoding='UTF-8') as file:
                yaml_cfg = yaml.load(file, Loader=yaml.FullLoader)
            try:
                for section in yaml_cfg:
                    print(
                        "Downloading author {}'s doujinshi.\n".format(
                            section['author']))
                    if isinstance(section['author'], int):
                        section['author'] = str(section['author'])
                    self.mgr.enter_sub_dir(section['author'])
                    if self._download(section['urls']):
                        print(
                            "Author {}'s doujinshi download done.\n".format(
                                section['author']))
                    self.mgr.exit_dir()
                    self.println(DL_MIDDLE)
                print("All sections' download done.\n")
            except Exception as e:
                print("Download failed and stopped.")
                print(str(e))
        os.chdir(self.home)
        self.println(DL_TAIL)

    def reset(self):
        self.plugins = None
        self.mgr = None
        self.analyzer = None
        self.info = None
        self.current_analyzer = None
        self.home = os.getcwd()

    def run(self):
        print(self.intro)
        while True:
            result = input(
                self.prompt.format(
                    self.current_analyzer if self.current_analyzer else '#')).strip()
            try:
                self.println()
                if 'help' in result:
                    self.help()
                    self.done()
                elif 'load cfg' in result:
                    path = result.split(" ")[-1]
                    self.load_cfg(path)
                    self.done()
                elif 'show plugins' in result:
                    self.list_plugins()
                    self.done()
                elif 'load plugin' in result:
                    ns = result.split(" ")[-1]
                    self.load_plugin(ns)
                    self.done()
                elif 'download' in result:
                    url = result.split(" ")[-1]
                    self.single_download(url)
                    self.done()
                elif 'batch' in result:
                    path = result.split(" ")[-1]
                    self.batch_download(path)
                    self.done()
                elif 'pwd' in result:
                    print(os.getcwd())
                    self.done()
                elif 'reset' in result:
                    self.reset()
                    self.done()
                elif 'cd' in result:
                    os.chdir(result.split(" ")[-1])
                    self.done()
                elif 'quit' in result:
                    print("Bye \n")
                    break
                else:
                    print("Syntax Error, enter 'help' for help.")
            except Exception as e:
                print(str(e))


@parameters_type_check
def convert2yml(path: str, target: str):
    head_template = ['- author: {}\n', '  urls:\n']
    url_template = '  - {}\n'
    try:
        with open(path, 'r') as f:
            cont = f.readlines()
        authors = {}
        current_author = ""
        for line in cont:
            if "Author" in line:
                current_author = line.split(":")[1].strip()
                authors[current_author] = []
            if "http" in line:
                authors[current_author].append(line.strip())
            if len(line.strip()) < 2:
                current_author = ""

        result = []
        with open(target, 'w') as f1:
            for author in authors:
                result.append(head_template[0].format(author))
                result.append(head_template[1])
                for url in authors[author]:
                    result.append(url_template.format(url))
            f1.writelines(result)
        print("Convert done!!!\n")
    except Exception:
        print("Convert failed!!!\n")
        print("""
        URL file should like this:

        Author:ttt
        http://xxxx
        http://yyyy

        Author:sss
        https://zzzz
        """)
        return


def run():
    parser = argparse.ArgumentParser(
        description='A Doujinshi Collector Framework.')
    parser.add_argument('-c', '--cfg', type=str, help='Configuration file path.', metavar="CONFIG FILE")
    parser.add_argument('-p', '--plugin', type=str, help="Load a plugin from FILE.", metavar="NAMESPACE:PLUGIN NAME")
    parser.add_argument('-f', '--convert',
                        nargs='+', type=str,
                        help="Convert url files to yml", metavar=("SOURCE FILE", "TARGET FILE"))
    args = parser.parse_args()
    if args.convert:
        if len(args.convert) == 2:
            convert2yml(args.convert[0], args.convert[1])
        else:
            print("Convert failed!!! You need to set source file and target file.\n")
        return
    else:
        cmd = REPR(args.cfg, args.plugin)
        cmd.run()


if __name__ == '__main__':
    run()
