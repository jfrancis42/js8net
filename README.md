# js8net

#### _Jeff Francis <jeff@gritch.org>_, N0GQ



## The Library

js8net is a python3 package for interacting with the JS8Call API. It works exclusively in TCP mode. It *might* work with python2. I haven't tried it. If it doesn't work, but you'd like it to, I'll happily consider your patches for inclusion.

The JS8Call API is a bit painful to use directly from your own code for several reasons:

- It's essentially undocumented. While there are some partial docs floating around, mostly you have to read the JS8Call source code. Specifically, the MainWindow::networkMessage() function in mainwindow.cpp will tell you what functions are available and what the parameters required and returned are.

- The API is completely asynchronous. You send commands to JS8Call whenever you wish, and it sends the reply whenever it's good and ready. Or maybe not. As a result, without an API library, you have to keep track of what queries were sent, then attempt to match up random replies with the original queries.

- It's incomplete. You cannot mark INBOX messages as read (or delete them). You cannot toggle SPOT on or off. You cannot trigger a contact log. You cannot toggle TX on or off. You cannot enable or disable Autoreply, Heartbeat Networking, Heartbeat Acknowledgements, change Decoder Sensitivity, turn simultaneous decoding on or off, change callsign groups, change Station Status, change the CQ or Reply messages. I'd also love to see an API call to generate a message checksum (for a message I'm generating) and to validate the checksum of a received message.

- The API is completely disconnected from the GUI. If you make a change using the API, for example changing the speed from Normal to Slow or changing your grid square, those changes are invisible in the GUI. The changes happen, but they're not reflected on the screen, leading to a very confusing state.

- API usage does not reset the idle timeout. Meaning that after the specified period of time without interacting with the GUI, all transmission stops until you click the timeout "OK" notice with a mouse. And the maximum time the timeout can be set for is only 1440 minutes (24 hours). You can get rid of this behavior by setting IDLE_BLOCKS to FALSE in the C++ source and recompiling, but recompiling JS8Call is quite painful compared with most software, and is horrifically slow on the Pi. I have an icky, but usable work-around below.

- There are many errors and notices, such as serial comms errors between the software and your laptop, that can only be cleared or retried by clicking the mouse on the screen. They cannot be handled via the API.

This library is an attempt to hide as much of the API's complexity as possible behind a more traditional query/reply paradigm. It also tries to make up for some of the API's shortcomings as best it can.

As you use this API, keep in mind the architecture of JS8Call itself that doesn't allow API changes to be visible in the GUI. It will confuse you until you get used to it. If you change the grid square using the API, the GUI will still show the old grid square. If you change your transmission speed using the API, the GUI will still show the old transmission speed. Everything will work just fine, but it will look wrong on screen. There are bugs open against JS8Call to fix this.

While JS8Call by and large does work well, it's been two years since the last release, and there are numerous anticipated bug fixes supposedly in the works that should make JS8Call a much better piece of software to work with via the API.

## Transmit Timeout Work-Around

If you're not interested in recompiling JS8Call from scratch, there's a work-around (at least for Linux users): xdotool. xdotool is a handy tool for faking various mouse and keyboard events under X11. I wrote a simple little shell script that keeps JS8Call from going to sleep by moving the mouse to the text entry box in the GUI once per hour, then "clicking" the left mouse button. Once per hour is very much overkill, as once ever 24 hours would be enough. Whatever, it works on both x86 Linux and on the Pi. Windows and Mac users, I don't know the answer for you. You'll have to determine the appropriate X and Y coordinates on your screen for the little box to click in, and that will depend on the resolution of your screen, the size of the JS8Call window (I maximize mine), and the position of the JS8Call windows relative to the top left corner (which isn't relevant if it's maximized, it's always 0,0). On my laptop, the right spot is 1300,1100. So I just put the following script in a file and run it in an xterm:
````bash
#!/bin/bash

while [ 1 ]
do
	xdotool search --name "JS8Call" windowactivate %@ \
		mousemove 1300 1100 click 1
	sleep 3600
done
````

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

## The New (very alpha quality) Web Interface

I'm working on a new web interface for monitoring and interacting with JS8Call using the js8net library. It's very much in an alpha stage at this point, but it does (mostly) work. If you point it at a running JS8Call instance, it will provide you a running update on what your system is doing and who it's hearing. If you provide it with an EN.dat file (downloaded from the FCC at the link below) in the directory you run the web interface from, it'll even include the info on the callsigns heard. Note that in it's current alpha state, this only works for US callsigns.

The download link for the FCC callsign date (updated daily, though you certainly don't have to update your own file daily) is here:
ftp://wirelessftp.fcc.gov/pub/uls/complete/l_amat.zip

At some point, I anticipate the option of querying one of the many callsign webpages with public APIs (such as qrz.com) for this info, allowing for resolution of non-US callsigns.

For now, the "Send Grid" and "Send Heartbeat" buttons do work perfectly. The "Send Text Message" and "Send Email" buttons do not (yet). And the "Query" button for asking for unresolved grid squares sort of work some of the time (actually, it sends the query fine, it just sometimes doesn't "hear" the answer properly). It's alpha code. Deal with it.

Note that IMHO, it would NOT be wise to expose this web page to the open internet. It allows anyone who stumbles across the page to send transmissions over radio with your callsign attached to them, but completely out of your control. In most countries (USA include), this is illegal. I anticipate putting a --read-only flag in the code at some point so you can expose what your station hears without the risk of random people sending data, but that does not yet exist. You've been warned...
