## Description
dropbox_include.py is designed for GNU/Linux users. It provides *exclude by default* functionality by defining directories to be included. Every time a new folder is created under dropbox main directory it checks whether the folder should be excluded or not. Moreover, directories to be included can be defined without having to restart the application/service. New settings will be applied every time a new folder is created under dropbox main directory.

## Requirements
Dropbox itself. Install it from (More details underneath):
* [Dropbox](https://www.dropbox.com/install)

This software requires the following python libraries:
* pyinotify (python-pyinotify)
* systemd.journal (python-systemd)
* os
* subprocess
* time
* argparse
* logging

## Installation
dropbox_include.py is designed to be installed under .dropbox-dist directory which is usually placed under user home folder *~/*. However, it could be placed in any other directory.
It requires a configuration file *dropbox_include.conf* which by default should be placed under:
* *~/*.config/dropbox/

In addition, by default, other two configuration files are defined:
* dropbox_never_exclude_directories.conf
* dropbox_include_directories.conf

In case of a common user
```shell
root@hostname:~# apt install python-pyinotify python-systemd
username@hostname:~$ cd
username@hostname:~$ git clone https://github.com/igaritano/dropbox_include.git
username@hostname:~$ mv ~/dropbox_include/dropbox_include.py ~/.dropbox-dist/
username@hostname:~$ mv ~/dropbox_include/.config/* ~/.config/
```
or in case of running as root
```shell
root@hostname:~# apt install python-pyinotify python-systemd
root@hostname:~# cd
root@hostname:~# git clone https://github.com/igaritano/dropbox_include.git
root@hostname:~# mv ~/dropbox_include/dropbox_include.py ~/.dropbox-dist/
root@hostname:~# mv ~/dropbox_include/.config ~/
```

Before running *dropbox_include.py* check whether the setting are correct:
```shell
username@hostname:~$ vi ~/.config/dropbox/dropbox_include.conf
```
or
```shell
root@hostname:~# vi ~/.config/dropbox/dropbox_include.conf
```

In order to install as a system service (systemd), different system service definitions are included

There are two main group of services definitions:
* Those designed for unprivileged/common users
   * dropbox@.service
   * dropbox_headless@.service
   * dropbox_include@.service
   * dropbox_include_headless@.service
* Those designed for root/administrator user (they include *root* in their name)
   * dropbox@root.service
   * dropbox_headless@root.service
   * dropbox_include@root.service
   * dropbox_include_headless@root.service

Moreover, depending on the target host type, whether the target host has a graphical interface or whether is a headless host, there are two additional subgroups:
* Those which include *headless* in their name
   * dropbox_headless@.service
   * dropbox_include_headless@.service
   * dropbox_headless@root.service
   * dropbox_include_headless@root.service
* Those who do not
   * dropbox@.service
   * dropbox_include@.service
   * dropbox@root.service
   * dropbox_include@root.service

Unprivileged/common system services, should be placed under *~/.config/systemd/user/* folder, enabled and started.
* In case of a graphical interface host:
```shell
username@hostname:~$ systemctl enable --user dropbox@username
username@hostname:~$ systemctl enable --user dropbox_include@username

username@hostname:~$ systemctl start --user dropbox@username
username@hostname:~$ systemctl start --user dropbox_include@username
```
* In case of a headless host:
```shell
username@hostname:~$ systemctl enable --user dropbox_headless@username
username@hostname:~$ systemctl enable --user dropbox_include_headless@username

username@hostname:~$ systemctl start --user dropbox_headless@username
username@hostname:~$ systemctl start --user dropbox_include_headless@username
```

Otherwise, if services are going to be executed as root, place *root.service* definitions under */etc/systemd/system/* folder, enable and start them.
* In case of a graphical interface host:
```shell
root@hostname:~# mv ~/dropbox_include/etc/systemd/system/* /etc/systemd/system/
root@hostname:~# systemctl enable dropbox@root.service
root@hostname:~# systemctl enable dropbox_include@root.service

root@hostname:~# systemctl start dropbox@root.service
root@hostname:~# systemctl start dropbox_include@root.service
```
* In case of a headless host:
```shell
root@hostname:~# mv ~/dropbox_include/etc/systemd/system/* /etc/systemd/system/
root@hostname:~# systemctl enable dropbox_headless@root.service
root@hostname:~# systemctl enable dropbox_include_headless@root.service

root@hostname:~# systemctl start dropbox_headless@root.service
root@hostname:~# systemctl start dropbox_include_headless@root.service
```

### Dropbox installation steps
These are dropbox installation steps (64 bits):
* Download the dropbox python script, place it under */usr/bin/*, install dependencies and install dropbox binary.
```shell
root@hostname:~# wget https://www.dropbox.com/download?dl=packages/dropbox.py -O ~/dropbox
root@hostname:~# mv ~/dropbox /usr/bin/
root@hostname:~# chmod +x /usr/bin/dropbox
root@hostname:~# apt install python-gpgme
```

* Run dropbox daemon in order to activate it. In case of common user
```shell
username@hostname:~$ dropbox start -i
username@hostname:~$ dropbox stop
username@hostname:~$ ~/.dropbox-dist/dropboxd
This computer isn't linked to any Dropbox account...
Please visit https://www.dropbox.com/cli_link_nonce?nonce=*activation_code* to link this device.
This computer is now linked to Dropbox. Welcome *dropbox_account*
^C
```
* or in case of root user
    
```shell
root@hostname:~# dropbox start -i
root@hostname:~# dropbox stop
root@hostname:~# ~/.dropbox-dist/dropboxd
This computer isn't linked to any Dropbox account...
Please visit https://www.dropbox.com/cli_link_nonce?nonce=*activation_code* to link this device.
This computer is now linked to Dropbox. Welcome *dropbox_account*
^C
```

* Link to desired dropbox account by accessing to the URL provided by dropbox daemon and login in with desired dropbox account.
    * If successful the daemon will output the following message: *This computer is now linked to Dropbox. Welcome dropbox_account*


## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
