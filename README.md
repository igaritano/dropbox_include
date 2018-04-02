## Description
dropbox_include.py is designed for GNU/Linux users. It provides *exclude by default* functionality by defining directories to be included. Everytime a new folder is created under dropbox main directory it checks whether the folder should be excluded or not. Moreover, directories to be included can be defined without having to restart the application/service. New settings will be applied everytime a new folder is created under dropbox main directory.

## Requirements
This software requires the following python libraries:
* pyinotify
* systemd.journal
* os
* subprocess
* time
* argparse
* logging

## Installation
dropbox_include.py is designed to be installed under .dropbox-dist directory which is usually placed under user home folder. However, it could be placed in any other directory.
It requires a configuration file *dropbox_include.conf* which by default should be placed under:
* */user home folder/*.config/dropbox/
In addition, by default, other two configuration files are defined:
* dropbox_never_exclude_directories.conf
* dropbox_include_directories.conf

In order to install as a system service, the following two system service definitions are included:
* dropbox@.service
* dropbox_include@.service

Those system services should be placed under */etc/systemd/system/* folder, enabled and started.
```shell
# systemctl enable dropbox@username
# systemctl enable dropbox_include@username

# systemctl start dropbox@username
# systemctl start dropbox_include@username
```