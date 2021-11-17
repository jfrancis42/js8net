# js8net
### _Jeff Francis <jeff@gritch.org>_

Early draft. Not ready to use.

Note that it's up to you to process incoming messages that are not
already processed by the library. The incoming message queue is
rx_queue, and the lock for it (don't forget to use the lock!) is
rx_lock.

If you don't want to block on incoming messages, see the queue docs
here:

https://docs.python.org/3/library/queue.html

Let me reiterate for all to hear how much multi-byte characters suck
Satan's white ass. For the love of God, this is one thing they got
right in Python2. The convolutions in this code to deal with
multi-byte characters strings that may or may not have been cut off in
the middle of a two-byte sequence due to network packetization is an
Unholy mess. But in the end, it works. It's just a thousand times
uglier than it would be in Python2.
