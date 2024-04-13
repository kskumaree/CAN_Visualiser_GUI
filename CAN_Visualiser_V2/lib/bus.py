import can
import asyncio
import time

from datetime import datetime


class Bus:
    def __init__(self, interface, br):
        if interface:
            print("interface is")
            print(interface)
            self._can_bus = can.ThreadSafeBus(
                bustype="serial",
                channel=interface,
                baudrate=br,
                receive_own_messages=True,
            )
        else:
            self._can_bus = None

        self._filter_rules = []
        self._history = []
        self._loop = None
        self._notifier = None
        self._online = False

    @property
    def can_bus(self):
        return self._can_bus

    @property
    def filter_rules(self):
        return self._filter_rules

    @filter_rules.setter
    def filter_rules(self):
        return self._filter_rules

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value):
        self._history = value

    @property
    def notifier(self):
        return self._notifier

    @notifier.setter
    def notifier(self, value):
        self._notifier = value

    @property
    def online(self):
        return self._online

    @online.setter
    def online(self, value):
        self._online = value

    async def listen(self, callback):
        reader = can.AsyncBufferedReader()

        try:
            logger = can.Logger(
                f"log/{ datetime.now().isoformat(timespec='seconds') }.log"
            )
        except:
            logger = can.Logger(
                "log/{}.log".format(datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p"))
            )

        # Set up listeners and add callback functions
        listeners = [
            reader,  # AsyncBufferedReader() listener
            logger,  # Regular Listener object
        ]
        listeners.extend(callback)

        loop = asyncio.get_event_loop()

        # Create Notifier with an explicit loop to use for scheduling of callbacks
        self.notifier = can.Notifier(self.can_bus, listeners, timeout=1.0, loop=loop)

        while True:
            # Wait for next message from AsyncBufferedReader
            msg = await reader.get_message()
            self.history.append(msg)

    def start(self, callback):
        self.online = True
        asyncio.run(self.listen(callback))

    def stop(self):
        print("Exiting...")
        self.notifier.stop()
        self.can_bus.shutdown()
        self.online = False
