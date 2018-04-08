#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Iñaki Garitano (igaritano@garitano.org)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import subprocess
import pyinotify
import time
import argparse
import logging
from logging.handlers import RotatingFileHandler
from systemd.journal import JournalHandler


# Constants
__app_name__ = 'dropbox_include.py'
__version__ = '1.0'


# Global variables
logger = None
logger_level = 'WARNING'
logger_method = 'console'
logger_name = 'dropbox_include'
logger_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger_maxBytes = 10240
logger_backupCount = 10
logger_filename = '/var/log/dropbox/dropbox_include.log'
config_file = '~/.config/dropbox/dropbox_include.conf'
dropbox_path = '~/Dropbox'
dropbox_cache = '.dropbox.cache'
dropbox_exclude_add_command = 'dropbox exclude add'
dropbox_exclude_list_command = 'dropbox exclude list'
dropbox_exclude_remove_command = 'dropbox exclude remove'
include_directory_config_files = []
include_directory_list = []
old_config_file = ''


# Functions
def setLogger():

    # Global variables
    global logger
    global logger_method
    global logger_name
    global logger_level
    global logger_format
    global logger_filename
    global logger_maxBytes
    global logger_backupCount

    formatter = logging.Formatter(logger_format)

    if logger is None:
        logger = logging.getLogger(logger_name)
    else:
        logger.debug('logger reconfiguration')

        for logger_handler in logger.handlers[:]:
            logger.removeHandler(logger_handler)
        logger = logging.getLogger(logger_name)

    if logger_method == 'journal':
        logger.addHandler(JournalHandler())
        logger.handlers[-1].setFormatter(formatter)
    elif logger_method == 'file':
        handler = RotatingFileHandler(
            logger_filename,
            maxBytes=logger_maxBytes,
            backupCount=logger_backupCount)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        logger.addHandler(logging.StreamHandler())
        logger.handlers[-1].setFormatter(formatter)

    logger.setLevel(logger_level)

    logger.debug('logger configured')

    # setLogger function ends here.
    # -----------------------------


def confInclude(line, begin_line):
    '''
    This function returns the file path of the include option.
    '''

    logger.debug('Configuration file - Include line: '
                 + str(line))

    # Local variables
    space = False
    space_position = 0
    variable = ''

    for position, character in enumerate(line[begin_line:]):
        if character == ' ':
            space = True
        if space and not character == ' ':
            space_position = position + begin_line
            break

    variable = line[space_position:]

    return variable

    # confInclude function ends here.
    # -------------------------------


def confAssign(line, begin_line):
    '''
    This function returns the value after the equal sign or character.
    '''

    logger.debug('Configuration file - Assign line: '
                 + str(line))

    # Local variables
    equal_sign = False
    last_position = 0
    assign_position = 0
    variable = ''

    for position, character in enumerate(line[begin_line:]):
        if character == '=' or character == ':':
            equal_sign = True
            last_position = position
        if equal_sign and position > last_position and not character == ' ':
            assign_position = position + begin_line
            break

    variable = line[assign_position:]

    return variable

    # confInclude function ends here.
    # -------------------------------


def configuration(config_file):
    '''
    This function evaluates the configuration file and sets all global
    variables.
    '''

    logger.debug('Configuration file: '
                 + str(config_file))

    # Global variables
    global include_directory_config_files
    global dropbox_path
    global dropbox_cache
    global include_directory_list
    global dropbox_exclude_add_command
    global dropbox_exclude_list_command
    global dropbox_exclude_remove_command
    global logger_method
    global logger_name
    global logger_level
    global logger_format
    global logger_filename
    global logger_maxBytes
    global logger_backupCount

    include_directory_config_files = []
    include_directory_list = []

    # Local variables
    content = ''
    directory = ''
    begin_line = 0

    if os.path.exists(os.path.expanduser(config_file)):
        with open(os.path.expanduser(config_file), 'r') as file:
            try:
                content = file.read()
                file.close()
            except IOError:
                print("IOError")

    if len(content):
        for line in content.split('\n'):
            begin_line = 0
            if len(line) > 0:
                if line[0] == ' ':
                    for position, character in enumerate(line):
                        if not character == ' ':
                            begin_line = position
                            break

                if line[begin_line:].startswith('include'):
                    include_directory_config_files.append(confInclude(
                        line, begin_line))
                elif line[begin_line:].startswith('dropbox_path'):
                    dropbox_path = confAssign(line, begin_line)
                elif line[begin_line:].startswith('dropbox_cache'):
                    dropbox_cache = confAssign(line, begin_line)
                elif line[begin_line:]\
                        .startswith('dropbox_exclude_add_command'):
                    dropbox_exclude_add_command = confAssign(line, begin_line)
                elif line[begin_line:]\
                        .startswith('dropbox_exclude_list_command'):
                    dropbox_exclude_list_command = confAssign(line, begin_line)
                elif line[begin_line:]\
                        .startswith('dropbox_exclude_remove_command'):
                    dropbox_exclude_remove_command = confAssign(
                        line, begin_line)
                elif line[begin_line:].startswith('logger_method'):
                    logger_method = confAssign(line, begin_line)
                elif line[begin_line:].startswith('logger_name'):
                    logger_name = confAssign(line, begin_line)
                elif line[begin_line:].startswith('logger_level'):
                    logger_level = confAssign(line, begin_line)
                elif line[begin_line:].startswith('logger_format'):
                    logger_format = confAssign(line, begin_line)
                elif line[begin_line:].startswith('logger_filename'):
                    logger_filename = confAssign(line, begin_line)
                elif line[begin_line:].startswith('logger_maxBytes'):
                    logger_maxBytes = confAssign(line, begin_line)
                elif line[begin_line:].startswith('logger_backupCount'):
                    logger_backupCount = confAssign(line, begin_line)
                else:
                    logger.debug(str(line))

    content = ''

    for include_directory_config_file in include_directory_config_files:

        logger.debug('Include directories configuration file: '
                     + str(include_directory_config_file))

        directory = os.path.dirname(os.path.expanduser(config_file))
        if os.path.exists(os.path.join(directory,
                                       include_directory_config_file)):
            with open(os.path.join(directory,
                                   include_directory_config_file),
                      'r') as file:
                try:
                    content = file.read()
                    file.close()
                except IOError:
                    print("IOError")

            if len(content):
                for line in content.split('\n'):
                    if not line == '' \
                       and not line.startswith('#') \
                       and not line.startswith(';'):
                        directory = os.path.join(
                            os.path.expanduser(dropbox_path), line)
                        include_directory_list.append(directory)

    include_directory_list.sort()

    logger.debug('Configuration file settings:')
    logger.debug('logger_level: ' + str(logger_level))
    logger.debug('logger_method: ' + str(logger_method))
    logger.debug('logger_name: ' + str(logger_name))
    logger.debug('logger_format: ' + str(logger_format))
    logger.debug('logger_maxBytes: ' + str(logger_maxBytes))
    logger.debug('logger_backupCount: ' + str(logger_backupCount))
    logger.debug('logger_filename: ' + str(logger_filename))
    logger.debug('config_file: ' + str(config_file))
    logger.debug('dropbox_path: ' + str(dropbox_path))
    logger.debug('dropbox_cache: ' + str(dropbox_cache))
    logger.debug('dropbox_exclude_add_command: ' +
                 str(dropbox_exclude_add_command))
    logger.debug('dropbox_exclude_list_command: ' +
                 str(dropbox_exclude_list_command))
    logger.debug('dropbox_exclude_remove_command: ' +
                 str(dropbox_exclude_remove_command))
    logger.debug('include_directory_config_files: ' +
                 str(include_directory_config_files))

    # configuration function ends here.
    # ---------------------------------


def parse_arguments():
    '''
    This function evaluates command line arguments and sets all global
    variables.
    '''

    logger.debug('Parse command line arguments')

    # Global variables
    global config_file
    global dropbox_path
    global dropbox_cache
    global dropbox_exclude_add_command
    global dropbox_exclude_list_command
    global dropbox_exclude_remove_command
    global logger_method
    global logger_level
    global logger_format
    global logger_filename

    parser = argparse.ArgumentParser()

    # parser.add_argument('', action='store', dest='', help='')
    parser.add_argument('-f', action='store',
                        dest='config_file',
                        help='Configuration file')
    parser.add_argument('--config_file', action='store',
                        dest='config_file',
                        help='Configuration file')
    parser.add_argument('-c', action='store',
                        dest='dropbox_cache',
                        help='Dropbox cache folder')
    parser.add_argument('--cache', action='store',
                        dest='dropbox_cache',
                        help='Dropbox cache folder')
    parser.add_argument('-p', action='store',
                        dest='dropbox_path',
                        help='Dropbox path')
    parser.add_argument('--dropbox_path', action='store',
                        dest='dropbox_path',
                        help='Dropbox path')
    parser.add_argument('-a', action='store',
                        dest='dropbox_exclude_add_command',
                        help='Dropbox exclude add command')
    parser.add_argument('--exclude_add', action='store',
                        dest='dropbox_exclude_add_command',
                        help='Dropbox exclude add command')
    parser.add_argument('-l', action='store',
                        dest='dropbox_exclude_list_command',
                        help='Dropbox exclude list command')
    parser.add_argument('--exclude_list', action='store',
                        dest='dropbox_exclude_list_command',
                        help='Dropbox exclude list command')
    parser.add_argument('-r', action='store',
                        dest='dropbox_exclude_remove_command',
                        help='Dropbox exclude remove command')
    parser.add_argument('--exclude_remove', action='store',
                        dest='dropbox_exclude_remove_command',
                        help='Dropbox exclude remove command')
    parser.add_argument('--logger_method', action='store',
                        dest='logger_method',
                        help='Logger method: journal, file')
    parser.add_argument('--logger_level', action='store',
                        dest='logger_level',
                        help='Logger level: DEBUG, INFO, WARNING, ERROR, \
                        CRITICAL')
    parser.add_argument('--logger_format', action='store',
                        dest='logger_format',
                        help='Logger format. Example: 1970-01-01 00:00:00,000 \
                        - dropbox_include - WARNING - message')
    parser.add_argument('--logger_filename', action='store',
                        dest='logger_filename',
                        help='Logger filename. Full path.')
    parser.add_argument('--version', action='version',
                        version='%(prog)s' + ' ' + str(__version__))

    args = parser.parse_args()

    logger.debug('Command line arguments: '
                 + str(args))

    if args.config_file:
        config_file = args.config_file

    if args.dropbox_cache:
        dropbox_cache = args.dropbox_cache

    if args.dropbox_path:
        dropbox_path = args.dropbox_path

    if args.dropbox_exclude_add_command:
        dropbox_exclude_add_command = args.dropbox_exclude_add_command

    if args.dropbox_exclude_list_command:
        dropbox_exclude_list_command = args.dropbox_exclude_list_command

    if args.dropbox_exclude_remove_command:
        dropbox_exclude_remove_command = args.dropbox_exclude_remove_command

    if args.logger_method:
        logger_method = args.logger_method

    if args.logger_level:
        logger_level = args.logger_level

    if args.logger_format:
        logger_format = args.logger_format

    if args.logger_filename:
        logger_filename = args.logger_filename

    logger.debug('Command line arguments parse:')
    logger.debug('logger_level: ' + str(logger_level))
    logger.debug('logger_method: ' + str(logger_method))
    logger.debug('logger_name: ' + str(logger_name))
    logger.debug('logger_format: ' + str(logger_format))
    logger.debug('logger_maxBytes: ' + str(logger_maxBytes))
    logger.debug('logger_backupCount: ' + str(logger_backupCount))
    logger.debug('logger_filename: ' + str(logger_filename))
    logger.debug('config_file: ' + str(config_file))
    logger.debug('dropbox_path: ' + str(dropbox_path))
    logger.debug('dropbox_cache: ' + str(dropbox_cache))
    logger.debug('dropbox_exclude_add_command: ' +
                 str(dropbox_exclude_add_command))
    logger.debug('dropbox_exclude_list_command: ' +
                 str(dropbox_exclude_list_command))
    logger.debug('dropbox_exclude_remove_command: ' +
                 str(dropbox_exclude_remove_command))
    logger.debug('include_directory_config_files: ' +
                 str(include_directory_config_files))

    # parse_arguments function ends here.
    # -----------------------------------


def evalCurrentDirectories(path):
    '''
    This function evaluates current directories and subdirectories in a given
    directory path.
    '''

    logger.debug('Evaluate subdirectories in a given path: '
                 + str(path))

    # Local variables
    current_directories = []

    for directory, subdirectories, files in os.walk(os.path.expanduser(path),
                                                    followlinks=True):
        current_directories.append(directory)

    current_directories.sort()

    return current_directories

    # evalCurrentDirectories function ends here.
    # ------------------------------------------


def pathToDict(path):

    # Local variables
    counter = 1
    basename = ''
    basenames_list = []
    pathtodict = {}

    while os.path.basename(path):
        basename = os.path.basename(path)
        basenames_list.append(basename)
        path = os.path.dirname(path)

    basenames_list.reverse()
    for basename in basenames_list:
        pathtodict[counter] = basename
        counter += 1

    return pathtodict

    # pathToDict function ends here.
    # ------------------------------


def directoriesListToDicts(directorieslist):

    # Local variables
    directoriesDictList = []

    for directory in directorieslist:
        directoriesDictList.append(pathToDict(directory))

    return directoriesDictList

    # directoriesListToDicts function ends here.
    # ------------------------------------------


def evalToExcludeDirectories2(include_directories, current_directories):
    '''
    This function evaluates directories to be excluded comparing each current
    directory with included directories.
    '''

    logger.debug('Evaluate directories not present on a given list:'
                 + '\nInclude directory list: ' + str(include_directories)
                 + '\nDirectory list to evaluate: ' + str(current_directories))

    # Global variables
    global dropbox_path
    global dropbox_cache

    # Local variables
    include_directory_list_of_dicts = []
    current_directory_list_of_dicts = []
    aux_dict = {}
    exclude_directory_list_of_dicts = []
    exclude_directory_set = set()
    exclude_directory_list = []

    include_directory_list_of_dicts = directoriesListToDicts(
        include_directories)

    include_directory_list_of_dicts.append(directoriesListToDicts(
        [os.path.join(os.path.expanduser(dropbox_path), dropbox_cache)])[0])

    current_directory_list_of_dicts = directoriesListToDicts(
        current_directories)

    for current_directory in current_directory_list_of_dicts:

        mainsubdirectory = []

        for include_directory in include_directory_list_of_dicts:

            maxcounter = 0

            for counter in range(1, min(len(current_directory),
                                        len(include_directory)) + 1):

                if current_directory[counter] == include_directory[counter]:

                    maxcounter = counter

                else:

                    break

            mainsubdirectory.append(maxcounter)

        # commonalities = (number_of_in_common_directories,
        #                 (number_of_include_directory_directories,
        #                   position_in_include_directory_list_of_dicts),
        #                  number_of_current_directory_directories)
        commonalities = (max(mainsubdirectory),
                         min([(len(include_directory_list_of_dicts[position]),
                               position)
                              for position, value in
                              enumerate(mainsubdirectory)
                              if value == max(mainsubdirectory)]),
                         len(current_directory))

        if commonalities[0] == 0:

            aux_dict = {}
            aux_dict['directory'] = current_directory
            aux_dict['length'] = commonalities[2]
            exclude_directory_list_of_dicts.append(aux_dict)

        else:

            if commonalities[1][0] < commonalities[2]:
                if commonalities[0] < commonalities[1][0]:
                    aux_dict = {}
                    aux_dict['directory'] = current_directory
                    aux_dict['length'] = commonalities[0] + 1
                    exclude_directory_list_of_dicts.append(aux_dict)

            elif commonalities[1][0] == commonalities[2]:
                if commonalities[0] < commonalities[2]:
                    aux_dict = {}
                    aux_dict['directory'] = current_directory
                    aux_dict['length'] = commonalities[2]
                    exclude_directory_list_of_dicts.append(aux_dict)

            else:
                if commonalities[0] < commonalities[2]:
                    aux_dict = {}
                    aux_dict['directory'] = current_directory
                    aux_dict['length'] = commonalities[2]
                    exclude_directory_list_of_dicts.append(aux_dict)

        for entry in exclude_directory_list_of_dicts:
            print(entry)
            directory = os.sep
            for index in range(1, entry['length'] + 1):
                directory = os.path.join(directory, entry['directory'][index])
            exclude_directory_set.add(directory)

    exclude_directory_list = list(exclude_directory_set)
    exclude_directory_list.sort()

    logger.debug('To exclude directories: ' + str(exclude_directory_list))

    return exclude_directory_list

    # evalToExcludeDirectories2 function ends here.
    # ---------------------------------------------


def executeCommand(command,
                   argument_list,
                   child_working_directory):
    '''
    This function takes the command, the argument list and the
    child_working_directory path and executes the given command with the
    given arguments on the given cwd path.
    '''

    logger.debug('Execute command: '
                 + str(command)
                 + ' '
                 + str(argument_list))

    # Local variables
    args = []

    # Split the command and add to args list
    args.extend(command.split())

    # For each argument in the list, include it in the args list.
    for argument in argument_list:
        args.append(argument)

    # Execute the command with the given argument list on the given cwd path

    logger.info(str(args))

    p = subprocess.Popen(args,
                         cwd=child_working_directory,
                         stdout=subprocess.PIPE)
    out, err = p.communicate()

    # Return the output of the executed command.
    return out

    # executeCommand function ends here.
    # ----------------------------------


def evalDropboxExcludeList():
    '''
    This function evaluates the list of excluded directories.
    '''

    logger.debug('Evaluate dropbox excluded directory list')

    # Global variables
    global dropbox_exclude_list_command
    global dropbox_path

    # Local variables
    dropbox_exclude_list = []
    args = []

    dropbox_exclude_list = executeCommand(
        dropbox_exclude_list_command, args, os.path.expanduser(dropbox_path))

    # Split the list considering each line as an independent directory.
    dropbox_exclude_list_aux = dropbox_exclude_list.split('\n')

    # Remove the first and the last list members which are 'Excluded: ' and ''
    try:
        dropbox_exclude_list_aux.pop(0)
        dropbox_exclude_list_aux.pop(-1)
    except IndexError:
        print("IndexError")

    # Return the list of directories.
    return dropbox_exclude_list_aux

    # evalDropboxExcludeList function ends here.
    # ------------------------------------------


def evalToUnexcludeDirectories(excluded_directories, include_directory_list):
    '''
    This function evaluates each excluded directory against include
    directories and devices whether the directory should be unexcluded or not.
    '''

    logger.debug('Evaluate directories which should not be excluded')

    # Global variables
    global dropbox_path

    # Local variables
    include_list = []
    directories = []
    in_common = ''
    unexclude_set = set()
    unexclude_list = []

    for include in include_directory_list:
        include_list.append(
            include[len(os.path.expanduser(dropbox_path))+1:].lower())

    include_list.sort()

    for directory in excluded_directories:

        for include_directory in include_list:

            directories = []
            directories.append(directory.lower())
            directories.append(include_directory)

            in_common = os.path.commonprefix(directories)

            if len(in_common):

                if len(directories[0]) >= len(directories[1]):

                    if directories[0][:len(directories[1])] == directories[1]:

                        if directories[0].startswith(directories[1] + os.sep) \
                           or (directories[0] + os.sep).startswith(
                                directories[1] + os.sep):

                            unexclude_set.add(directories[0])

                else:

                    if directories[0] == directories[1][:len(directories[0])]:

                        if directories[1].startswith(directories[0] + os.sep) \
                           or (directories[1] + os.sep).startswith(
                                directories[0] + os.sep):

                            unexclude_set.add(directories[0])

    unexclude_list = list(unexclude_set)

    unexclude_list.sort()

    logger.debug('Directories to unexclude: '
                 + str(unexclude_list))

    return unexclude_list

    # evalToUnexcludeDirectories function ends here.
    # ----------------------------------------------


def evalExcludeInclude(directory_list):
    '''
    Function that inotify calls whenever a new directory is created under
    monitored directory path.
    '''

    logger.debug('Configure the entire environment, and go through include exclude \
                 sequence')

    logger.info('Directory(ies) to check: '
                + str(directory_list))

    # Local variables
    exclude_directories = []

    configuration(config_file)

    exclude_directories = evalToExcludeDirectories2(
        include_directory_list, directory_list)

    if len(exclude_directories):
        out = executeCommand(dropbox_exclude_add_command,
                             exclude_directories,
                             os.path.expanduser(dropbox_path))

    logger.info('Entering exclude and unexclude sequence')

    dropbox_exclude_list = evalDropboxExcludeList()

    unexclude_list = evalToUnexcludeDirectories(
        dropbox_exclude_list, include_directory_list)

    if unexclude_list:
        out = executeCommand(dropbox_exclude_remove_command,
                             unexclude_list,
                             os.path.expanduser(dropbox_path))

    # evalExcludeInclude function ends here.
    # --------------------------------------

# Functions - END
# ---------------


# Classes
class EventHandler(pyinotify.ProcessEvent):
    '''
    Class which is called by inotify.
    '''

    # Define a function for folder and file creation process
    def process_IN_CREATE(self, event):
        '''
        Function which is called by inotify whenever a new directory is
        created.
        '''

        logger.debug('New directory detected: '
                     + str(event.pathname))

        # Local variables
        directory_list = []

        directory_list.append(event.pathname)

        evalExcludeInclude(directory_list)

    # process_IN_CREATE function ends here.
    # -------------------------------------


# EventHandler class definition ends here.
# ----------------------------------------


# -----------------------------------------------------------------------------
#                                     Main
# -----------------------------------------------------------------------------

def main():

    setLogger()

    logger.warning('Starting ' + __app_name__ + ' ' + __version__)

    # Parse configuration file

    logger.debug('Parse ' + str(config_file) + ' configuration file if exists')

    configuration(config_file)

    logger.debug('Set logger with default settings')
    setLogger()

    # argparse section

    logger.debug('Parse command line arguments')
    old_config_file = config_file
    parse_arguments()

    if not config_file == old_config_file:
        logger.debug('Set logger with configuration file settings')
        configuration(config_file)
        setLogger()

    # end of argparse section

    logger.info('Entering initial exclude and unexclude sequence')

    current_directories = evalCurrentDirectories(dropbox_path)

    logger.debug('Initial dropbox_path directories: '
                 + str(current_directories))

    exclude_directories = evalToExcludeDirectories2(
        include_directory_list,
        current_directories)

    logger.debug('To exclude directories: '
                 + str(exclude_directories))

    if len(exclude_directories):
        out = executeCommand(dropbox_exclude_add_command,
                             exclude_directories,
                             os.path.expanduser(dropbox_path))

    dropbox_exclude_list = evalDropboxExcludeList()

    logger.debug('Initial already excluded directories: '
                 + str(dropbox_exclude_list))

    unexclude_list = evalToUnexcludeDirectories(
        dropbox_exclude_list,
        include_directory_list)

    logger.debug('Initial directories to unexclude: '
                 + str(unexclude_list))

    if unexclude_list:
        out = executeCommand(dropbox_exclude_remove_command,
                             unexclude_list,
                             os.path.expanduser(dropbox_path))

    logger.info('Leaving initial exclude and unexclude sequence')

    # -------------------------------------------------------------------------

    logger.info('Entering inotify setup')

    # Continue running until user stops it
    # If dropbox creates a new directory or subdirectory inside the main
    # dropbox folder, check whether it should be excluded or not and do
    # it so.

    # The watch manager stores the watches and provides operations on watches
    wm = pyinotify.WatchManager()

    # Watched events: watch whether a new directory is created
    mask = pyinotify.IN_CREATE | pyinotify.IN_ISDIR

    # Associate this WatchManager with a ThreadedNotifier
    notifier = pyinotify.ThreadedNotifier(wm, EventHandler())

    # Start the notifier from a new thread, without doing anything as no
    # directory or file are currently monitored yet.
    notifier.start()

    # Add a new watch on folder to monitor for watched events.
    wm.add_watch(os.path.expanduser(dropbox_path),
                 mask, rec=True, auto_add=True)

    logger.info('Entering inotify loop')

    while True:
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            logger.warning('Leaving due to KeyboardInterrupt')
            notifier.stop()
            break
        except:
            logger.warning('Leaving due to kill signal')
            notifier.stop()
            raise

# New functions
# -------------


if __name__ == '__main__':

    main()
