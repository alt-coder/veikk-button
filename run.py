import subprocess
import re
from evdev import ecodes
import evdev
from evdev.util import categorize
from pynput import keyboard
import pickle

viekk_keys = []  # 82, 79, 80, 75, 179, 180, 78
rawl = []   #list of all the keys pressed for registering shortcut keys
mappedkeys = {} # map of keycode and assigned keys shortcut
model = ""  #model of veikk if A30 then set maxButton = 8 else 13

#callback fn when a shortcut key is pressed during registration
def on_press(key):
    if key not in rawl and key != keyboard.Key.esc and key != keyboard.Key.enter:
        print('{0}'.format(
            key), end="+")
        rawl.append(key)


firstenter = 0 # sometime running the script register an Enter key , the variable disable that.

#callback fn when a shortcut key is released during registration
def on_release(key):
    global firstenter
    if key == keyboard.Key.esc:
        rawl.clear()

    if (key == keyboard.Key.enter) and (firstenter != 0):
        # Stop listener
        return False
    firstenter = firstenter+1

# get xinput id to disable the tablet
def getkeyboardid():
    global model
    cmd = "xinput"
    arg = 'list'
    try:
        with subprocess.Popen([cmd, arg], stdout=subprocess.PIPE) as temp:

            # s= str(temp.stdout.read() )
            output = str(temp.communicate())
            # print(output)
            keyboardinput = re.findall(
                r'VEIKK.*?keyboard.+?=\d*', output, re.I)
            if len(keyboardinput) == 0:
                raise Exception(
                    "Veikk tablet not connected use 'xinput list' to check.")
            keyboardinput = str(keyboardinput[0])
            model = keyboardinput
            keyid = re.sub(pattern=r'.*?=', string=keyboardinput, repl='')
            keyid = int(keyid)
            t = subprocess.Popen([cmd, 'float', str(keyid)],
                                 stdout=subprocess.PIPE)
            return keyid
    except:
        raise Exception("Unable to find id")


id = getkeyboardid()
if id == None:
    raise Exception("Unable to find id")

#get the device path 
def getdevice():
    paths = evdev.list_devices()

    for path in paths:
        try:
            d = evdev.InputDevice(path)

            dname = str(d.name)
            if(dname.find('VEIKK') != -1 and dname.find('Keyboard') != -1):
                print(dname)
                return d

        except:
            raise Exception("Veikk Tablet with buttons not Found")


dev = getdevice()

# register all the buttons on the tablet
def getButtons():
    print("Press all the buttons on the tablet one by one in the order you want to assign shourtcuts")
    maxloopcount = 13  # set this variable to maximum button on your Tablet
    if 'A30' in model:
        maxloopcount = 8
    count = 1
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            e = categorize(event)

            if event.code not in viekk_keys:
                viekk_keys.append(event.code)
                print("Unique Button {0} has been registerd".format(count))
                if(count >= maxloopcount):
                    break
                count = count+1


def record():
    print("Usage :- Press the shortcut keys you want to assign and then Press Enter to register the input")
    print("Use backspace to clear the keyboard ShortCut and Re-enter the keys")
    count = 1
    for keycode in viekk_keys:
        print("press the shortcut key for Button ", count)

        with keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        ) as listener:
            listener.join()
        if len(rawl) != 0:
            mappedkeys[keycode] = rawl.copy()
            print("has been registered for Button {0}".format(count))
        rawl.clear()
        count = count+1
    print(mappedkeys)

# fn to simulate key press and release
def press_and_release(keys):
    controller = keyboard.Controller()
    for key in keys:
        controller.press(key)
    for key in reversed(keys):
        controller.release(key)

#handle the events from the tablet.
def handle_events():
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            e = categorize(event)

            if event.code in mappedkeys and event.value == 1:
                press_and_release(mappedkeys[event.code])


# load the objects
def main():
    global mappedkeys
    try:
        with open("shortcut.pkl", "rb") as shortcut:
            mappedkeys = pickle.load(shortcut)
    except (OSError, IOError) as e:
        getButtons()
        record()
        with open("shortcut.pkl", "wb") as shortcut:
            pickle.dump(mappedkeys, shortcut)

    print("Ready to take inputs from the tablet")
    handle_events()

if __name__ == "__main__":
    main()