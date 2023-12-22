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

class SerialCtrl():
    def __init__(self):
        '''
        Initializing the main varialbles for the serial data
        
        '''
        self._Can_Core = Core()
        # self._Can_API = API(self._Can_Core)
        self._Can_API = API(self._Can_Core)
        self._status = False

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

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
        '''
        Method that get the lost of available coms in the system
        '''
        ports = serial.tools.list_ports.comports()
        self.com_list = [com[0] for com in ports]
        self.com_list.insert(0, "--")

    def SerialOpen(self, ComGUI):
        '''
        Method to setup the serial connection and make sure to go for the next only 
        if the connection is done properly
        '''
        PORT = ComGUI.clicked_com.get()
        BAUD = ComGUI.clicked_bd.get()
        
        self.Can_Core.can_monitor(PORT,BAUD)
        self._Can_API = API(self._Can_Core)
        self.status = True

    def SerialClose(self, ComGUI):
        '''
        Method used to close the UART communication
        '''
        self.Can_Core.bus.stop()
        self.status = False
        self.threading = False

    def SerialSync(self, gui):

        num_msgid = len(self.Can_API.get_messages().keys())
        print(num_msgid)
        if( num_msgid > 0 ):
            gui.conn.btn_start_stream["state"] = "active"
            gui.conn.btn_add_chart["state"] = "active"
            gui.conn.btn_kill_chart["state"] = "active"
            gui.conn.save_check["state"] = "active"
            gui.conn.sync_status["text"] = "OK"
            gui.conn.sync_status["fg"] = "green"
            gui.conn.ch_status["text"] = num_msgid
            gui.conn.ch_status["fg"] = "green"
            gui.data.SynchChannel = int(num_msgid)
            gui.data.GenChannels(sorted(self.Can_API.get_messages().keys()))
            gui.data.buildYdata()
            print(gui.data.Channels, gui.data.YData)

    def SerialDataStream(self, gui):
            self.threading = True
            cnt = 0
            channel_list = sorted(self.Can_API.get_messages().keys())
            
            gui.UpdateChart()

            while self.threading:
                # gui.data.SetRefTime()
                gui.data.UpdataXdata()
                i = 0

                for ChNumber in channel_list:
                    # print(ChNumber)
                    history = self.Can_API.get_message_log(int(ChNumber), last =1)    
                    # print(history)
                    for m in history:
                        gui.data.UpdataYdata(i,int.from_bytes(m.data,'little'))
                    i = i+1
                Ysam = [Ys[len(gui.data.XData)-1] for Ys in gui.data.YData]
                gui.data.AdjustData()
                # print(
                #     f"X Len: {len(gui.data.XData)}, Xstart:{gui.data.XData[0]}  Xend : {gui.data.XData[len(gui.data.XData)-1]}, Xrange: {gui.data.XData[len(gui.data.XData)-1] - gui.data.XData[0]} Ydata len: {len(gui.data.YData[0])} Yval: : {Ysam} ")
