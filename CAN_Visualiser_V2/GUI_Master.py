from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import customtkinter
import threading

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


matplotlib.use("QtAgg")
import matplotlib.style as mplstyle
import matplotlib.animation as animation

# mplstyle.use('fast')


from functools import partial


class MyFrame(customtkinter.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)
        # add widgets onto the frame, for example:
        self.label = customtkinter.CTkLabel(self, text=text)
        self.label.grid(row=0, column=0, padx=20)


class RootGUI:
    def __init__(self, serial, data):
        """Initializing the root GUI and other comps of the program"""
        self.root = customtkinter.CTk()
        self.root.title("CAN Visualiser")
        self.root.geometry("460x120")

        # plt.style.use('dark_background')

        # matplotlib.use('Qt5Agg')
        mplstyle.use("fast")

        customtkinter.set_appearance_mode(
            "System"
        )  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme(
            "dark-blue"
        )  # Themes: blue (default), dark-blue, green
        if customtkinter.get_appearance_mode() == "Dark":
            plt.style.use("dark_background")

        # self.root.config(bg="white")
        self.serial = serial
        self.data = data

        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        print("Closing the window and exit")
        self.root.destroy()
        self.serial.SerialClose(self)


# Class to setup and create the communication manager with MCU
class ComGui:
    def __init__(self, root, serial, data):
        """
        Initialize the connetion GUI and initialize the main widgets
        """
        # Initializing the Widgets
        self.root = root
        self.serial = serial
        self.data = data
        self.frame = MyFrame(master=root, text="Com Manager")
        self.frame.grid(sticky="n", padx=5, pady=5)
        # self.frame.configure(text = "hehe")
        self.label_com = customtkinter.CTkLabel(
            self.frame, text="Available Port(s): ", width=15, anchor="w"
        )
        self.label_bd = customtkinter.CTkLabel(
            self.frame, text="Baude Rate: ", width=15, anchor="w"
        )

        # Setup the Drop option menu
        self.baudOptionMenu()
        self.ComOptionMenu()

        # Add the control buttons for refreshing the COMs & Connect
        self.btn_refresh = customtkinter.CTkButton(
            self.frame, text="Refresh", width=10, command=self.com_refresh
        )
        self.btn_connect = customtkinter.CTkButton(
            self.frame,
            text="Connect",
            width=10,
            state="disabled",
            command=self.serial_connect,
        )

        # Optional Graphic parameters
        self.padx = 20
        self.pady = 5

        # Put on the grid all the elements
        self.publish()

    def publish(self):
        """
        Method to display all the Widget of the main frame
        """
        self.frame.grid(row=0, column=0, rowspan=3, columnspan=3, padx=5, pady=5)
        self.label_com.grid(column=1, row=2)
        self.label_bd.grid(column=1, row=3)

        self.drop_baud.grid(column=2, row=3, padx=self.padx, pady=self.pady)
        self.drop_com.grid(column=2, row=2, padx=self.padx)

        self.btn_refresh.grid(column=3, row=2)
        self.btn_connect.grid(column=3, row=3)

    def ComOptionMenu(self):
        """
        Method to Get the available COMs connected to the PC
        and list them into the drop menu
        """
        # Generate the list of available coms

        self.serial.getCOMList()

        self.clicked_com = StringVar()
        self.clicked_com.set(self.serial.com_list[0])

        self.drop_com = customtkinter.CTkOptionMenu(
            self.frame,
            variable=self.clicked_com,
            values=self.serial.com_list,
            width=80,
            command=self.connect_ctrl,
            dynamic_resizing=False,
        )

        # print(self.clicked_com)
        # self.drop_com.configure(width=10)

    def baudOptionMenu(self):
        """
        Method to list all the baud rates in a drop menu
        """
        self.clicked_bd = StringVar()
        bds = [
            "--",
            "300",
            "600",
            "1200",
            "2400",
            "4800",
            "9600",
            "14400",
            "19200",
            "28800",
            "38400",
            "56000",
            "57600",
            "115200",
            "128000",
            "256000",
            "921600",
        ]
        self.clicked_bd.set(bds[0])
        self.drop_baud = customtkinter.CTkOptionMenu(
            self.frame,
            variable=self.clicked_bd,
            values=bds,
            width=80,
            command=self.connect_ctrl,
            dynamic_resizing=False,
        )
        # self.drop_baud.configure(width=10)

    def connect_ctrl(self, widget):
        """
        Mehtod to keep the connect button disabled if all the
        conditions are not cleared
        """
        print("Connect ctrl")
        # Checking the logic consistency to keep the connection btn
        if "--" in self.clicked_bd.get() or "--" in self.clicked_com.get():
            # self.btn_connect["state"] = "disabled"
            self.btn_connect.configure(state="disabled")
            print("yayy")
        else:
            # self.btn_connect["state"] = "active"
            self.btn_connect.configure(state="normal")

    def com_refresh(self):
        print("Refresh")
        # Get the Widget destroyed
        self.drop_com.destroy()

        # Refresh the list of available Coms
        self.ComOptionMenu()

        # Publish the this new droplet
        self.drop_com.grid(column=2, row=2, padx=self.padx)

        # Just in case to secure the connect logic
        logic = []
        self.connect_ctrl(logic)

    def serial_connect(self):
        """
        Method that Updates the GUI during connect / disconnect status
        Manage serials and data flows during connect / disconnect status
        """
        # if self.btn_connect["text"] in "Connect":
        if self.btn_connect.cget("text") in "Connect":
            # Start the serial communication
            self.serial.SerialOpen(self)

            # If connection established move on
            if self.serial.status:
                # Update the COM manager
                # self.btn_connect["text"] = "Disconnect"
                # self.btn_refresh["state"] = "disable"
                # self.drop_baud["state"] = "disable"
                # self.drop_com["state"] = "disable"

                self.btn_connect.configure(text="Disconnect")
                self.btn_refresh.configure(state="disabled")
                self.drop_baud.configure(state="disabled")
                self.drop_com.configure(state="disabled")

                InfoMsg = f"Successful UART connection using {self.clicked_com.get()}"
                messagebox.showinfo("showinfo", InfoMsg)
                self.conn = ConnGUI(self.root, self.serial, self.data)
                self.serial.SerialSync(self)
            else:
                ErrorMsg = f"Failure to estabish UART connection using {self.clicked_com.get()} "
                messagebox.showerror("showerror", ErrorMsg)
        else:
            # Closing the Serial COM
            # Close the serial communication
            self.serial.SerialClose(self)

            InfoMsg = f"UART connection using {self.clicked_com.get()} is now closed"
            messagebox.showwarning("showinfo", InfoMsg)
            # self.btn_connect["text"] = "Connect"
            # self.btn_refresh["state"] = "active"
            # self.drop_baud["state"] = "active"
            # self.drop_com["state"] = "active"

            self.btn_connect.configure(text="Connect")
            self.btn_refresh.configure(state="normal")
            self.drop_baud.configure(state="normal")
            self.drop_com.configure(state="normal")


class ConnGUI:
    def __init__(self, root, serial, data):
        """
        Initialize main Widgets for communication GUI
        """
        self.root = root
        self.serial = serial
        self.data = data

        # Build ConnGui Static Elements

        self.frame = LabelFrame(
            root, text="Connection Manager", padx=5, pady=5, width=60
        )

        # self.frame = MyFrame(master=root,text = "Connection Manager",width = 40)
        # self.frame.grid( padx=5, pady=5)

        self.sync_label = customtkinter.CTkLabel(
            self.frame, text="Sync Status: ", width=15, anchor="w"
        )
        self.sync_status = customtkinter.CTkLabel(
            self.frame, text="..Sync..", text_color="orange", width=5
        )

        self.ch_label = customtkinter.CTkLabel(
            self.frame, text="Active channels: ", width=15, anchor="w"
        )
        self.ch_status = customtkinter.CTkLabel(
            self.frame, text="...", text_color="orange", width=5
        )

        self.btn_start_stream = customtkinter.CTkButton(
            self.frame,
            text="Start",
            state="disabled",
            width=5,
            command=self.start_stream,
        )

        self.btn_stop_stream = customtkinter.CTkButton(
            self.frame, text="Stop", state="disabled", width=5, command=self.stop_stream
        )

        self.btn_add_chart = customtkinter.CTkButton(
            self.frame,
            text="+",
            state="disabled",
            width=5,
            fg_color="#098577",
            command=self.new_chart,
        )

        self.btn_kill_chart = customtkinter.CTkButton(
            self.frame,
            text="-",
            state="disabled",
            width=5,
            fg_color="#CC252C",
            command=self.kill_chart,
        )
        self.save = False
        self.SaveVar = IntVar()
        self.save_check = customtkinter.CTkCheckBox(
            self.frame,
            text="Save data",
            variable=self.SaveVar,
            onvalue=1,
            offvalue=0,
            state="disabled",
            command=self.save_data,
        )

        self.separator = ttk.Separator(self.frame, orient="vertical")

        # Optional Graphic parameters
        self.padx = 20
        self.pady = 5

        # Extending the GUI
        self.ConnGUIOpen()
        self.chartMaster = DisGUI(self.root, self.serial, self.data)

    def ConnGUIOpen(self):
        """
        Method to display all the widgets
        """
        self.root.geometry("800x120")
        self.frame.grid(row=0, column=4, rowspan=3, columnspan=5, padx=5, pady=5)

        self.sync_label.grid(column=1, row=1)
        self.sync_status.grid(column=2, row=1)

        self.ch_label.grid(column=1, row=2)
        self.ch_status.grid(column=2, row=2, pady=self.pady)

        self.btn_start_stream.grid(column=3, row=1, padx=self.padx)
        self.btn_stop_stream.grid(column=3, row=2, padx=self.padx)

        self.btn_add_chart.grid(column=4, row=1, padx=self.padx)
        self.btn_kill_chart.grid(column=5, row=1, padx=self.padx)

        self.save_check.grid(column=4, row=2, columnspan=2)
        self.separator.place(relx=0.58, rely=0, relwidth=0.001, relheight=1)

    def ConnGUIClose(self):
        """
        Method to close the connection GUI and destorys the widgets
        """
        # Must destroy all the element so they are not kept in Memory
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        self.root.geometry("460x120")

    def start_stream(self):
        # self.btn_start_stream["state"] = "disabled"
        # self.btn_stop_stream["state"] = "active"

        self.btn_start_stream.configure(state="disabled")
        self.btn_stop_stream.configure(state="normal")

        self.serial.t1 = threading.Thread(
            target=self.serial.SerialDataStream, args=(self,), daemon=True
        )
        self.serial.t1.start()

    def UpdateChart(self):
        try:
            # mydisplayChannels = []
            if customtkinter.get_appearance_mode() == "Dark":
                plt.style.use("dark_background")
            else:
                plt.style.use("default")

            for MyChannelOpt in range(len(self.chartMaster.ViewVar)):
                self.chartMaster.figs[MyChannelOpt][1].clear()
                for cnt, state in enumerate(self.chartMaster.ViewVar[MyChannelOpt]):
                    if state.get():
                        MyChannel = self.chartMaster.OptionVar[MyChannelOpt][cnt].get()
                        # mydisplayChannels.append(MyChannel)
                        ChannelIndex = self.data.ChannelNum[MyChannel]

                        FuncName = self.chartMaster.FunVar[MyChannelOpt][cnt].get()

                        self.chart = self.chartMaster.figs[MyChannelOpt][1]
                        self.color = self.data.ChannelColor[MyChannel]
                        self.y = self.data.YDisplay[ChannelIndex]
                        self.x = self.data.XDisplay
                        self.data.FunctionMaster[FuncName](self)

                if customtkinter.get_appearance_mode() == "Dark":
                    plt.style.use("dark_background")
                    self.chartMaster.figs[MyChannelOpt][1].grid(
                        color="w", linestyle="-", linewidth=0.2
                    )
                else:
                    plt.style.use("default")
                    self.chartMaster.figs[MyChannelOpt][1].grid(
                        color="b", linestyle="-", linewidth=0.2
                    )

                self.chartMaster.figs[MyChannelOpt][0].canvas.draw()
            # print(mydisplayChannels)
        except Exception as e:
            print(e)
        if self.serial.threading:
            self.root.after(20, self.UpdateChart)

    def stop_stream(self):
        # self.btn_start_stream["state"] = "active"
        # self.btn_stop_stream["state"] = "disabled"

        self.btn_stop_stream.configure(state="disabled")
        self.btn_start_stream.configure(state="normal")
        
        self.serial.threading = False
        # self.serial.SerialStop(self)

    def new_chart(self):
        self.chartMaster.AddChannelMaster()

    def kill_chart(self):
        try:
            if len(self.chartMaster.frames) > 0:
                totalFrame = len(self.chartMaster.frames) - 1
                self.chartMaster.frames[totalFrame].destroy()
                self.chartMaster.frames.pop()
                self.chartMaster.figs.pop()
                self.chartMaster.ControlFrames[totalFrame][0].destroy()
                self.chartMaster.ControlFrames.pop()

                self.chartMaster.ChannelFrame[totalFrame][0].destroy()
                self.chartMaster.ChannelFrame.pop()

                self.chartMaster.ViewVar.pop()
                self.chartMaster.OptionVar.pop()
                self.chartMaster.FunVar.pop()
                self.chartMaster.AdjustRootFrame()
        except:
            pass

    def save_data(self):
        fig = plt.figure()
        msg_id = 1
        if msg_id and msg_id in self.serial.Can_API.get_messages():
            idx = 0
            # Create figure for plotting
            sig_num = len(self.serial.Can_API.get_messages(msg_id).data)

            ax1 = plt.subplot(1, 1, 1)
            ax2 = plt.subplot(1, 1, 1)
            ax3 = plt.subplot(1, 1, 1)

            print(f"Axis1: {ax1}\n")

            # ax1 = fig.add_subplot(2,2,1)
            # ax2 = fig.add_subplot(2,2,2)
            # ax3 = fig.add_subplot(2,2,3)

            xs1 = []
            ys1 = []
            xs2 = []
            ys2 = []
            xs3 = []
            ys3 = []

            # ax = plt.subplots(1,1,1)
            # xs = []
            # ys = []

            # def init():
            # ax1.tick_params(
            #     axis="x",
            #     which="both",
            #     length=0,
            #     labelbottom=False,
            #     labeltop=False,
            #     labelleft=False,
            #     labelright=False,
            # )
            # ax2.tick_params(
            #     axis="x",
            #     which="both",
            #     length=0,
            #     labelbottom=False,
            #     labeltop=False,
            #     labelleft=False,
            #     labelright=False,
            # )
            # ax3.tick_params(
            #     axis="x",
            #     which="both",
            #     length=0,
            #     labelbottom=False,
            #     labeltop=False,
            #     labelleft=False,
            #     labelright=False,
            # )

            # This function is called periodically from FuncAnimation
            def animate(i, xs1, ys1, xs2, ys2, xs3, ys3):
                # Read last 500 messages
                # This could be faster
                history = self.serial.Can_API.get_message_log(msg_id, last=500)

                xs1.clear()
                ys1.clear()
                xs2.clear()
                ys2.clear()
                xs3.clear()
                ys3.clear()

                for m in history:
                    # xs1.append(self.data.XData)
                    # xs1.append(m.timestamp)
                    xs1.append(self.data.XDisplay)
                    ys1.append(m.data[0])
                    ys2.append(m.data[1])
                    ys3.append(m.data[2])

                ax1.clear()
                ax2.clear()
                ax3.clear()

                ax1.plot(xs1, ys1)
                ax2.plot(xs1, ys2)
                ax3.plot(xs1, ys3)

                # Format plot
                ax1.set_title(
                    f"Message { hex(msg_id) } ({ self.serial.Can_API.get_messages(msg_id).count })"
                )
                ax1.set_xlabel(f"{ xs1[-1] }")
                ax1.set_ylabel("data")

                ax2.set_title(
                    f"Message { hex(msg_id) } ({ self.serial.Can_API.get_messages(msg_id).count })"
                )
                ax2.set_xlabel(f"{ xs1[-1] }")
                ax2.set_ylabel("data")

                ax3.set_title(
                    f"Message { hex(msg_id) } ({ self.serial.Can_API.get_messages(msg_id).count })"
                )
                ax3.set_xlabel(f"{ xs1[-1] }")
                ax3.set_ylabel("data")

            # Set up plot to call animate() function periodically
            ani = animation.FuncAnimation(
                fig,
                animate,
                fargs=(xs1, ys1, xs2, ys2, xs3, ys3),
                interval=10,
                # init_func=init,
            )

            plt.show()
        pass

    def UpdateChartAnimation(self):

        def animate():
            for MyChannelOpt in range(len(self.chartMaster.ViewVar)):
                self.chartMaster.figs[MyChannelOpt][1].clear()
                for cnt, state in enumerate(self.chartMaster.ViewVar[MyChannelOpt]):
                    if state.get():
                        MyChannel = self.chartMaster.OptionVar[MyChannelOpt][cnt].get()
                        # mydisplayChannels.append(MyChannel)
                        ChannelIndex = self.data.ChannelNum[MyChannel]

                        self.chart = self.chartMaster.figs[MyChannelOpt][1]
                        self.color = self.data.ChannelColor[MyChannel]
                        self.y = self.data.YDisplay[ChannelIndex]
                        self.x = self.data.XDisplay

        try:
            # mydisplayChannels = []
            if customtkinter.get_appearance_mode() == "Dark":
                plt.style.use("dark_background")
            else:
                plt.style.use("default")

            for MyChannelOpt in range(len(self.chartMaster.ViewVar)):
                self.chartMaster.figs[MyChannelOpt][1].clear()
                for cnt, state in enumerate(self.chartMaster.ViewVar[MyChannelOpt]):
                    if state.get():
                        MyChannel = self.chartMaster.OptionVar[MyChannelOpt][cnt].get()
                        # mydisplayChannels.append(MyChannel)
                        ChannelIndex = self.data.ChannelNum[MyChannel]

                        FuncName = self.chartMaster.FunVar[MyChannelOpt][cnt].get()

                        self.chart = self.chartMaster.figs[MyChannelOpt][1]
                        self.color = self.data.ChannelColor[MyChannel]
                        self.y = self.data.YDisplay[ChannelIndex]
                        self.x = self.data.XDisplay
                        self.data.FunctionMaster[FuncName](self)

                if customtkinter.get_appearance_mode() == "Dark":
                    plt.style.use("dark_background")
                    self.chartMaster.figs[MyChannelOpt][1].grid(
                        color="w", linestyle="-", linewidth=0.2
                    )
                else:
                    plt.style.use("default")
                    self.chartMaster.figs[MyChannelOpt][1].grid(
                        color="b", linestyle="-", linewidth=0.2
                    )

                self.chartMaster.figs[MyChannelOpt][0].canvas.draw()
            # print(mydisplayChannels)
        except Exception as e:
            print(e)
        if self.serial.Can_Core.online:
            self.root.after(20, self.UpdateChart)


class DisGUI:
    def __init__(self, root, serial, data):
        self.root = root
        self.serial = serial
        self.data = data

        self.frames = []
        self.framesCol = 0
        self.framesRow = 20
        self.totalframes = 0

        self.figs = []
        self.toolbars = []

        self.ControlFrames = []

        self.ChannelFrame = []

        self.ViewVar = []
        self.OptionVar = []
        self.FunVar = []

    def AddChannelMaster(self):
        self.AddMasterFrame()
        self.AdjustRootFrame()
        self.AddGraph()
        self.AddChannelFrame()
        self.AddBtnFrame()

    def AddMasterFrame(self):
        self.frames.append(
            LabelFrame(
                self.root,
                text=f"Display Manager - {len(self.frames)+1}",
                padx=5,
                pady=5,
            )
        )
        self.totalframes = len(self.frames) - 1

        if self.totalframes % 2 == 0:
            self.framesCol = 0
        else:
            self.framesCol = 9

        self.framesRow = 100 + 100 * int(self.totalframes / 2)
        self.frames[self.totalframes].grid(
            padx=5, column=self.framesCol, row=self.framesRow, columnspan=9, sticky=NW
        )

        if self.totalframes + 1 == 0:
            frame_height = 120
        else:
            frame_height = 120 + 330 * (int(self.totalframes / 2) + 1)

        self.frames[self.totalframes].width = 170
        self.frames[self.totalframes].height = frame_height

    def AdjustRootFrame(self):
        self.totalframes = len(self.frames) - 1
        if self.totalframes > 0:
            RootW = 800 * 2
        else:
            RootW = 800
        if self.totalframes + 1 == 0:
            RootH = 120
        else:
            RootH = 120 + 330 * (int(self.totalframes / 2) + 1)
        self.root.geometry(f"{RootW}x{RootH}")

    def AddGraph(self):
        if customtkinter.get_appearance_mode() == "Dark":
            plt.style.use("dark_background")
        else:
            plt.style.use("default")

        self.figs.append([])
        self.toolbars.append([])
        self.figs[self.totalframes].append(plt.Figure(figsize=(7, 3), dpi=80))

        self.figs[self.totalframes].append(
            self.figs[self.totalframes][0].add_subplot(111)
        )

        self.figs[self.totalframes].append(
            FigureCanvasTkAgg(
                self.figs[self.totalframes][0], master=self.frames[self.totalframes]
            )
        )

        # self.toolbars[self.totalframes].append(
        #     NavigationToolbar2Tk(
        #         self.figs[self.totalframes][2], self.frames[self.totalframes]
        #     )
        # )
        # self.toolbars[self.totalframes][0].update()

        self.figs[self.totalframes][2].get_tk_widget().grid(
            column=1, row=0, rowspan=17, columnspan=4, sticky=N
        )

        # self.figs[self.totalframes][2]._tkcanvas.grid(
        #     column=1, row=0, rowspan=17, columnspan=4, sticky=N
        # )

    def AddBtnFrame(self):
        btnH = 1
        btnW = 4

        self.ControlFrames.append([])
        self.ControlFrames[self.totalframes].append(
            LabelFrame(self.frames[self.totalframes], pady=5)
        )
        self.ControlFrames[self.totalframes][0].grid(
            column=0, row=0, padx=5, pady=5, sticky=N
        )
        self.ControlFrames[self.totalframes].append(
            customtkinter.CTkButton(
                self.ControlFrames[self.totalframes][0],
                text="+",
                width=btnW,
                height=btnH,
                command=partial(self.AddChannel, self.ChannelFrame[self.totalframes]),
            )
        )
        self.ControlFrames[self.totalframes][1].grid(column=0, row=0, padx=5, pady=5)
        self.ControlFrames[self.totalframes].append(
            customtkinter.CTkButton(
                self.ControlFrames[self.totalframes][0],
                text="-",
                width=btnW,
                height=btnH,
                command=partial(
                    self.DeleteChannel, self.ChannelFrame[self.totalframes]
                ),
            )
        )
        self.ControlFrames[self.totalframes][2].grid(column=1, row=0, padx=5, pady=5)

    def AddChannelFrame(self):
        """
        Methods that adds the main frame that will manage the frames of the options

        """
        self.ChannelFrame.append([])
        self.ViewVar.append([])
        self.OptionVar.append([])
        self.FunVar.append([])
        self.ChannelFrame[self.totalframes].append(
            LabelFrame(self.frames[self.totalframes], pady=5)
        )
        self.ChannelFrame[self.totalframes].append(self.totalframes)

        self.ChannelFrame[self.totalframes][0].grid(
            column=0, row=1, padx=5, pady=5, rowspan=16, sticky=N
        )

        self.AddChannel(self.ChannelFrame[self.totalframes])

    def AddChannel(self, ChannelFrame):
        """
        Method that initiate the channel frame which will provide options & control to the user
        """
        if len(ChannelFrame[0].winfo_children()) < 8:
            NewFrameChannel = LabelFrame(ChannelFrame[0])
            # print(
            #     f"Mumber of element into the Frame {len(ChannelFrame.winfo_children())}")

            NewFrameChannel.grid(
                column=0, row=len(ChannelFrame[0].winfo_children()) - 1
            )

            self.ViewVar[ChannelFrame[1]].append(IntVar())
            Ch_btn = customtkinter.CTkCheckBox(
                NewFrameChannel,
                text=" ",
                variable=self.ViewVar[ChannelFrame[1]][
                    len(self.ViewVar[ChannelFrame[1]]) - 1
                ],
                onvalue=1,
                offvalue=0,
                width=1,
                height=1,
            )
            Ch_btn.grid(row=0, column=0, padx=1)
            self.ChannelOption(NewFrameChannel, ChannelFrame[1])
            self.ChannelFunc(NewFrameChannel, ChannelFrame[1])

    def ChannelOption(self, Frame, ChannelFrameNumber):
        self.OptionVar[ChannelFrameNumber].append(StringVar())

        bds = self.data.Channels

        self.OptionVar[ChannelFrameNumber][
            len(self.OptionVar[ChannelFrameNumber]) - 1
        ].set(bds[0])
        drop_ch = customtkinter.CTkOptionMenu(
            Frame,
            variable=self.OptionVar[ChannelFrameNumber][
                len(self.OptionVar[ChannelFrameNumber]) - 1
            ],
            values=bds,
            width=70,
            dynamic_resizing=False,
        )
        drop_ch.configure(width=50)
        drop_ch.grid(row=0, column=1, padx=1)

    def ChannelFunc(self, Frame, ChannelFrameNumber):
        self.FunVar[ChannelFrameNumber].append(StringVar())

        bds = [func for func in self.data.FunctionMaster.keys()]

        self.FunVar[ChannelFrameNumber][
            len(self.OptionVar[ChannelFrameNumber]) - 1
        ].set(bds[0])
        drop_ch = customtkinter.CTkOptionMenu(
            Frame,
            variable=self.FunVar[ChannelFrameNumber][
                len(self.OptionVar[ChannelFrameNumber]) - 1
            ],
            values=bds,
            width=70,
            dynamic_resizing=False,
        )
        drop_ch.configure(width=50)
        drop_ch.grid(row=0, column=2, padx=1)

    def DeleteChannel(self, ChannelFrame):
        if len(ChannelFrame[0].winfo_children()) > 1:
            ChannelFrame[0].winfo_children()[
                len(ChannelFrame[0].winfo_children()) - 1
            ].destroy()
            self.ViewVar[ChannelFrame[1]].pop()
            self.OptionVar[ChannelFrame[1]].pop()
            self.FunVar[ChannelFrame[1]].pop()


if __name__ == "__main__":
    RootGUI()
    ComGui()
    ConnGUI()
    DisGUI()
