"""
The mode for working with the BBC micro:bit. Conatains most of the origial
functionality from Mu when it was only a micro:bit related editor.

Copyright (c) 2015-2017 Nicholas H.Tollervey and others (see the AUTHORS file).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
import os.path
import logging
import semver
import time
import re
import platform
import subprocess
import configparser
from tokenize import TokenError
from mu.logic import HOME_DIRECTORY
from mu.contrib import uflash, espfs
from mu.modes.api import ESP_APIS, SHARED_APIS
from mu.modes.base import MicroPythonMode
from mu.interface.panes import CHARTS
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

# We can run without nudatus
can_minify = True
try:
    import nudatus
except ImportError:  # pragma: no cover
    can_minify = False

logger = logging.getLogger(__name__)


class DeviceFlasher(QThread):
    """
    Used to flash the micro:bit in a non-blocking manner.
    """
    # Emitted when flashing the micro:bit fails for any reason.
    on_flash_fail = pyqtSignal(str)

    def __init__(self, paths_to_microbits, python_script, path_to_runtime):
        """
        The paths_to_microbits should be a list containing filesystem paths to
        attached micro:bits to flash. The python_script should be the text of
        the script to flash onto the device. The path_to_runtime should be the
        path of the hex file for the MicroPython runtime to use. If the
        path_to_runtime is None, the default MicroPython runtime is used by
        default.
        """
        QThread.__init__(self)
        self.paths_to_microbits = paths_to_microbits
        self.python_script = python_script
        self.path_to_runtime = path_to_runtime

    def run(self):
        """
        Flash the device.
        """
        try:
            uflash.flash(paths_to_microbits=self.paths_to_microbits,
                         python_script=self.python_script,
                         path_to_runtime=self.path_to_runtime)
        except Exception as ex:
            # Catch everything so Mu can recover from all of the wide variety
            # of possible exceptions that could happen at this point.
            logger.error(ex)
            self.on_flash_fail.emit(str(ex))


class DeviceRunner(QThread):

    on_error = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.running = False
        
    def set(self, filename, content, serial):
        self.filename = filename
        self.content = content
        self.serial = serial

    def run(self):
        try:
            self.running = True
            if self.filename is None:
                result, err = espfs.run_content(self, content=self.content, serial=self.serial)
                # print(result, err)
            else:
                result, err = espfs.run_py(self, filename=self.filename, serial=self.serial)
                # print(result, err)
            if result == 1:
                self.on_error.emit(str(err, "utf8"))
                self.running = False
            elif result == 2:
                size = re.findall("\d+", str(err, "utf8"))[0]
                self.on_error.emit(_("MemoryError: memory allocation failed,"
                                     " allocating {} bytes").format(size))
                self.running = False
        except Exception as ex:
            logger.error(ex)

    def stop(self):
        self.running = False


class DeviceRestorer(QThread):

    on_info = pyqtSignal(str)
    on_info10 = pyqtSignal(str)
    on_restore = pyqtSignal()
    on_start = pyqtSignal()
    on_finish = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.running = False

    def set(self, _port, _home):
        self.port = _port
        self.home = _home

    def run(self):
        try:
            self.running = True
            lib_path = os.path.join(self.home, '__config__', 'target.bin')
            if platform.system() == "Darwin":
                app_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
                app_dir = os.path.dirname(os.path.abspath(app_path))
                app_dir = os.path.join(app_dir, "../Resources")
                if not os.path.isfile(lib_path):
                    lib_path = os.path.join(app_dir, 'target.bin')
                cmd = '"{}/python/bin/python3" "{}/app_packages/esptool.py" -p {} -b 1152000 write_flash -ff=40m -fm=dio -fs=8MB 0x0000 "{}"'.format(app_dir, app_dir, self.port, lib_path)
            else:
                app_dir = os.path.split( os.path.realpath( sys.argv[0] ) )[0]
                # app_dir = "D:\\github\\mu-mpython\\build\\nsis"
                if not os.path.isfile(lib_path):
                    lib_path = os.path.join(app_dir, 'target.bin')
                cmd = '"{}\\Python\\python.exe" "{}\\pkgs\\esptool.py" -p {} -b 1152000 write_flash -ff=40m -fm=dio -fs=8MB 0x0000 "{}"'.format(app_dir, app_dir, self.port, lib_path)
                # print(cmd)

            # self.on_info.emit(app_dir)
            
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while p.poll() is None:
                line = p.stdout.readline()
                if line.startswith(b'\'esptool\' '):
                    self.on_info.emit('Please install Python 3.6 and esptool first, then run this command.')
                elif line.startswith(b'Serial port COM'):
                    self.on_info10.emit('In the next 15 seconds, please press the Key A and Key B at once then loose both keys')
                # elif line.startswith(b'A fatal error occurred: Failed to connect to Espressif device:'):
                # elif line.startswith(b'A fatal error occurred: MD5 of file does not match data in flash!'):
                elif line.startswith(b'A fatal error occurred: '):
                    self.on_info.emit('Recovery failed')
                elif line.startswith(b'Compressed '):
                    self.on_info.emit('Start to recovery the firmware, it took about 30 seconds to recovery...')
                    self.on_start.emit()
                elif line.startswith(b'Hard resetting via RTS pin...'):
                    self.on_finish.emit()
                # print(line)
            # print("run over")
            self.running = False
            self.on_restore.emit()
        except Exception as ex:
            logger.error(ex)

    def stop(self):
        self.running = False


class DeviceRestoreTimer(QThread):

    on_info = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.running = False

    def run(self):
        time.sleep(1)
        self.running = True
        count = 0
        max = 35
        while count < max:
            if self.running:
                time.sleep(1)
                self.on_info.emit(_('Recovering {} %').format(str(count * 3)))
                if count < 33:
                    count += 1
            else:
                time.sleep(1)
                self.on_info.emit(_('Recovering {} %').format("100"))
                # time.sleep(1)
                # self.on_info.emit(_('Recovery complete'))
                return

    def stop(self):
        self.running = False


class FileManager(QObject):
    """
    Used to manage micro:bit filesystem operations in a manner such that the
    UI remains responsive.

    Provides an FTP-ish API. Emits signals on success or failure of different
    operations.
    """
    # Emitted when the tuple of files on the mPython is known.
    on_list_files = pyqtSignal(tuple, str)
    # Emitted when the file with referenced filename is got from the mPython.
    on_get_file = pyqtSignal(str)
    # Emitted when the file with referenced filename is got from the mPython.
    on_load_py = pyqtSignal(str)
    # Emitted when the file with referenced filename is put onto the mPython.
    on_put_file = pyqtSignal(str)
    # Emitted when the file with referenced filename is loaded from the mPython.
    on_load_file = pyqtSignal(str)
    # Emitted when the file with referenced filename is running from the mPython.
    on_run_file = pyqtSignal(str)
    # Emitted when the file with referenced filename is deleted from the mPython.
    on_delete_file = pyqtSignal(str)
    # Emitted when Mu is unable to list the files on the mPython.
    on_list_fail = pyqtSignal()
    # Emitted when the referenced file fails to be got from the mPython.
    on_get_fail = pyqtSignal(str)
    # Emitted when the referenced file fails to be put onto the mPython.
    on_put_fail = pyqtSignal(str)
    # Emitted when the referenced file fails to be opened from the mPython.
    on_load_start = pyqtSignal(str)
    on_load_fail = pyqtSignal(str)
    # Emitted when the referenced file fails to be running from the mPython.
    on_run_fail = pyqtSignal(str)
    # Emitted when the referenced file fails to be deleted from the mPython.
    stop_py = pyqtSignal()
    on_delete_fail = pyqtSignal(str)
    on_set_default = pyqtSignal(str)
    on_set_default_fail = pyqtSignal(str)
    on_write_lib_start = pyqtSignal()
    on_write_lib = pyqtSignal()
    on_write_lib_fail = pyqtSignal(str)
    on_rename_start = pyqtSignal()
    on_rename = pyqtSignal(str, str)
    on_rename_fail = pyqtSignal(str)
    on_run_content = pyqtSignal(str)
    on_info_start = pyqtSignal(str, int)
    
    def __init__(self):
        super(QObject, self).__init__()
        self.device_runner = DeviceRunner()
        self.device_restorer = DeviceRestorer()
        self.restorer_timer = DeviceRestoreTimer()
        self.stop_py.connect(self.device_runner.stop)
        self.device_runner.on_error.connect(self.on_error)
        self.device_restorer.on_info.connect(self.on_info)
        self.device_restorer.on_info10.connect(self.on_info10)
        self.device_restorer.on_restore.connect(self.on_start)
        self.device_restorer.on_start.connect(self.on_restore_start)
        self.device_restorer.on_finish.connect(self.on_restore_finish)
        self.restorer_timer.on_info.connect(self.on_info)

    def on_start(self):
        """
        Run when the thread containing this object's instance is started so
        it can emit the list of files found on the connected micro:bit.
        """
        self.ls()

    def on_error(self, err):
        self.on_run_fail.emit(err)

    def on_info(self, info):
        self.on_info_start.emit(info, 2)
        
    def on_info10(self, info):
        self.on_info_start.emit(info, 15)

    def on_restore_start(self):
        self.restorer_timer.start()

    def on_restore_finish(self):
        self.restorer_timer.stop()

    def ls(self):
        """
        List the files on the micro:bit. Emit the resulting tuple of filenames
        or emit a failure signal.
        """
        try:
            result = tuple(espfs.ls())
            #dft_file = espfs.get_default()
            #self.on_list_files.emit(result, bytes.decode(dft_file))
            self.on_list_files.emit(result, "")
        except Exception as ex:
            logger.exception(ex)
            self.on_list_fail.emit()

    def get(self, esp_filename, local_filename):
        """
        Get the referenced mPython filename and save it to the local
        filename. Emit the name of the filename when complete or emit a
        failure signal.
        """
        try:
            self.stop_py.emit()
            time.sleep(0.5)
            out = espfs.get(esp_filename)
            with open(local_filename, 'wb') as f:
                f.write(out)
            self.on_get_file.emit(esp_filename)
        except Exception as ex:
            logger.error(ex)
            self.stop_py.emit()
            self.on_get_fail.emit(esp_filename)

    def put(self, local_filename):
        """
        Put the referenced local file onto the filesystem on the micro:bit.
        Emit the name of the file on the micro:bit when complete, or emit
        a failure signal.
        """
        try:
            self.stop_py.emit()
            time.sleep(0.5)
            espfs.put(local_filename, target=None)
            self.on_put_file.emit(os.path.basename(local_filename))
        except Exception as ex:
            logger.error(ex)
            self.on_put_fail.emit(local_filename)
            
    def load_py(self, esp_filename, workspace_dir):
        try:
            self.on_load_start.emit(esp_filename)
            self.stop_py.emit()
            time.sleep(1)
            out = espfs.get(esp_filename)
            if out == b'':
                self.on_load_fail.emit(_("Failed to read file '{}', please try again.").format(esp_filename))
                return
            temp_dir = os.path.join(workspace_dir, "__temp__")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            local_filename = os.path.join(temp_dir, esp_filename)
            with open(local_filename, 'wb') as f:
                f.write(out)
            self.on_load_py.emit(local_filename)
        except Exception as ex:
            logger.error(ex)
            self.on_load_fail.emit("{}".format(ex))
    
    def run_py(self, esp_filename):
        try:
            self.stop_py.emit()
            time.sleep(1)
            self.device_runner.set(esp_filename, None, None)
            self.device_runner.start()
            self.on_run_file.emit(esp_filename)
        except Exception as ex:
            logger.error(ex)
            self.on_run_fail.emit("{}".format(ex))

    def run_content(self, content):
        try:
            self.stop_py.emit()
            time.sleep(1)
            self.device_runner.set(None, content, None)
            self.device_runner.start()
            # self.on_run_file.emit(esp_filename)
        except Exception as ex:
            logger.error(ex)
            self.on_run_fail.emit("{}".format(ex))
    
    def stop_run_py(self):   
        self.stop_py.emit()

    def delete(self, esp_filename):
        """
        Delete the referenced file on the micro:bit's filesystem. Emit the name
        of the file when complete, or emit a failure signal.
        """
        try:
            self.stop_py.emit()
            time.sleep(0.5)
            espfs.rm(esp_filename)
            self.on_delete_file.emit(esp_filename)
        except Exception as ex:
            logger.error(ex)
            self.on_delete_fail.emit(esp_filename)

    def set_default(self, esp_filename):
        try:
            self.stop_py.emit()
            time.sleep(0.5)
            espfs.set_default(esp_filename, None)
            self.on_set_default.emit(esp_filename)
            #self.ls()
            espfs.soft_reboot(None)
        except Exception as ex:
            logger.error(ex)
            self.on_set_default_fail.emit("{}".format(ex))

    def write_lib(self, _home):
        try:
            self.stop_py.emit()
            time.sleep(0.5)
            self.on_write_lib_start.emit()
            libpath = os.path.join(_home, '__config__', 'mpython.py')
            if not os.path.isfile(libpath):
                app_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
                app_dir = os.path.dirname(os.path.abspath(app_path))
                if platform.system() == "Darwin":
                    libpath = os.path.join(app_dir, "../Resources/mpython.py")
                else:
                    libpath = os.path.join(app_dir, "mpython.py")
            # print(libpath)
            espfs.write_lib(libpath)
            self.on_write_lib.emit()
        except Exception as ex:
            logger.error(ex)
            self.on_write_lib_fail.emit("{}".format(ex))

    def rename(self, esp_filename, new_name):        
        try:
            self.stop_py.emit()
            time.sleep(0.5)
            self.on_rename_start.emit()
            espfs.rename(esp_filename, new_name)
            self.on_rename.emit(esp_filename, new_name)
        except Exception as ex:
            logger.error(ex)
            self.on_rename_fail.emit("{}".format(ex))

    def reset_firmware(self, _home):
        try:
            self.stop_py.emit()
            time.sleep(0.5)
            port, serial_number = espfs.find_device()
            if port is not None:
                self.device_restorer.set(port, _home)
                self.device_restorer.start()
                # p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)  
                # p.wait()  
                # if p.returncode != 0:  
                #    print("Error.")  
                #    return -1 
        except Exception as ex:
            logger.error(ex)


class EspMode(MicroPythonMode):
    """
    Represents the functionality required by the micro:bit mode.
    """
    name = _('mPython')
    description = _("Write MicroPython for the mPython board.")
    icon = 'mPython'
    save_timeout = 0  #: Don't autosave
    fs = None  #: Reference to filesystem navigator.
    flash_thread = None
    flash_timer = None
    file_extensions = ['txt','json','ini']#'hex'
    
    builtins = ['I2C', 'PWM', 'Pin', 'ADC', 'TouchPad', 'SSD1106_I2C',
                'esp', 'ustruct', 'NeoPixel', 'dht_readinto', 'sleep_ms',
                'sleep_us']

    valid_boards = [
        (0x10C4, 0xEA60),  # mPython USB VID, PID
    ]

    valid_serial_numbers = [9900, 9901]  # Serial numbers of supported boards.

    python_script = ''

    def actions(self):
        """
        Return an ordered list of actions provided by this module. An action
        is a name (also used to identify the icon) , description, and handler.
        """
        buttons = [
            {
                'name': 'flash',
                'display_name': _('Flash'),
                'description': _('Flash your code onto the mPython board.'),
                'handler': self.flash_file,
                'shortcut': 'F3',
            },
            {
                'name': 'run',
                'display_name': _('Run'),
                'description': _('Run your code in real time on the mPython board.'),
                'handler': self.run_file,
                'shortcut': 'F5',
            },
            {
                'name': 'files',
                'display_name': _('Files'),
                'description': _('Access the file system on the mPython board.'),
                'handler': self.toggle_files,
                'shortcut': 'F4',
            },
            {
                'name': 'repl',
                'display_name': _('REPL'),
                'description': _('Use the REPL to live-code on the mPython board.'),
                'handler': self.toggle_repl,
                'shortcut': 'Ctrl+Shift+I',
            }, ]
        if CHARTS:
            buttons.append({
                'name': 'plotter',
                'display_name': _('Plotter'),
                'description': _('Plot incoming REPL data.'),
                'handler': self.toggle_plotter,
                'shortcut': 'CTRL+Shift+P',
            })
        return buttons

    def api(self):
        """
        Return a list of API specifications to be used by auto-suggest and call
        tips.
        """
        return SHARED_APIS + ESP_APIS

    def flash(self):
        """
        Takes the currently active tab, compiles the Python script therein into
        a hex file and flashes it all onto the connected device.

        WARNING: This method is getting more complex due to several edge
        cases. Ergo, it's a target for refactoring.
        """
        user_defined_microbit_path = None
        self.python_script = ''
        logger.info('Preparing to flash script.')
        # The first thing to do is check the script is valid and of the
        # expected length.
        # Grab the Python script.
        tab = self.view.current_tab
        if tab is None:
            # There is no active text editor. Exit.
            return
        # Check the script's contents.
        python_script = tab.text().encode('utf-8')
        logger.debug('Python script:')
        logger.debug(python_script)
        # Check minification status.
        minify = False
        if uflash.get_minifier():
            minify = self.editor.minify
        # Attempt and handle minification.
        if len(python_script) >= uflash._MAX_SIZE:
            message = _('Unable to flash "{}"').format(tab.label)
            if minify and can_minify:
                orginal = len(python_script)
                script = python_script.decode('utf-8')
                try:
                    mangled = nudatus.mangle(script).encode('utf-8')
                except TokenError as e:
                    msg, (line, col) = e.args
                    logger.debug('Minify failed')
                    logger.exception(e)
                    message = _("Problem with script")
                    information = _("{} [{}:{}]").format(msg, line, col)
                    self.view.show_message(message, information, 'Warning')
                    return
                saved = orginal - len(mangled)
                percent = saved / orginal * 100
                logger.debug('Script minified, {} bytes ({:.2f}%) saved:'
                             .format(saved, percent))
                logger.debug(mangled)
                python_script = mangled
                if len(python_script) >= 8192:
                    information = _("Our minifier tried but your "
                                    "script is too long!")
                    self.view.show_message(message, information, 'Warning')
                    return
            elif minify and not can_minify:
                information = _("Your script is too long and the minifier"
                                " isn't available")
                self.view.show_message(message, information, 'Warning')
                return
            else:
                information = _("Your script is too long!")
                self.view.show_message(message, information, 'Warning')
                return
        # By this point, there's a valid Python script in "python_script".
        # Assign this to an attribute for later processing in a different
        # method.
        self.python_script = python_script
        # Next step: find the microbit port and serial number.
        path_to_microbit = uflash.find_microbit()
        logger.info('Path to micro:bit: {}'.format(path_to_microbit))
        port = None
        serial_number = None
        try:
            port, serial_number = self.find_device()
            logger.info('Serial port: {}'.format(port))
            logger.info('Device serial number: {}'.format(serial_number))
        except Exception as ex:
            logger.warning('Unable to make serial connection to micro:bit.')
            logger.warning(ex)
        # Determine the location of the BBC micro:bit. If it can't be found
        # fall back to asking the user to locate it.
        if path_to_microbit is None:
            # Ask the user to locate the device.
            path_to_microbit = self.view.get_microbit_path(HOME_DIRECTORY)
            user_defined_microbit_path = path_to_microbit
            logger.debug('User defined path to micro:bit: {}'.format(
                         user_defined_microbit_path))
        # Check the path and that it exists simply because the path maybe based
        # on stale data.
        if path_to_microbit and os.path.exists(path_to_microbit):
            force_flash = False  # If set to true, fully flash the device.
            # If there's no port but there's a path_to_microbit, then we're
            # probably running on Windows with an old device, so force flash.
            if not port:
                force_flash = True
            if not self.python_script.strip():
                # If the script is empty, this is a signal to simply force a
                # flash.
                logger.info("Python script empty. Forcing flash.")
                force_flash = True
            logger.info("Checking target device.")
            # Get the version of MicroPython on the device.
            try:
                version_info = espfs.version()
                logger.info(version_info)
                board_info = version_info['version'].split()
                if (board_info[0] == 'micro:bit' and
                        board_info[1].startswith('v')):
                    # New style versions, so the correct information will be
                    # in the "release" field.
                    try:
                        # Check the release is a correct semantic version.
                        semver.parse(version_info['release'])
                        board_version = version_info['release']
                    except ValueError:
                        # If it's an invalid semver, set to unknown version to
                        # force flash.
                        board_version = '0.0.1'
                else:
                    # 0.0.1 indicates an old unknown version. This is just a
                    # valid arbitrary flag for semver comparison a couple of
                    # lines below.
                    board_version = '0.0.1'
                logger.info('Board MicroPython: {}'.format(board_version))
                logger.info(
                    'Mu MicroPython: {}'.format(uflash.MICROPYTHON_VERSION))
                # If there's an older version of MicroPython on the device,
                # update it with the one packaged with Mu.
                if semver.compare(board_version,
                                  uflash.MICROPYTHON_VERSION) < 0:
                    force_flash = True
            except Exception:
                # Could not get version of MicroPython. This means either the
                # device has a really old version of MicroPython or is running
                # something else. In any case, flash MicroPython onto the
                # device.
                logger.warn('Could not detect version of MicroPython.')
                force_flash = True
            # Check use of custom runtime.
            rt_hex_path = self.editor.microbit_runtime.strip()
            message = _('Flashing "{}" onto the micro:bit.').format(tab.label)
            if (rt_hex_path and os.path.exists(rt_hex_path)):
                message = message + _(" Runtime: {}").format(rt_hex_path)
                force_flash = True  # Using a custom runtime, so flash it.
            else:
                rt_hex_path = None
                self.editor.microbit_runtime = ''
            # Check for use of user defined path (to save hex onto local
            # file system.
            if user_defined_microbit_path:
                force_flash = True
            # If we need to flash the device with a clean hex, do so now.
            if force_flash:
                logger.info('Flashing new MicroPython runtime onto device')
                self.editor.show_status_message(message, 10)
                self.set_buttons(flash=False)
                if user_defined_microbit_path or not port:
                    # The user has provided a path to a location on the
                    # filesystem. In this case save the combined hex/script
                    # in the specified path_to_microbit.
                    # Or... Mu has a path to a micro:bit but can't establish
                    # a serial connection, so use the combined hex/script
                    # to flash the device.
                    self.flash_thread = DeviceFlasher([path_to_microbit],
                                                      self.python_script,
                                                      rt_hex_path)
                    # Reset python_script so Mu doesn't try to copy it as the
                    # main.py file.
                    self.python_script = ''
                else:
                    # We appear to need to flash a connected micro:bit device,
                    # so just flash the Python hex with no embedded Python
                    # script, since this will be copied over when the
                    # flashing operation has finished.
                    model_serial_number = int(serial_number[:4])
                    if rt_hex_path:
                        # If the user has specified a bespoke runtime hex file
                        # assume they know what they're doing and hope for the
                        # best.
                        self.flash_thread = DeviceFlasher([path_to_microbit],
                                                          b'', rt_hex_path)
                    elif model_serial_number in self.valid_serial_numbers:
                        # The connected board has a serial number that
                        # indicates the MicroPython hex bundled with Mu
                        # supports it. In which case, flash it.
                        self.flash_thread = DeviceFlasher([path_to_microbit],
                                                          b'', None)
                    else:
                        message = _('Unsupported BBC micro:bit.')
                        information = _("Your device is newer than this "
                                        "version of Mu. Please update Mu "
                                        "to the latest version to support "
                                        "this device.\n\n"
                                        "https://codewith.mu/")
                        self.view.show_message(message, information)
                        return
                if sys.platform == 'win32':
                    # Windows blocks on write.
                    self.flash_thread.finished.connect(self.flash_finished)
                else:
                    if user_defined_microbit_path:
                        # Call the flash_finished immediately the thread
                        # finishes if Mu is writing the hex file to a user
                        # defined location on the local filesystem.
                        self.flash_thread.finished.connect(self.flash_finished)
                    else:
                        # Other platforms don't block, so schedule the finish
                        # call for 10 seconds (approximately how long flashing
                        # the connected device takes).
                        self.flash_timer = QTimer()
                        self.flash_timer.timeout.connect(self.flash_finished)
                        self.flash_timer.setSingleShot(True)
                        self.flash_timer.start(10000)
                self.flash_thread.on_flash_fail.connect(self.flash_failed)
                self.flash_thread.start()
            else:
                try:
                    self.copy_main()
                except IOError as ioex:
                    # There was a problem with the serial communication with
                    # the device, so revert to forced flash... "old style".
                    # THIS IS A HACK! :-(
                    logger.warning('Could not copy file to device.')
                    logger.error(ioex)
                    logger.info('Falling back to old-style flashing.')
                    self.flash_thread = DeviceFlasher([path_to_microbit],
                                                      self.python_script,
                                                      rt_hex_path)
                    self.python_script = ''
                    if sys.platform == 'win32':
                        # Windows blocks on write.
                        self.flash_thread.finished.connect(self.flash_finished)
                    else:
                        self.flash_timer = QTimer()
                        self.flash_timer.timeout.connect(self.flash_finished)
                        self.flash_timer.setSingleShot(True)
                        self.flash_timer.start(10000)
                    self.flash_thread.on_flash_fail.connect(self.flash_failed)
                    self.flash_thread.start()
                except Exception as ex:
                    self.flash_failed(ex)
        else:
            # Try to be helpful... essentially there is nothing Mu can do but
            # prompt for patience while the device is mounted and/or do the
            # classic "have you tried switching it off and on again?" trick.
            # This one's for James at the Raspberry Pi Foundation. ;-)
            message = _('Could not find an attached BBC micro:bit.')
            information = _("Please ensure you leave enough time for the BBC"
                            " micro:bit to be attached and configured"
                            " correctly by your computer. This may take"
                            " several seconds."
                            " Alternatively, try removing and re-attaching the"
                            " device or saving your work and restarting Mu if"
                            " the device remains unfound.")
            self.view.show_message(message, information)

    def flash_finished(self):
        """
        Called when the thread used to flash the micro:bit has finished.
        """
        self.set_buttons(flash=True)
        self.editor.show_status_message(_("Finished flashing."))
        self.flash_thread = None
        self.flash_timer = None
        if self.python_script:
            try:
                self.copy_main()
            except Exception as ex:
                self.flash_failed(ex)

    def flash_file(self):
        tab = self.editor._view.current_tab
        if tab is None:
            return
        if not tab.path:
            # Unsaved file.
            message = _('Please save the file first.')
            self.view.show_message(message, None)
            return
        port, number = espfs.find_device()
        if port is None:
            message = _('Could not find an attached mPython board.')
            information = _("Please make sure the mPython board is plugged into this computer.")
            self.view.show_message(message, information)
        else:
            #self.editor.save()
            content = tab.text()
            if self.fs is None:
                try:
                    #espfs.put(tab.path, target=None)
                    self.editor.show_status_message(_("Flashing to board ..."))
                    espfs.put_py(tab.path, content, target=None)
                    self.add_fs()
                    if self.file_manager:
                        self.file_manager.on_put_file.emit(os.path.basename(tab.path))
                except Exception as ex:
                    logger.error(ex)
                    if self.file_manager:
                        self.file_manager.on_put_fail.emit(os.path.basename(tab.path))
            else:
                try:
                    if self.file_manager:
                        self.file_manager.stop_py.emit()
                        time.sleep(0.5)
                    # espfs.put(tab.path, target=None)
                    self.editor.show_status_message(_("Flashing to board ..."))
                    espfs.put_py(tab.path, content, target=None)
                    if self.file_manager:
                        self.file_manager.on_put_file.emit(os.path.basename(tab.path))
                    # self.fs.list_files.emit()
                except Exception as ex:
                    logger.error(ex)
                    if self.file_manager:
                        self.file_manager.on_put_fail.emit(os.path.basename(tab.path))

    def run_file(self):
        tab = self.editor._view.current_tab
        if tab is None:
            return
        port, number = espfs.find_device()
        if port is None:
            message = _('Could not find an attached mPython board.')
            information = _("Please make sure the mPython board is plugged into this computer.")
            self.view.show_message(message, information)
        else:
            content = tab.text()
            if self.fs is None:
                try:
                    self.add_fs()
                    if self.file_manager:
                        self.file_manager.on_run_content.emit(content)
                except Exception as ex:
                    logger.error(ex)
            else:
                try:
                    if self.file_manager:
                        self.file_manager.stop_py.emit()
                        time.sleep(0.5)                        
                        self.file_manager.on_run_content.emit(content)
                except Exception as ex:
                    logger.error(ex)

    def copy_main(self):
        """
        If the attribute self.python_script contains any code, copy it onto the
        connected micro:bit as main.py, then restart the board (CTRL-D).
        """
        if self.python_script.strip():
            script = self.python_script
            logger.info('Copying main.py onto device')
            commands = [
                "fd = open('main.py', 'wb')",
                "f = fd.write",
            ]
            while script:
                line = script[:64]
                commands.append('f(' + repr(line) + ')')
                script = script[64:]
            commands.append('fd.close()')
            logger.info(commands)
            serial = espfs.get_serial()
            out, err = espfs.execute(commands, serial)
            logger.info((out, err))
            if err:
                raise IOError(espfs.clean_error(err))
            # Reset the device.
            serial.write(b'import microbit\r\n')
            serial.write(b'microbit.reset()\r\n')
            self.editor.show_status_message(_('Copied code onto micro:bit.'))
        self.python_script = ''

    def flash_failed(self, error):
        """
        Called when the thread used to flash the micro:bit encounters a
        problem.
        """
        logger.error(error)
        message = _("There was a problem flashing the mPython board.")
        information = _("Please do not disconnect the device until flashing"
                        " has completed. Please check the logs for more"
                        " information.")
        self.view.show_message(message, information, 'Warning')
        if self.flash_timer:
            self.flash_timer.stop()
            self.flash_timer = None
        self.set_buttons(flash=True)
        self.flash_thread = None

    def toggle_repl(self, event):
        """
        Check for the existence of the file pane before toggling REPL.
        """
        if self.fs is None:
            super().toggle_repl(event)
            if self.repl:
                self.set_buttons(flash=False, run=False)
                self.editor.show_status_message(_('If there is a running program, please press Ctrl+C to interrupt.'))
            elif not (self.repl or self.plotter):
               self.set_buttons(flash=True, run=True)
        else:
            self.file_manager.stop_py.emit()
            self.remove_fs()
            """
            message = _("REPL and file system cannot work at the same time.")
            information = _("The REPL and file system both use the same USB "
                            "serial connection. Only one can be active "
                            "at any time. Toggle the file system off and "
                            "try again.")
            self.view.show_message(message, information)
            """

    def toggle_plotter(self, event):
        """
        Check for the existence of the file pane before toggling plotter.
        """
        if self.fs is None:
            super().toggle_plotter(event)
            if self.plotter:
                self.set_buttons(flash=False, run=False)
            elif not (self.repl or self.plotter):
                self.set_buttons(flash=True, run=True)
        else:
            self.file_manager.stop_py.emit()
            self.remove_fs()
            """
            message = _("The plotter and file system cannot work at the same "
                        "time.")
            information = _("The plotter and file system both use the same "
                            "USB serial connection. Only one can be active "
                            "at any time. Toggle the file system off and "
                            "try again.")
            self.view.show_message(message, information)
            """

    def toggle_files(self, event):
        """
        Check for the existence of the REPL or plotter before toggling the file
        system navigator for the micro:bit on or off.
        """
        if (self.repl or self.plotter):
            if self.repl:
                super().toggle_repl(event)
            if self.plotter:
                super().toggle_plotter(event)
            
            """
            message = _("File system cannot work at the same time as the "
                        "REPL or plotter.")
            information = _("The file system and the REPL and plotter "
                            "use the same USB serial connection. Toggle the "
                            "REPL and plotter off and try again.")
            self.view.show_message(message, information)
            """
        else:
            if self.fs is None:
                self.add_fs()
                if self.fs:
                    logger.info('Toggle filesystem on.')
                    # self.set_buttons(repl=False, plotter=False)
            else:
                self.file_manager.stop_py.emit()
                self.remove_fs()
                logger.info('Toggle filesystem off.')
                # self.set_buttons(repl=True, plotter=True)
        self.set_buttons(flash=True, run=True)

    def add_fs(self, _reset=False):
        """
        Add the file system navigator to the UI.
        """
        # Check for micro:bit
        port, serial_number = self.find_device()
        if not port:
            message = _('Could not find an attached mPython board.')
            information = _("Please make sure the mPython board is plugged into this computer.")
            self.view.show_message(message, information)
            return
        self.file_manager_thread = QThread(self)
        self.file_manager = FileManager()
        self.file_manager.moveToThread(self.file_manager_thread)
        self.file_manager_thread.started.\
            connect(self.file_manager.on_start)
        if _reset:
            self.file_manager_thread.started.\
                connect(self.do_reset_firmware)
        self.fs = self.view.add_filesystem_esp(self.workspace_dir(),
                                               self.file_manager)
        self.fs.set_message.connect(self.editor.show_status_message)
        self.fs.set_warning.connect(self.view.show_message)
        self.file_manager_thread.start()

    def remove_fs(self):
        """
        Remove the file system navigator from the UI.
        """
        self.view.remove_filesystem()
        self.file_manager = None
        self.file_manager_thread = None
        self.fs = None

    def on_data_flood(self):
        """
        Ensure the Files button is active before the REPL is killed off when
        a data flood of the plotter is detected.
        """
        self.set_buttons(files=True)
        super().on_data_flood()

    def open_file(self, path):
        """
        Tries to open a MicroPython hex file with an embedded Python script.
        """
        text = None
        if path.lower().endswith('.hex'):
            # Try to open the hex and extract the Python script
            try:
                with open(path, newline='') as f:
                    text = uflash.extract_script(f.read())
            except Exception:
                return None
        return text

    def get_res_path(self):
        if platform.system() == "Darwin":
            app_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            app_dir = os.path.dirname(os.path.abspath(app_path))
            res_path = os.path.join(app_dir, "../Resources/")
        else:
            res_path = os.path.split(os.path.realpath(sys.argv[0]))[0] + '\\'
        return res_path

    def get_firmware_version(self, _response):
        if b'icroPython ' in _response:
            i = _response.find(b'icroPython ') + 11
            _response = _response[i:]
            j = _response.find(b';')
            _response = _response[0:j]
            k = _response.find(b' on ') + 4
            _date = _response[k:]
            return str(_response, encoding="utf8"), str(_date, encoding="utf8")
        else:
            return None, None

    def do_reset_firmware(self):
        self.file_manager.reset_firmware(self.workspace_dir())
    
    def check_firmware(self):
        # print("check_firmware")
        if self.editor.mode != "mPython":
            return
        if not self.view.update_bin_status:
            return
        try:
            serial = espfs.get_serial()
            if serial:
                serial.write(b'\x02')
                for i in range(3):
                    serial.write(b'\r\x03')
                    time.sleep(0.01)
                response = serial.read_until(b'Type "help()" for more information.')
                # print(response)
                firmware_ver, firmware_date = self.get_firmware_version(response)
                if firmware_ver is None:
                    serial.write(b'\r\x03')
                    response = serial.read_until(b'Type "help()" for more information.')
                    # print(response)
                    firmware_ver, firmware_date = self.get_firmware_version(response)
                if firmware_ver is None:
                    firmware_ver = ""
                    firmware_date = "None"
                print(firmware_ver, firmware_date)
                config_dir = os.path.join(self.workspace_dir(), "__config__")
                ini_path = os.path.join(config_dir, "mpython.ini")
                if not os.path.isfile(ini_path):
                    return
                cf = configparser.ConfigParser()
                cf.read(ini_path)
                if cf.has_section("firmware"):
                    local_ver = None
                    local_date = None
                    local_ignore = None
                    try:
                        local_ver = cf.get("firmware","version")
                        local_date = cf.get("firmware","date")
                        local_ignore = cf.get("firmware","ignore")
                    except Exception as ex:
                        print(ex)
                    print(local_ver, local_date, local_ignore)
                    if local_ignore is not None:
                        if local_ignore == "1":
                            return
                    if local_ver is not None:
                        if firmware_ver == local_ver:
                            return
                        if firmware_ver == "":
                            info = _("No onboard firmware detected, replace th"
                                "e firmware in hardware by the firmware in sof"
                                "tware (release date: {}).\n\nWarning: this op"
                                "eration will cause all user files lost.").format(local_date)
                            if self.view.show_update_firmware(info, config_dir):
                                if self.fs is None:
                                    self.add_fs(_reset=True)
                                else:
                                    self.file_manager.reset_firmware(self.workspace_dir())
                        else:
                            info = _("The firmware (release date: {}) "
                                "which preloaded in hardware is different "
                                "from the firmware (release date: {}) "
                                "which preseted in software. The question "
                                "is whether to replace the firmware in "
                                "hardware by the firmware in software.\n\n"
                                "Warning: this operation will cause all "
                                "user files lost.").format(firmware_date,
                                local_date)
                            if self.view.show_update_firmware(info, config_dir):
                                result = self.view.show_confirmation(_("WARNING: This operation "
                                    "will cause all user files lost.!!!\nWARNING: This operation "
                                    "will cause all user files lost !!!\nWARNING: This operation "
                                    "will cause all user files lost !!!"), icon='Warning')
                                if result == QMessageBox.Ok:
                                    if self.fs is None:
                                        self.add_fs(_reset=True)
                                    else:
                                        self.file_manager.reset_firmware(self.workspace_dir())
        except Exception as ex:
            return        

