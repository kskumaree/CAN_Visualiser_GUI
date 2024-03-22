import serial.tools.list_ports  # pip install pyserial

# Secure the UART serial communication with MCU

import importlib
import pkgutil
from threading import Thread
from can import CanutilsLogReader

from CANCore.cancore import Core
from lib.bus import Bus
from lib.message import Messages
from lib.api import API


class SerialCtrl:
    def __init__(self):
        """
        Initializing the main varialbles for the serial data

        """
        self._Can_Core = Core()
        # self._Can_API = API(self._Can_Core)
        self._Can_API = API(self._Can_Core)
        self._status = False

        self._channel_list =[]

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def channel_list(self):
        return self._channel_list

    @channel_list.setter
    def channel_list(self, value):
        self._channel_list = value

        

    ############## CLI ##########
    @property
    def Can_Core(self):
        return self._Can_Core

    @property
    def Can_API(self):
        return self._Can_API

    @Can_API.setter
    def Can_API(self, value):
        self._Can_API = value

    def getCOMList(self):
        """
        Method that get the list of available coms in the system
        """
        ports = serial.tools.list_ports.comports()
        self.com_list = [com[0] for com in ports]
        self.com_list.insert(0, "--")

    def SerialOpen(self, ComGUI):
        """
        Method to setup the serial connection and make sure to go for the next only
        if the connection is done properly
        """
        PORT = ComGUI.clicked_com.get()
        BAUD = ComGUI.clicked_bd.get()

        self.Can_Core.can_monitor(PORT, BAUD)
        self._Can_API = API(self._Can_Core)
        self.status = True

    def SerialClose(self, ComGUI):
        """
        Method used to close the UART communication
        """
        self.Can_Core.bus.stop()
        self.status = False
        self.threading = False

    def SerialSync(self, gui):
        local_list = []
        self.Can_Core.db.import_definitions("can.dbc")
        if self.Can_Core.db.definitions:
            print(f"Imported {len(self.Can_Core.db.definitions.messages)} definitions")

        msg_list = sorted(self.Can_API.get_messages().keys())
        num_msgid = len(msg_list)
        print(num_msgid)

        for msg_id in msg_list:
            msg_def = self.Can_API.db.definitions.get_message_by_frame_id(msg_id)
            name = msg_def.name
            print(name)
            msg = self.Can_API.get_messages(msg_id)
            msg.label = name
            for signal in msg_def.signals:
                local_list.append(signal.name)
                # print(signal.raw_initial)
            # print(msg.data)
            # print(msg_def.decode_simple(msg.data))
                history = self.Can_API.get_message_log(int(msg_id), last=1)
                for m in history:
                    sig_data = self.Can_API.db.definitions.decode_message(msg_id,m.data)
                    print(sig_data[signal.name])

        print(local_list)
        num_channels = len(local_list)
        channel_list = local_list
        if num_msgid > 0:
            gui.conn.btn_start_stream["state"] = "active"
            gui.conn.btn_add_chart["state"] = "active"
            gui.conn.btn_kill_chart["state"] = "active"
            gui.conn.save_check["state"] = "active"

            gui.conn.btn_start_stream.configure(state="normal")
            gui.conn.btn_add_chart.configure(state="normal")
            gui.conn.btn_kill_chart.configure(state="normal")
            gui.conn.save_check.configure(state="normal")

            # gui.conn.sync_status["text"] = "OK"
            # gui.conn.sync_status["fg"] = "green"

            gui.conn.sync_status.configure(text="OK")
            gui.conn.sync_status.configure(text_color="green")

            # gui.conn.ch_status["text"] = num_msgid
            # gui.conn.ch_status["fg"] = "green"

            gui.conn.ch_status.configure(text=num_channels)
            gui.conn.ch_status.configure(text_color="green")

            gui.data.SynchChannel = int(num_channels)
            gui.data.GenChannels(channel_list)
            gui.data.buildYdata()
            print(gui.data.Channels, gui.data.YData)

        

    def SerialDataStream(self, gui):
        self.threading = True
        # self.Can_Core.db.import_definitions("can.dbc")
        if self.Can_Core.db.definitions:
            print(f"Imported {len(self.Can_Core.db.definitions.messages)} definitions")

        msg_list = sorted(self.Can_API.get_messages().keys())
        num_msgid = len(msg_list)
        print(num_msgid)

        

        gui.UpdateChart()

        while self.threading:
            gui.data.SetRefTime()
            gui.data.UpdataXdata()

            # i = 0
            # for ChNumber in channel_list:
            #     # print(ChNumber)
            #     history = self.Can_API.get_message_log(int(ChNumber), last=1)
            #     # print(history)
            #     for m in history:
            #         gui.data.UpdataYdata(i,int.from_bytes(m.data,'little'))
            #         # gui.data.UpdataYdata(i, m.data[0])
            #         # print(len(m.data))
            #     i = i + 1


            i = 0
            for msg_id in msg_list:
                msg_def = self.Can_API.db.definitions.get_message_by_frame_id(msg_id)
                history = self.Can_API.get_message_log(int(msg_id), last=1)
                for m in history:
                    for signal in msg_def.signals:
                        sig_data = self.Can_API.db.definitions.decode_message(msg_id,m.data)
                        y_data = sig_data[signal.name]
                        gui.data.UpdataYdata(i,y_data)
                        i = i+1

            # Ysam = [Ys[len(gui.data.XData) - 1] for Ys in gui.data.YData]
            gui.data.AdjustData()
            # print(
            #     f"X Len: {len(gui.data.XData)}, Xstart:{gui.data.XData[0]}  Xend : {gui.data.XData[len(gui.data.XData)-1]}, Xrange: {gui.data.XData[len(gui.data.XData)-1] - gui.data.XData[0]} Ydata len: {len(gui.data.YData[0])} Yval: : {Ysam} ")
