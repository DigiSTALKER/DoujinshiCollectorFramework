# 同人志爬虫框架
这个程序是基于Python的爬虫框架，可以用于各种同人志网站的爬取。

## 安装需求

### Python版本:
Python>=3.6

其他依赖库:

pampy>=0.3.0  
requests>=2.23.0  
pytest>=5.4.3  
stevedore>=2.0.0  
PyYAML>=5.3.1  
lxml>=4.5.0  
bs4>=0.0.1  
pysocks>=1.7.1  

### 通过Pip安装whl（适合熟悉Python的用户）:

从Github的releases中下载whl文件：

```
pip install djsc-0.0.x-py3-none-any.whl
```

### Windows安装包（开箱即用）：

在Github的releases中下载并解压即可安装（已捆绑部分插件）。

## 如何使用

下面的例子运行在Win 10上，使用的是whl的安装方式:

1. 从Github仓库中下载config_demo.ini，并根据你的需求编辑：

   ```
   [Proxy]
   enable_proxy = True
   http = socks5://127.0.0.1:5082
   https = socks5h://127.0.0.1:5082
   
   [Headers]
   # Cookies setting you need to use browser to acquire raw cookie string
   # cookies =
   
   # Default user agent
   user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36
   
   [Main]
   max_workers = 4
   
   # depends on your platform
   output_dir = D:\Doujinshis
   
   # 5 seconds
   timeout = 5
   
   # plugins: entry point:name
   #
   # if plugin library's setup.py like this:
   # entry_points={
   #        'djscp': [            // entry point
   #            'A = djsplugins.a:A',  // name = package.file:Class
   #            'B = djsplugins.b:B',
   #        ],
   #    },
   #
   # your `plugins` configuration should like this:
   # plugins = djscp:A, djscp:B
   #
   plugins = djscp:EXAMPLE
   ```

   Proxy部分是为支持socks协议的代理软件使用的，具体什么软件请自己查。

   Max workers是作为concurrent.futures.ThreadPoolExecutor()的最大worker数量。

   Timeout是提供给requests.get()的。

   Plugins部分的设置要看你安装了何种插件。比如, 我构建了一个插件包叫"djscp"，包中的setup.py有如下设置。其中"entry_points"是最重要的。

    

   ```
   entry_points={
           'djscp': [            // entry point
               'A = djsplugins.a:A',  // name = package.file:Class
               'B = djsplugins.b:B',
           ],
       },
   ```

   参考上面的setup.py的entry_point设置，你的 config_demo.ini应该像这样：

   ```
   [Main]
   plugins = djscp:A, djscp:B
   ```

2. 运行djsc.exe：

   ```
   PS H:\> djsc.exe -h
   usage: djsc [-h] [-c CONFIG FILE] [-p NAMESPACE:PLUGIN NAME]
               [-f SOURCE FILE [TARGET FILE ...]]
   
   A Doujinshi Collector Framework.
   
   optional arguments:
     -h, --help            show this help message and exit
     -c CONFIG FILE, --cfg CONFIG FILE
                        Configuration file path.
     -p NAMESPACE:PLUGIN NAME, --plugin NAMESPACE:PLUGIN NAME
                        Load a plugin from FILE.
     -f SOURCE FILE [TARGET FILE ...], --convert SOURCE FILE [TARGET FILE ...]
   ```
   
   你可以用 --cfg 加载你的config_demo.ini或者稍后再加载：
   
   
   
   ```
   PS H:\> djsc.exe
   Welcome to use Doujinshi Collector v0.0.x Enter 'help' for useful information.
   
   DJSC|#> load cfg config_demo.ini
   

   Load done.

   Done.
   ```
   
   输入help查看帮助信息：
   
   ```
   DJSC|#> help
   
   
   
   Welcome to use Doujinshi Collector.
   All available commands:
   help                         -- Check useful information.
   
   load_cfg CONFIG.INI          -- Load configuration files, check config_demo.ini for reference.
   
   show_plugins                 -- List all registered namespaces and plugins in your configuration file.
                                   And what analyzer currently you use.
   
   load_plugin NS:PG            -- Load plugin as analyzer by namespace(NS) and plugin name(PG).
                                   e.g. "load plugins djscp:manga".
   
   download URL                 -- Download a doujinshi. You must use load plugin before this command.
   
   bulk_down URLS_FILE_PATH     -- Download a bunch of doujinshis by reading a yaml format file.
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

   meta URL                     -- Download metadata file only.

   bulk_meta URLS_FILE_PATH     -- Download a bunch of doujinshis' metadata by reading a yaml format file.

   pwd                          -- Just pwd.
   
   pwd                          -- Just pwd.
   
   reset                        -- Reset all configurations.
   
   cd                           -- Change path.
   
   quit                         -- Exit the program.

   
   Done.
   
   ```
   
   如果你没有加载任何爬虫插件, 输入 'show plugins' 只会显示你在config_demo.ini里所设置的插件：
   
   ```
   DJSC|#> show plugins
   
   
   All registered namespaces and plugins:
   Namespaces: | Plugins:
   -----------------------
   djscp      | ['EXAMPLE']
   

   
   Done.
   
   ```
   
   使用'load plugin'去加载插件，一次只能加载一个：
   
   ```
   DJSC|#> load plugin djscp:EXAMPLE
   
   
   Plugin djscp:EXAMPLE apply done.
   
   Done.
   
   DJSC|djscp:EXAMPLE> show plugins
   
   
   All registered namespaces and plugins:
   Namespace: | Plugins:
   -----------------------
   djscp      | ['EXAMPLE']
   
   
   
   Currently use: djscp:EXAMPLE as analyzer.
   
   Done.
   
   ```
   
   当前面的所有设置都完成后，便可以键入 'download' 或者 'batch' 去下载你想要的同人志。

## 如何创建你的插件

1. 安装 djsc framework.
2.  从 djscollect.BasePlugin导入AbstractPlugin和其他内容，并重写下面的所有抽象方法。

AbstractPlugin中的抽象所有方法，需要严格遵守输出类型（输入类型任意）。:

| Method              | Input Type               | Output type | Description                                                  |
| ------------------- | ------------------------ | ----------- | ------------------------------------------------------------ |
| save_url_from_input | List                     | Bool        | 从用户输入加载url                                            |
| get_ids_from_urls   | None                     | List        | 从url生成独立id                                              |
| next_book           | None                     | Bool        | 令下一本同人志数据用于分析                                   |
| prepare_for_analyse | requests.models.Response | Bool        | 用Librarian类去下载html用于分析                              |
| analyse_title       | None                     | Tuple       | 返回一个含三个元素的元组，包含 (id, index title, origin title) |
| analyse_metadata    | None                     | Dict        | return metadata as a dict                                    |
| analyse_pic_urls    | None                     | List        | 返回一个含该同人志的所有图片url的列表                        |