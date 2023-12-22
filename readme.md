# Can Visualiser

V1

## Installation Guide

Open CAN_Visualiser Folder in a Code Editor (Eg. VS Code)

Open Terminal with current folder and run the following commands.

```bat

Set-ExecutionPolicy Unrestricted -Scope Process

# Create Virtual Python Environment
python -m venv .venv

# Activate Virtual Python Environment
.venv\Scripts\activate

# Upgrade pip
python -m pip install pip --upgrade

# Install Package Requirements
pip install -r .\requirements.txt

# Create directory for storing CAN Log messages
mkdir log

# Run Python GUI
python master.py
```

## Instruction Guide

Connest to the Serial Port with appropriate Baud Rate

Add Graphs using + Icon

Add and select Channels (Msg IDs)

Click Start to begin plotting

Click Stop once done

Click Disconnect

Close Window to create Log File.
