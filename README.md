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
