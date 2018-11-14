"""
Contains definitions for the MicroPython micro:bit related APIs so they can be
used in the editor for autocomplete and call tips.

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


ESP_APIS = [
    # mpython
    _("from"),
    _("import"),
    _("mpython"),
    # esp
    _("esp.osdebug(None) /nturn off vendor O/S debugging messages"),
    _("esp.osdebug(0) /nredirect vendor O/S debugging messages to UART(0)"),
    # mpython buzz
    _("mpython.buzz.isOn \n蜂鸣器开关状态，返回值为 True/False"),
    _("mpython.buzz.on(n) \n蜂鸣器开，参数n为频率，单位Hz，如：500(Hz)"),
    _("mpython.buzz.off() \n蜂鸣器关"),
    _("mpython.buzz.freq(n) \n蜂鸣器频率，单位Hz"),
    #_("mpython.buzz.duty(n) \n蜂鸣器音量，0～512"),
    # mpython TextMode
    _("mpython.TextMode.normal \n值为1"),
    _("mpython.TextMode.rev \n值为2"),
    _("mpython.TextMode.trans \n值为3"),
    _("mpython.TextMode.xor \n值为4"),
    # mpython PinMode
    _("mpython.PinMode.IN \n值为1"),
    _("mpython.PinMode.OUT \n值为2"),
    _("mpython.PinMode.PWM \n值为3"),
    _("mpython.PinMode.ANALOG \n值为4"),
    # mpython MPythonPin
    _("mpython.MPythonPin(pin, mode = PinMode.IN) \npin: 端口号\nmode: PinMode.IN / PinMode.OUT / PinMode.PWM / PinMode.ANALOG"),
    _("mpython.MPythonPin.read_digital()"),
    _("mpython.MPythonPin.write_digital()"),
    _("mpython.MPythonPin.read_analog()"),
    _("mpython.MPythonPin.write_analog(duty, freq=1000)"),
    # mpython Servo
    _("mpython.Servo.write_us(us) \nus: min=750, max=2250"),
    _("mpython.Servo.write_angle(angle) \nangle: min=0, max=180"),
    # mpython UI
    _("mpython.UI.ProgressBar(x, y, width, height, progress)"),
    _("mpython.UI.stripBar(x, y, width, height, progress, dir=1, frame=1)"),
    # mpython DHTBase
    _("mpython.DHTBase.measure()"),
    # mpython DHT11
    _("mpython.DHT11.humidity()"),
    _("mpython.DHT11.temperature()"),
    # mpython DHT22
    _("mpython.DHT22.humidity()"),
    _("mpython.DHT22.temperature()"),
    # mpython display
    _("mpython.oled.fill(c) \n用指定颜色填充屏幕，0为全黑"),
    _("mpython.oled.fill_rect(x, y, w, h, c)"),
    #_("oled.DispChar(str, x, y, mode = TextMode.normal) \nstr: 需要显示的字符\nx: 显示位置的x坐标\ny: 显示位置的y坐标\n(可选参数)mode : normal = 1(默认值) / rev = 2 / trans = 3 / xor = 4"),
    _("mpython.oled.DispChar(str, x, y) \nstr: 需要显示的字符\nx: 显示位置的x坐标\ny: 显示位置的y坐标"),
    _("mpython.oled.circle(x0, y0, radius , c)"),
    _("mpython.oled.fill_circle(x0, y0, radius , c)"),
    _("mpython.oled.triangle(x0, y0, x1, y1, x2, y2, c)"),
    _("mpython.oled.fill_triangle(x0, y0, x1, y1, x2, y2, c)"),
    _("mpython.oled.Bitmap(x, y, bitmap, w, h, c)"),
    _("mpython.oled.drawCircleHelper(x0, y0, r, cornername, c)"),
    _("mpython.oled.RoundRect(x, y, w, h, r, c)"),
    _("mpython.oled.show() \n显示内容生效"),
    _("mpython.oled.pixel(x, y[, c]) \n如果参数c没有赋值，则返回点(x,y)的颜色\n如果参数c有值，则设置点(x,y)为指定颜色c"),
    _("mpython.oled.hline(x, y, w, c)"),
    _("mpython.oled.vline(x, y, w, c)"),
    _("mpython.oled.line(x1, y1, x2, y2, c)"),
    _("mpython.oled.rect(x, y, w, h, c)"),
    _("mpython.oled.text(s, x, y[, c])"),
    _("mpython.oled.blit(fbuf, x, y[, key])"),
    _("mpython.oled.MONO_VLSB \nMonochrome (1-bit) color format This defines a mapping where the bits in a byte are vertically mapped with bit 0 being nearest the top of the screen. Consequently each byte occupies 8 vertical pixels. Subsequent bytes appear at successive horizontal locations until the rightmost edge is reached. Further bytes are rendered at locations starting at the leftmost edge, 8 pixels lower."),
    _("mpython.oled.MONO_HLSB \nMonochrome (1-bit) color format This defines a mapping where the bits in a byte are horizontally mapped. Each byte occupies 8 horizontal pixels with bit 0 being the leftmost. Subsequent bytes appear at successive horizontal locations until the rightmost edge is reached. Further bytes are rendered on the next row, one pixel lower."),
    _("mpython.oled.MONO_HMSB \nMonochrome (1-bit) color format This defines a mapping where the bits in a byte are horizontally mapped. Each byte occupies 8 horizontal pixels with bit 7 being the leftmost. Subsequent bytes appear at successive horizontal locations until the rightmost edge is reached. Further bytes are rendered on the next row, one pixel lower."),
    _("mpython.oled.RGB565 \nRed Green Blue (16-bit, 5+6+5) color format"),
    _("mpython.oled.GS2_HMSB \nGrayscale (2-bit) color format"),
    _("mpython.oled.GS4_HMSB \nGrayscale (4-bit) color format"),
    _("mpython.oled.GS8 \nGrayscale (8-bit) color format"),
    # mpython accelerometer
    _("mpython.accelerometer.get_x() \nx轴加速度值，返回值是G的倍数，G=9.8m/s^2"),
    _("mpython.accelerometer.get_y() \ny轴加速度值，返回值是G的倍数，G=9.8m/s^2"),
    _("mpython.accelerometer.get_z() \nz轴加速度值，返回值是G的倍数，G=9.8m/s^2"),
    # mpython object
    _("mpython.rgb.write()"),
    _("mpython.light.read() \n读取声音值"),
    _("mpython.sound.read() \n读取光线值"),
    _("mpython.button_a.value() \n读取按键A的值"),
    _("mpython.button_b.value() \n读取按键B的值"),
    _("mpython.button_a.irq(_function) \n为按键A设置响应事件"),
    _("mpython.button_b.irq(_function) \n为按键B设置响应事件"),
    #mpython touchPad
    _("mpython.touchPad_P.read()"),
    _("mpython.touchPad_Y.read()"),
    _("mpython.touchPad_T.read()"),
    _("mpython.touchPad_H.read()"),
    _("mpython.touchPad_O.read()"),
    _("mpython.touchPad_N.read()"),
    # RNG
    _("random.getrandbits(n) \nReturn an integer with n random bits."),
    _("random.seed(n) \nInitialise the random number generator with a known integer 'n'."),
    _("random.randint(a, b) \nReturn a random whole number between a and b (inclusive)."),
    _("random.randrange(stop) \nReturn a random whole number between 0 and up to (but not including) stop."),
    _("random.choice(seq) \nReturn a randomly selected element from a sequence of objects (such as a list)."),
    _("random.random() \nReturn a random floating point number between 0.0 and 1.0."),
    _("random.uniform(a, b) \nReturn a random floating point number between a and b (inclusive)."),
    # OS
    _("os.listdir() \nReturn a list of the names of all the files contained within the local\non-device file system."),
    _("os.remove(filename) \nRemove (delete) the file named filename."),
    _("os.size(filename) \nReturn the size, in bytes, of the file named filename."),
    _("os.uname() \nReturn information about MicroPython and the device."),
    _("os.getcwd() \nReturn current working directory"),
    _("os.chdir(path) \nChange current working directory"),
    _("os.mkdir(path) \Make new directory"),
    _("os.rmdir(path) \Remove directory"),
    _("os.listdir(path='.') \Return list of directory. Defaults to current working directory."),
    # SYS
    _("sys.version"),
    _("sys.version_info"),
    _("sys.implementation"),
    _("sys.platform"),
    _("sys.byteorder"),
    _("sys.print_exception(ex) \nPrint to the REPL information about the exception 'ex'."),
    # micro:bit
    # Music module
    _("music.set_tempo(number, bpm) \nMake a beat last a 'number' of ticks long and\nplayed at 'bpm' beats per minute."),
    _("music.pitch(freq, length=-1, pin=microbit.pin0, wait=True) \nMake micro:bit play a note at 'freq' frequency for\n'length' milliseconds. E.g. pitch(440, 1000) will play concert 'A' for 1 second.\nIf length is a negative number the pitch is played continuously.\nUse the optional pin argument to override the default output for the speaker.\nIf wait is False the music will play in the background while the program\ncontinues."),
    _("music.play(music, pin=microbit.pin0, wait=True, loop=False) \nMake micro:bit play 'music' list of notes. Try out the built in music to see\nhow it works. E.g. music.play(music.PUNCHLINE).\nUse the optional pin argument to override the default output for the speaker.\nIf wait is False the music will play in the background while the program\ncontinues.\nIf loop is True, the tune will repeat."),
    _("music.get_tempo() \nReturn the number of ticks in a beat and number of beats per minute."),
    _("music.stop(pin=microbit.pin0) \nStops all music playback on the given pin. If no pin is given, pin0 is assumed."),
    _("music.reset()\nIf things go wrong, reset() the music to its default settings."),
    _("music.DADADADUM"),
    _("music.ENTERTAINER"),
    _("music.PRELUDE"),
    _("music.ODE"),
    _("music.NYAN"),
    _("music.RINGTONE"),
    _("music.FUNK"),
    _("music.BLUES"),
    _("music.BIRTHDAY"),
    _("music.WEDDING"),
    _("music.FUNERAL"),
    _("music.PUNCHLINE"),
    _("music.PYTHON"),
    _("music.BADDY"),
    _("music.CHASE"),
    _("music.BA_DING"),
    _("music.WAWAWAWAA"),
    _("music.JUMP_UP"),
    _("music.JUMP_DOWN"),
    _("music.POWER_UP"),
    _("music.POWER_DOWN"),
    # Antigravity
    _("antigravity"),
    # This module
    _("this.authors() \nUse authors() to reveal the names of the people who created this software."),
    # Love module
    _("love.badaboom()\nHear my soul speak:\nThe very instant that I saw you, did\nMy heart fly to your service."),
    # NeoPixel module
    _("neopixel.NeoPixel(pin, n) \nCreate a list representing a strip of 'n' neopixels controlled from the\nspecified pin (e.g. microbit.pin0).\nUse the resulting object to change each pixel by position (starting from 0).\nIndividual pixels are given RGB (red, green, blue) values between 0-255 as a\ntupe. For example, (255, 255, 255) is white:\n\nnp = neopixel.NeoPixel(microbit.pin0, 8)\nnp[0] = (255, 0, 128)\nnp.show()"),
    _("neopixel.NeoPixel.clear() \nClear all the pixels."),
    _("neopixel.NeoPixel.show() \nShow the pixels. Must be called for any updates to become visible."),
    # Radio
    _("radio.on() \nTurns on the radio. This needs to be called since the radio draws power and\ntakes up memory that you may otherwise need."),
    _("radio.off() \nTurns off the radio, thus saving power and memory."),
    _("radio.config(length=32, queue=3, channel=7, power=0, address=0x75626974, group=0, data_rate=radio.RATE_1MBIT) \nConfigures the various settings relating to the radio. The specified default\nvalues are sensible.\n'length' is the maximum length, in bytes, of a message. It can be up to 251\nbytes long.\n'queue' is the number of messages to store on the message queue.\n'channel' (0-100) defines the channel to which the radio is tuned.\n'address' is an arbitrary 32-bit address that's used to filter packets.\n'group' is an 8-bit value used with 'address' when filtering packets.\n'data_rate' is the throughput speed. It can be one of: radio.RATE_250KbIT,\nradio.RATE_1MbIT (the default) or radio.2MBIT."),
    _("radio.reset() \nReset the settings to their default value."),
    _("radio.send_bytes(message) \nSends a message containing bytes."),
    _("radio.receive_bytes() \nReceive the next incoming message from the message queue. Returns 'None' if\nthere are no pending messages. Messages are returned as bytes."),
    _("radio.send(message) \nSend a message string."),
    _("radio.receive() \nReceive the next incoming message from the message queue as a string. Returns\n'None' if there are no pending messages."),
    _("radio.RATE_250KBIT"),
    _("radio.RATE_1MBIT"),
    _("radio.RATE_2MBIT"),
    # Audio
    _("audio.play(source, wait=True, pins=(pin0, pin1)) \nPlay the source to completion where 'source' is an iterable, each element of\nwhich must be an AudioFrame instance."),
    _("audio.AudioFrame()() \nRepresents a list of 32 samples each of which is a signed byte. It takes just\nover 4ms to play a single frame."),
    # Speech
    _("speech.translate(words) \nReturn a string containing the phonemes for the English words in the string\n'words'."),
    _("speech.say(words, pitch=64, speed=72, mouth=128, throat=128) \nSay the English words in the string 'words'. Override the optional pitch,\nspeed, mouth and throat settings to change the tone of voice."),
    _("speech.pronounce(phonemes, pitch=64, speed=72, mouth=128, throat=128) \nPronounce the phonemes in the string 'phonemes'. Override the optional pitch,\nspeed, mouth and throat settings to change the tone of voice."),
    _("speech.sing(song, pitch=64, speed=72, mouth=128, throat=128) \nSing the phonemes in the string 'song'. Add pitch information to a phoneme\nwith a hash followed by a number between 1-255 like this: '#112DOWWWWWWWW'.\nOverride the optional pitch, speed, mouth and throat settings to change the\ntone of voice."),
    # Math functions
    _("math.sqrt(x) \nReturn the square root of 'x'."),
    _("math.pow(x, y) \nReturn 'x' raised to the power 'y'."),
    _("math.exp(x) \nReturn math.e**'x'."),
    _("math.log(x, base=math.e) \nWith one argument, return the natural logarithm of 'x' (to base e).\nWith two arguments, return the logarithm of 'x' to the given 'base'."),
    _("math.cos(x) \nReturn the cosine of 'x' radians."),
    _("math.sin(x) \nReturn the sine of 'x' radians."),
    _("math.tan(x) \nReturn the tangent of 'x' radians."),
    _("math.acos(x) \nReturn the arc cosine of 'x', in radians."),
    _("math.asin(x) \nReturn the arc sine of 'x', in radians."),
    _("math.atan(x) \nReturn the arc tangent of 'x', in radians."),
    _("math.atan2(x, y) \nReturn atan(y / x), in radians."),
    _("math.ceil(x) \nReturn the ceiling of 'x', the smallest integer greater than or equal to 'x'."),
    _("math.copysign(x, y) \nReturn a float with the magnitude (absolute value) of 'x' but the sign of 'y'. "),
    _("math.fabs(x) \nReturn the absolute value of 'x'."),
    _("math.floor(x) \nReturn the floor of 'x', the largest integer less than or equal to 'x'."),
    _("math.fmod(x, y) \nReturn 'x' modulo 'y'."),
    _("math.frexp(x) \nReturn the mantissa and exponent of 'x' as the pair (m, e). "),
    _("math.ldexp(x, i) \nReturn 'x' * (2**'i')."),
    _("math.modf(x) \nReturn the fractional and integer parts of x.\nBoth results carry the sign of x and are floats."),
    _("math.isfinite(x) \nReturn True if 'x' is neither an infinity nor a NaN, and False otherwise."),
    _("math.isinf(x) \nReturn True if 'x' is a positive or negative infinity, and False otherwise."),
    _("math.isnan(x) \nReturn True if 'x' is a NaN (not a number), and False otherwise."),
    _("math.trunc(x) \nReturn the Real value 'x' truncated to an Integral (usually an integer)."),
    _("math.radians(x) \nConvert angle 'x' from degrees to radians."),
    _("math.degrees(x) \nConvert angle 'x' from radians to degrees."),
    # Machine module
    _("machine.reset() \nResets the device in a manner similar to pushing the external RESET button"),
    _("machine.freq() \nReturns CPU frequency in hertz."),
    _("machine.freq(n) /nSet the CPU frequency to n Hz(e.g. 160000000 means 160 MHz)"),
    _("""machine.Pin(id [, mode, pull])\nCreate a Pin-object. Only id is mandatory.
mode (optional): specifies the pin mode (Pin.OUT or Pin.IN)
pull (optional): specifies if the pin has a pull resistor attached 
  pull can be one of: None, Pin.PULL_UP or Pin.PULL_DOWN."""),
    _("""machine.Pin.value([x])\n This method allows to set and get the
value of the pin, depending on whether the argument x is supplied or not.
If the argument is omitted, the method returns the actual input value (0 or 1) on the pin.
If the argument is supplied, the method sets the output to the given value."""),
    _("machine.Pin.OUT"),
    _("machine.Pin.IN"),
    _("machine.Pin.PULL_UP"),
    _("machine.Pin.PULL_DOWN"),
    _("""machine.ADC(pin)
Create an ADC object associated with the given pin. 
This allows you to then read analog values on that pin.
machine.ADC(machine.Pin(39))"""),
    _("machine.ADC.read() \nRead the analog pin value.\n\nadc = machine.ADC(machine.Pin(39))\nvalue = adc.read()"),
    # Time module
    _("time.sleep(seconds) \nSleep the given number of seconds."),
    _("time.sleep_ms(milliseconds) \nSleep the given number of milliseconds."),
    _("time.sleep_us(milliseconds) \nSleep the given number of microseconds."),
    _("time.ticks_ms() \nReturn number of milliseconds from an increasing counter. Wraps around after some value."),
    _("time.ticks_us() \nReturn number of microseconds from an increasing counter. Wraps around after some value."),
    _("time.ticks_diff() \nCompute difference between values ticks values obtained from time.ticks_ms() and time.ticks_us()."),
    _("""time.time() 
Returns the number of seconds, as an integer, since the Epoch, 
assuming that underlying RTC is set and maintained. If an
RTC is not set, this function returns number of seconds since a
port-specific reference point in time (usually since boot or reset)."""),
    # Network module
    _("""network.WLAN(interface_id) \n
Create a WLAN interface object. Supported interfaces are:
network.STA_IF (station aka client, connects to upstream WiFi access points) and 
network.AP_IF (access point mode, allows other WiFi clients to connect)."""),
    _("network.WLAN.STA_IF"),
    _("network.WLAN.AP_IF"),
    _("""network.WLAN.active([ is_active ])
Activates or deactivates the network interface when given boolean
argument. When argument is omitted the function returns the current state."""),
    _("""network.WLAN.connect(ssid, password)
Connect to the specified wireless network using the specified password."""),
    _("network.WLAN.disconnect() \nDisconnect from the currently connected wireless network."),
    _("""network.WLAN.scan()
Scan for the available wireless networks. Scanning is only possible on
STA interface. Returns list of tuples with the information about WiFi
access points:
   (ssid, bssid, channel, RSSI, authmode, hidden)"""),
    _("""network.WLAN.status()
Return the current status of the wireless connection. Possible values:
 - STAT_IDLE (no connection and no activity)
 - STAT_CONNECTING (connecting in progress)
 - STAT_WRONG_PASSWORD (failed due to incorrect password),
 - STAT_NO_AP_FOUND (failed because no access point replied),
 - STAT_CONNECT_FAIL (failed due to other problems),
 - STAT_GOT_IP (connection successful)"""),
    _("""network.WLAN.isconnected()
In case of STA mode, returns True if connected to a WiFi access point
and has a valid IP address. In AP mode returns True when a station is
connected. Returns False otherwise."""),
    _("""network.WLAN.ifconfig([ (ip, subnet, gateway, dns) ]) 
Get/set IP-level network interface parameters: IP address, subnet
mask, gateway and DNS server. When called with no arguments, this
method returns a 4-tuple with the above information. To set the above
values, pass a 4-tuple with the required information. For example:

nic = network.WLAN(network.WLAN.AP_IF)
nic.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))"""),
    # urequests module
    _("""urequests.get(url, headers={})
Send HTTP GET request to the given URL. 
An optional dictionary of HTTP headers can be provided.
Returns a urequests.Response-object"""),
    _("""urequests.post(url, data=None, json=None, headers={}) 
Send HTTP POST request to the given URL. Returns a
urequests.Response-object.
 - data (optional): bytes to send in the body of the request.
 - json (optional): JSON data to send in the body of the Request.
 - headers (optional): An optional dictionary of HTTP headers."""),
    _("urequests.Response() \n Object returned by "),
    _("urequests.Response.text \n String representation of response "),
    _("urequests.Response.json() \n Convert Response from JSON to Python dictionary."),
]
