# Setup

First of all a big thanks to @[jilam5555](https://github.com/jlam55555) for writing the driver for veikk graphic tablet see [this](https://github.com/jlam55555/veikk-linux-driver)

You must have the following dependencies to get started

1. linux-header see [this](https://askubuntu.com/questions/554624/)

2. [pip](https://pip.pypa.io/en/stable/installing/)

3. [libevdev](https://python-evdev.readthedocs.io/en/latest/install.html)

4. [pynput](https://pypi.org/project/pynput/)

Now clone the repo and run in the terminal 

```bash
make
sudo make all install clean
```

restart your computer and run

`/bin/python run.py   `

follow the instructions to setup the shortcut keys.

The mapping is saved in `shortcut.pkl` file so if you want to reset , delete the file.

