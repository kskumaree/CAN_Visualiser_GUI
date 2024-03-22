import time
import numpy as np


class DataMaster():
    def __init__(self):
        self.sync = "#?#\n"
        self.sync_ok = "!"
        self.StartStream = "#A#\n"
        self.StopStream = "#S#\n"
        self.SynchChannel = 0

        self.msg = []

        self.XData = []
        self.YData = []
        self.XData_with_Timestamp = []
        self.RefTime = 0

        self.FunctionMaster = {
            "RowData": self.RowData,
            "VoltageDisplay": self.VoltData
        }

        self.DisplayTimeRange = 0.001

        self.Channels = []
        self.ChannelNumList = [0,1,2,3,4,5,6,7]
        self.ChannelColorList = ['blue','green','red','cyan','magenta','yellow','black','white']
        self.ChannelNum = {
            'Ch0': 0,
            'Ch1': 1,
            'Ch2': 2,
            'Ch3': 3,
            'Ch4': 4,
            'Ch5': 5,
            'Ch6': 6,
            'Ch7': 7
        }
        self.ChannelColor = {
            'Ch0': 'blue',
            'Ch1': 'green',
            'Ch2': 'red',
            'Ch3': 'cyan',
            'Ch4': 'magenta',
            'Ch5': 'tab:brown',
            'Ch6': 'black',
            'Ch7': 'maroon'
        }

    def DecodeMsg(self):
        temp = self.RowMsg.decode('utf8')
        if len(temp) > 0:
            if "#" in temp:
                self.msg = temp.split("#")
                del self.msg[0]
                if self.msg[0] in "D":
                    self.messageLen = 0
                    self.messageLenCheck = 0
                    del self.msg[0]
                    del self.msg[len(self.msg)-1]
                    self.messageLen = int(self.msg[len(self.msg)-1])
                    del self.msg[len(self.msg)-1]
                    for item in self.msg:
                        self.messageLenCheck += len(item)

    def GenChannels(self,msg_ids):
        print(msg_ids)
        # self.Channels = [f"Ch{ch}" for ch in range(self.SynchChannel)]
        self.Channels = [f"{ch}" for ch in msg_ids]
        # self.Channels = msg_ids
        self.ChannelNum = {self.Channels[i]: self.ChannelNumList[i] for i in range(len(self.Channels))}
        self.ChannelColor = {self.Channels[i]: self.ChannelColorList[i] for i in range(len(self.Channels))}

        print(self.ChannelColor)
        print(self.ChannelNum)

    def buildYdata(self):
        self.YData = []
        for _ in range(self.SynchChannel):
            self.YData.append([])
    
    def buildXdata_with_Timestamp(self):
        self.XData_with_Timestamp = []
        for _ in range(self.SynchChannel):
            self.XData_with_Timestamp.append([])

    def ClearData(self):
        self.RowMsg = ""
        self.msg = []
        self.YData = []
        self.XData_with_Timestamp = []

    def IntMsgFunc(self):
        self.IntMsg = [int(msg) for msg in self.msg]

    def StreamDataCheck(self):
        self.StreamData = False
        if self.SynchChannel == len(self.msg):
            if self.messageLen == self.messageLenCheck:
                self.StreamData = True
                self.IntMsgFunc()

    def SetRefTime(self):
        if len(self.XData) == 0:
            self.RefTime = time.perf_counter()
        else:
            self.RefTime = time.perf_counter() - self.XData[len(self.XData)-1]

    def UpdataXdata(self):
        if len(self.XData) == 0:
            self.XData.append(0)
        else:
            self.XData.append(time.perf_counter()-self.RefTime)

    def UpdataXdata_with_Timestamp(self,ChNumber,Data):
        self.XData_with_Timestamp[ChNumber].append(Data)

    def UpdataYdata(self,ChNumber,Data):
        self.YData[ChNumber].append(Data)

    def AdjustData(self):
        lenXdata = len(self.XData)
        if (self.XData[lenXdata-1] - self.XData[0]) > self.DisplayTimeRange:
            del self.XData[0]
            for ydata in self.YData:
                del ydata[0]

        x = np.array(self.XData)
        self.XDisplay = np.linspace(x.min(), x.max(), len(x), endpoint=0)
        self.YDisplay = np.array(self.YData)

    def RowData(self, gui):
        gui.chart.plot(gui.x, gui.y, color=gui.color,
                       dash_capstyle='projecting', linewidth=1)

    def VoltData(self, gui):
        gui.chart.plot(gui.x, (gui.y), color=gui.color,
                       dash_capstyle='projecting', linewidth=1)
        