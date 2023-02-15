# js8net

#### _Jeff Francis <jeff@gritch.org>_, N0GQ

## The Library

js8net is a python3 package for interacting with the JS8Call API. It works exclusively in TCP mode. It *might* work with python2, but I suspect not. I haven't tried it. If it doesn't work, but you'd like it to, I'll happily consider your patches for inclusion. Likewise, it's intended to run on "unix-like" operating systems (OSX, Linux, and the various BSD flavors). It *might* work on Windows. It might not. The code has not been written to excluded Windows, but I have no simple way to test it. The generated web pages (see the bottom of this document) should be viewable on any modern Chromium-based browser and Firefox. I have not tested them on IE or Safari.

The JS8Call API is a bit painful to use directly from your own code for several reasons:

- It's essentially undocumented. While there are some partial docs floating around, mostly you have to read the JS8Call source code. Specifically, the MainWindow::networkMessage() function in mainwindow.cpp will tell you what functions are available and what the parameters required and returned are.

- The API is completely asynchronous. You send commands to JS8Call whenever you wish, and it sends the reply whenever it's good and ready. Or maybe not. As a result, without an API library, you have to keep track of what queries were sent, then attempt to match up random replies with the original queries.

- It's incomplete. You cannot mark INBOX messages as read (or delete them). You cannot toggle SPOT on or off. You cannot trigger a contact log. You cannot toggle TX on or off. You cannot enable or disable Autoreply, Heartbeat Networking, Heartbeat Acknowledgements, change Decoder Sensitivity, turn simultaneous decoding on or off, change callsign groups, change Station Status, change the CQ or Reply messages. I'd also love to see an API call to generate a message checksum (for a message I'm generating) and to validate the checksum of a received message.

- The API is completely disconnected from the GUI. If you make a change using the API, for example changing the speed from Normal to Slow or changing your grid square, those changes are partially visible in the GUI, yet don't actually change the modem speed.

- API usage does not reset the idle timeout. Meaning that after the specified period of time without interacting with the GUI, all transmission stops until you click the timeout "OK" notice with a mouse. And the maximum time the timeout can be set for is only 1440 minutes (24 hours). You can get rid of this behavior by setting IDLE_BLOCKS to FALSE in the C++ source and recompiling, but recompiling JS8Call is quite painful compared with most software, and is horrifically slow on the Pi. I have an icky, but usable work-around below.

- There are many errors and notices, such as serial comms errors between the software and your laptop, that can only be cleared or retried by clicking the mouse on the screen. They cannot be handled via the API.

This library is an attempt to hide as much of the API's complexity as possible behind a more traditional query/reply paradigm. It also tries to make up for some of the API's shortcomings as best it can. The good news is that there is at least a small amount of work being done to update the JS8Call code after all these years.

As you use this API, keep in mind the architecture of JS8Call itself that doesn't allow API changes to be visible in the GUI. It will confuse you until you get used to it. If you change the grid square using the API, the GUI will still show the old grid square. If you change your transmission speed using the API, the GUI will still show the old transmission speed. Everything will work just fine, but it will look wrong on screen. There are bugs open against JS8Call to fix this.

While JS8Call by and large does work well, it's been two years since the last release, and there are numerous anticipated bug fixes supposedly in the works that should make JS8Call a much better piece of software to work with via the API.

## Idle Timeout

Make sure you set the Idle Timeout to "Disabled", or the API will quit working after some (configurable) time after you don't touch the keyboard or mouse. Obviously, this breaks things.

## Getting Started

To get started, import the library, then tell it to connect to your JS8Call instance:

```python3
from js8net import *
start_net("10.1.1.141",2442)
```

At this point, there are two threads running. One thread receives requests from your code, and delivers them to JS8Call. The second thread receives the random data sent by JS8Call, processes that data, and provides it back to you, the user.

Generally speaking, you do not interact directly with the first queue. You make function calls using the js8net library, and those function calls are internally translated to the proper queries, and pushed into the queue for delivery. For example, to ask JS8Call for the currently configured Maidenhead grid square, you can simple do the following:

```python3
grid=get_grid()
```

Behind the scenes, the library creates the proper JSON for the query, delivers it to JS8Call, then watches the stream of traffic returning from JS8Call until it finds the grid information, then returns it as a result of the function call.

There are approximately a dozen or so of these function calls, listed below. The majority of these calls return a single value, however the one exception is the call to return or set the radio frequency. Because this function returns three values (radio dial frequency, the offset within the audio passband, and the effective transmit frequency), that one single call actually returns a JSON blob, rather than a single value. It's up to you to extract the values you need from the returned JSON:

```python3
>>> get_freq()
{'dial': 7078000, 'freq': 7080000, 'offset': 2000}
>>>
```

```python3
get_freq()
```

Ask JS8Call to get the radio's frequency. Returns the dial frequency (in hz), the offset in the audio passband (in hz), and the actual effective transmit frequency (basically the two values added together) as a JSON blob.

```python3
set_freq(dial,offset)
```

Set the radio's dial freq (in hz) and the offset within the passband (also in hz).

```python3
get_callsign()
```

Ask JS8Call for the configured callsign.

```python3
get_grid()
```

Ask JS8Call for the configured grid square.

```python3
set_grid(grid)
```

Set the grid square.

```python3
send_aprs_grid(grid)
```

Send the supplied grid info to APRS (use send_aprs_grid(get_grid()) to send your configured grid info.

```python3
send_sms(phone,message)
```

Send an SMS message via JS8.

```python3
send_email(address,message)
```

Send an email message via JS8.

```python3
get_info()
```

Ask JS8Call for the configured info field.

```python3
set_info(info)
```

Set the info field.

```python3
get_call_activity()
```

Get the contents of the right white box.

```python3
get_call_selected()
```

Return the call sign that's currently selected in the GUI.

```python3
get_band_activity()
```

Get the contents of the left white box.

```python3
get_rx_text()
```

Get the contents of the white box below the yellow window.

```python3
get_tx_text()
```

Set the contents of the white box below the yellow window.

```python3
set_tx_text(text)
```

Get the contents of the box below yellow window.

```python3
get_speed()
```

Ask JS8Call what speed it's currently configured for.  slow==4, normal==0, fast==1, turbo==2

```python3
set_speed(speed)
```

Set the JS8Call transmission speed.  slow==4, normal==0, fast==1, turbo==2

```python3
raise_window()
```

Raise the JS8Call window to the top on the screen.

```python3
send_message(message)
```

Send 'message' in the next transmit cycle.

There are also three functions related to your INBOX and sending messages:

```python3
send_inbox_message(dest_call,message)
```

This function immediately sends a message to dest_call to be stored in his INBOX. Note that this function __does not__ check for a successful ACK message from the receiver. That's left as an exercise for the programmer.

```python3
get_messages()
```

This function returns an array of all messages (READ, UNREAD, and STORED) in your own mailbox.

```python3
store_message(callsign,text)
```

This function stores a message in your INBOX for pickup by another user. The function returns your entire INBOX, including the new message that you just stored.

## Receiving

Sending of data, querying of status, and setting configuration are handled by the function calls above. Receiving data, however, is handled more directly by your own code.

Incoming messages from JS8Call are intercepted and parsed by the js8net library. The bulk of these are quietly handled, and various internal tables and states are automatically updated. Actual text sent by other users, however, are passed along to the rx_queue for your own processing. Note that the rx_queue is protected by a mutex called rx_lock. Use of this lock is necessary to prevent simultaneous reading and writing to the queue.

There are three types of messages that will come in at random from JS8Call, and four more types that will occur as the result of queries you make with the functions detailed above. The three types of messages that come from other JS8Call users are:

* RX.SPOT - A spot message.

* RX.ACTIVITY - Received data (typically, a single, incomplete frame;   a fragment of a larger message).

* RX.DIRECTED - A complete, reassembled message with each of the available frames properly concatenated together into a single string.

Unless you are doing something particularly interesting or different, it's likely that RX.DIRECTED is what you'll be interested in.

These messages are kept in a python queue. The following documentation will be helpful in understanding how to properly deal with queued data:

https://docs.python.org/3/library/queue.html

In the simplest case, pulling an entry from the queue will look something like this:

```python3
>>> with rx_lock:
      rx_queue.get()
{'params': {'DIAL': 7078000, 'FREQ': 7080748, 'OFFSET': 2748, 'SNR': 4, 'SPEED': 1, 'TDRIFT': 3.59999990\
46325684, 'UTC': 1637172368463, '_ID': -1}, 'type': 'RX.ACTIVITY', 'value': 'ZDXB/R/U00 RP72 ', 'time': \
1637172368.9904108}                                         
>>>
```

As this is a simple python dictionary, you can check the type of this
entry, then extract the text as follows:

```python3
>>> with rx_lock:
      message=rx_queue.get()
>>> message['type']
RX.ACTIVITY
>>> message['value']
ZDXB/R/U00 RP72
>>>
```

You can combine this into a loop with something like the following:

```python3
while(True):
    if(not(rx_queue.empty())):
        with rx_lock:
            message=rx_queue.get()
            if(message['type']=="RX.DIRECTED"):
                print(message)
        time.sleep(0.1)
```

You can, of course, do far more than simply print the received JSON blob.

The four additional types of messages that will show up in the queue are:

* RX.CALL_ACTIVITY - The result of the function call get_call_activity()
* RX.GET_BAND_ACTIVITY - The result of the function call get_band_activity()
* RX.TEXT - The result of the function call get_rx_text()
* INBOX - The result of the functions get_messages() or store_message()

See above for documentation on what these calls do.

## Executables

There are several scripts bundled with the library that show how to do various things, and are useful in their own right. Each of them requires command-line flags or environment variables that point to the JS8Call server. One can use --js8_host and --js8_port, OR you can the environment variables JS8HOST and JS8PORT and combine that with the flag --env (to tell the script to use the env variables). The script that sends your APRS grid square can also optionally get your location from a GPSD server. This can be specified with either --gpsd_host and --gpsd_port, or by setting the GPSDHOST and GPSDPORT environment variables, combined with the --env flag.

A useful bundled utility is groups.py. This script will process your DIRECTED.TXT file produced by JS8Call and write a file called groups.json which contains a list of all groups (ie, @JS8CHESS) seen in your DIRECTED.TXT file, as well as all callsigns of people who either sent traffic to that list, or responded to a query to that list. This file can be processed by your own scripts to do all sorts of interesting things, or you can pull data out of it manually for casual queries (heck, you can just load the JSON file into a text editor, for that matter and search visually). For example, if you just want to see the members (at least the members whose traffic your station was able to receive) of @JS8CHESS, you could, do the following:

```
nobody@mother:~/js8net$ ./groups.py ~/.local/share/JS8Call/DIRECTED.TXT
...
nobody@mother:~/js8net$ jq -r ."JS8CHESS" groups.json 
[
  "WA8WQU",
  "N2VJO",
  "VE3TRQ",
  "NC8R",
  "VE3SCN",
  "KB1CTC",
  "KW9Q",
  "K4KPI",
  "K1OEV",
  "KR4IW",
  "AA0DY",
  "WB4SOM",
  "K5MGK",
  "WE4SEL",
  "KE8NQQ",
  "N0YH",
  "N4JSW",
  "N0JVW",
  "KD2UWR",
  "K4RVA",
  "K1TWH"
]
nobody@mother:~/js8net$ 
```

Note that this is not EVERYBODY who is a member of a given group. It's a list of people who participated in that group during the time period your station was listening on that frequency, and whose data was logged in your DIRECTED.TXT file. The longer you listen, the more data you have to analyze. If you're brand new to JS8Call and your log file only goes back one day, your results will be very different from a user who has log data going back several years. Also note that it's entirely possible that the @BEER group on 20M is entirely different in purpose and membership than the @BEER group on 40M. If you've got both bands in your DIRECTED.TXT file, they'll be combined into one single @BEER group in the JSON file. While it's possible to modify groups.py to make this distinction and keep them separated, it doesn't currently do so.

## Distributed Data Collection and Web Interface

NOTE: I've started over on this part of the code. You'll note that if you run it, it's regressed to much simpler functionality. You'll also note that the code is considerably less horrible. I'm doing an almost from-scratch re-write. The old functionality will come back over time as I get it re-written. Much of the text below is now wrong and/or out of date. I will fix the docs as I fix the code. Consider this functionality as "pre-alpha".

It's important to note that this part of the software is still very much in the development stage, and may have critical vulnerabilities that make exposing the exposed services to the open Internet a Very Bad Idea. While it certainly will work, it's intended for protected, internal LAN use at this time. Also note that at this time, the web server MUST be run from the same directory as all of it's files (JSON files, images, etc). It's not yet smart enough to go look in the "right place" for these resources.

### Monitor
monitor.py provides a central process for the collectors to feed data to, and also serves the web interface to web clients. The monitor receives JS8Call data from the collectors, processes it, stores it, then serves web pages providing this information to the end user. The monitor listens on TCP port 8001 for inbound connections from collectors. While it's certainly possible to expose this port to the Internet, it's probably wiser to require collectors to connect to your site via a VPN.

In order to run the monitor, you'll need to install the yattag and maidenhead python libraries. To install these on a linux or OS/X system, run one of these commands (depending on where you want the libraries installed):

```
pip3 install yattag maidenhead
```
```
sudo pip3 install yattag maidenhead
```

You'll also need the graphviz software package in order to create connectivity graphs. To install this package on a linux or OS/X system, you'll run something similar to the following (your friendly neighborhood search engine will help if these don't work):

```
sudo apt install graphviz
```
```
sudo yum install graphviz
```
```
brew install graphviz
```

monitor.py provides the web interface on TCP port 8000. While the port is configurable, in Linux and other unix-derived operating systems, ports below 1024 require root privileges. It is not recommended to run the monitor process as root. If it's necessary to expose the web service on the normal TCP port 80, it's recommended that you run nginx to front the service. If you're running the service behind a home NAT service, it's usually also possible to do port translation as part of the port forwarding. See your internet provider's documentation for help. Last, but not least, it's also possible to do port-forwarding via IPTables to expose the port 8000 process on port 80.

Be aware that future versions of this software will offer the ability to send data via your radio. In most countries, it's illegal to allow non-monitored, non-licensed users to generate RF traffic under your callsign. While future versions will require explicit flags on the command line at runtime to enable transmission, it's wise to consider what access is allowed to the monitor.py process.

### Collector
collector.py is the agent which talks to your JS8Call instance and extracts data. This data is then sent to the monitor process. By default, it assumes the monitor is running on the same host as the collector on TCP port 8001, but command-line flags allow you to specify a different host (possibly across the Internet) and/or a different port. Any number of collectors (up to bandwidth and CPU limits of the monitor) may be pointed at a single monitor. If the collector operator specifies their call sign and radio type, that data will be displayed on the end user's web page for each received message.

The collector doesn't make a huge effort to properly handle exceptions at this point. If a thread dies, it simply restarts the thread. Future versions of the code will be smarter, but for now, this dumb behavior gets the job done.

### Web Interface

The first table includes the current list of collectors, one for each instance of JS8Call.

The second table includes all traffic seen for the last thirty minutes (this timeout can be changed with command-line flags). If you click on a call sign in the first two columns, a new window/tab will open on pskreporter.info showing all traffic to/from that callsign. If you've installed the FCC callsign file (see below), there will be an extra "Calls" field showing info on the two call signs involved in each transmission. Clicking on one of these calls will take you to that ham's QRZ.com page (assuming you're logged into qrz). In addition, there is a flag icon next to each from/to callsign that will take you to the pskreporter.info map page to visualize reported traffic to/from that callsign.

To have call owner information available, you'll need to download the FCC database and copy the EN.dat file into the directory you run the monitor.py process from. This file is updated daily (though there's no need for you to fetch this file daily) and can be downloaded from:
ftp://wirelessftp.fcc.gov/pub/uls/complete/l_amat.zip. Only the EN.dat file is used by the js8net process.

At some point, I anticipate the option of querying one of the many callsign webpages with public APIs (such as qrz.com) for non-USA call info. For now, the web interface is somewhat USA-centric.


### Known Issues

#### Bugs to be Fixed

* The Javascript code does not properly handle exceptions (because I haven't written the code yet to deal with exceptions), and does odd GUI things when there are certain JSON/network failures.
* Table headers aren't quite right, and do not properly reflect CSS intent (I think I'm missing the <tr> in the <thead> section, but haven't figured out how to add it yet).
* I taught myself Javascript specifically for this web project using a couple of 10+ year-old books I bought at a used book store on a recent road trip. In other words, it's my first ever Javascript project. So if you notice that my Javascript sucks even more than typical Javascript, that's why.
* I'd like to re-write the client-side code in React. Once I learn React.

#### Features to be Added

* Add an adjustable parameter for the "close" highlighting (currently fixed at 150mi)
* Add metric option (for countries who've never sent people to walk on the moon).
* Neither the core library nor the GUI properly handle relays.
* Callsigns with postfixes are handled correctly (ie, "N0CLU/MM"). Callsigns with prefixes are not (ie, "VK0/N0CLU"). This problem is harder to solve than it looks.
* Document the arrl.cty feature.
* You have to re-load the web page to get any new colors specified in color.dat. This isn't a bug, but it's something I may or may not change (making it automatic adds traffic to every transaction every three seconds).
* Not all of the country flags are 100% correct. I think I have all the actual countries right, but a lot of the territories and islands are still 'xx' (ie, undefined) until I get 2-3 hours some boring evening to look them all up.
* Should probably rebuild all of this in react.js at some point. But for now, it works.

### Credits

* The beautiful flag icons are from the project: https://github.com/lipis/flag-icons
* The country callsign mapping is courtesy of: https://www.country-files.com/category/contest/
* The SVG icons are from Creative Commons and Font Awesome Free.
* Thanks to COAS Book in Las Cruces, NM for being awesome. https://www.coasbooks.com/
* Javascript is a truly horrifying language. Not sure who to thank for that.
