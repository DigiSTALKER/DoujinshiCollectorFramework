# Doujinshi Collector Framework
Collecting Doujinshis from Internet  
[中文文档](https://github.com/Hochikong/DoujinshiCollectorFramework/blob/master/README_zhCN.md)

## Installation

### requirements:
Python>=3.6

The following dependencies are necessary:

pampy>=0.3.0  
requests>=2.23.0  
pytest>=5.4.3  
stevedore>=2.0.0  
PyYAML>=5.3.1  
lxml>=4.5.0  
bs4>=0.0.1  
pysocks>=1.7.1  

### Install via pip:

Download .whl file from github releases: 

```
pip install djsc-0.0.x-py3-none-any.whl
```

### Windows Installer(With plugins):

Download the exe from github releases. Just double click it.

## How to use

The following example is running on Windows 10:

1. Copy the config_demo.ini from github repository, edit the configuration file:

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

   I use shadowsocksr as proxy on Windows, it listens on port 5082.

   Max workers is the maximum workers for concurrent.futures.ThreadPoolExecutor().

   Timeout is for requests.get()

   Plugins setting depends on what plugin you have installed. For example, I build a plugin package call "djscp", the "entry_points" setting of setup.py, as you see below:

    

   ```
   entry_points={
           'djscp': [            // entry point
               'A = djsplugins.a:A',  // name = package.file:Class
               'B = djsplugins.b:B',
           ],
       },
   ```

   so, you plugins setting in config_demo.ini should like this:

   ```
   [Main]
   plugins = djscp:A, djscp:B
   ```

2. Run the djsc.exe

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
   
   You can use --cfg load your config_demo.ini or load that file later:
   
   
   
   ```
   PS H:\> djsc.exe
   Welcome to use Doujinshi Collector v0.0.x Enter 'help' for useful information.
   
   DJSC|#> load_cfg config_demo.ini
   

   Load done.

   Done.
   ```
   
   You can enter 'help' for useful information:
   
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

   bulk_meta URLS_FILE_PATH    -- Download a bunch of doujinshis' metadata by reading a yaml format file.

   pwd                          -- Just pwd.
   
   reset                        -- Reset all configurations.
   
   cd                           -- Change path.
   
   quit                         -- Exit the program.

   
   Done.
   
   ```
   
   If you didn't load any plugin as analyzer, enter 'show plugins' will only return those plugins in config_demo.ini:
   
   ```
   DJSC|#> show_plugins
   
   
   All registered namespaces and plugins:
   Namespaces: | Plugins:
   -----------------------
   djscp      | ['EXAMPLE']
   

   
   Done.
   
   ```
   
   Use 'load plugin' to load:
   
   ```
   DJSC|#> load_plugin djscp:EXAMPLE
   
   
   Plugin djscp:EXAMPLE apply done.
   
   Done.
   
   DJSC|djscp:EXAMPLE> show_plugins
   
   
   All registered namespaces and plugins:
   Namespace: | Plugins:
   -----------------------
   djscp      | ['EXAMPLE']
   
   
   
   Currently use: djscp:EXAMPLE as analyzer.
   
   Done.
   
   ```
   
   After all these preparations, you can use 'download' or 'batch' to download any doujinshis you like.

## How to write your own plugin

1. Install djsc framework.
2. Import 'AbstractPlugin' and other contents from djscollect.BasePlugin and rewrite all abstract methods.

All abstract methods in AbstractPlugin, all input types are depend on you, but all output types should follow the table below:

| Method              | Input Type               | Output type | Description                                                  |
| ------------------- | ------------------------ | ----------- | ------------------------------------------------------------ |
| save_url_from_input | List                     | Bool        | load urls from input                                         |
| get_ids_from_urls   | None                     | List        | generate id from url                                         |
| next_book           | None                     | Bool        | set next doujinshi to be analyzed                            |
| prepare_for_analyse | requests.models.Response | Bool        | use Librarian class to download html for analyse             |
| analyse_title       | None                     | Tuple       | return a tuple which contains three elements, (id, index title, origin title) |
| analyse_metadata    | None                     | Dict        | return metadata as a dict                                    |
| analyse_pic_urls    | None                     | List        | return a list, it contains all pictures' url of a doujinshi  |