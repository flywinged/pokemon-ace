import typing, pyautogui, pyperclip, time

def addScriptLine(line: str, indent: int = 0) -> str:
    return (" " * (4 * indent)) + line + "\n"

HMA_IS_OPEN = False

def openHMA():
    global HMA_IS_OPEN
    if not HMA_IS_OPEN:
        pyperclip.copy("C:\\Users\\clayt\\Desktop\\HexManiacAdvance\\HexManiacAdvance.exe")
        pyautogui.press("win")
        time.sleep(1)
        pyautogui.keyDown("ctrl")
        pyautogui.press("v")
        pyautogui.keyUp("ctrl")
        time.sleep(.5)
        pyautogui.press("return")
        time.sleep(5)
        pyautogui.keyDown("ctrl")
        pyautogui.press("o")
        pyautogui.keyUp("ctrl")
        pyperclip.copy("C:\\Users\\clayt\\Desktop\\pokemon-calamity\\ROMS\\calamity.gba")
        time.sleep(2)
        pyautogui.keyDown("ctrl")
        pyautogui.press("v")
        time.sleep(.5)
        pyautogui.keyUp("ctrl")
        pyautogui.press("return")
        time.sleep(5)
        pyautogui.press("escape")
        time.sleep(1)
        HMA_IS_OPEN = True

# Expected to pass in a list of filenames
def writeHMAScriptInHMA(scripts: typing.List[str], close: bool = True):
    openHMA()

    for script in scripts:
        with open(f"./Scripts/HMA/scripts/{script}.hma", "r", encoding="utf_8_sig") as f:
            hmaScript = f.read()
            pyperclip.copy(hmaScript)
            time.sleep(1)
            pyautogui.keyDown("ctrl")
            pyautogui.press("v")
            pyautogui.keyUp("ctrl")
            time.sleep(10)

    saveHMA()
    if close:
        closeHMA()

def writePythonScriptInHMA(scripts: typing.List[str], close: bool = True):

    openHMA()
    pyautogui.keyDown("ctrl")
    pyautogui.press("r")
    pyautogui.keyUp("ctrl")
    time.sleep(.5)
    
    # Now we copy and run each script
    for script in scripts:
        pyperclip.copy(script)
        pyautogui.keyDown("ctrl")
        pyautogui.press("v")
        pyautogui.keyUp("ctrl")
        time.sleep(1)
        pyautogui.keyDown("ctrl")
        pyautogui.press("return")
        pyautogui.keyUp("ctrl")
        time.sleep(10)
        pyautogui.keyDown("ctrl")
        pyautogui.press("a")
        pyautogui.keyUp("ctrl")
        time.sleep(.5)
        pyautogui.press("delete")
    
    # Close out of the sidebar and save
    pyautogui.keyDown("ctrl")
    pyautogui.press("r")
    pyautogui.keyUp("ctrl")
    time.sleep(.5)

    saveHMA()
    
    # Close HMA if require
    if close:
        closeHMA()

def saveHMA():
    time.sleep(0.5)
    pyautogui.keyDown("ctrl")
    pyautogui.press("s")
    time.sleep(0.5)
    pyautogui.keyUp("ctrl")

def closeHMA():
    global HMA_IS_OPEN
    if HMA_IS_OPEN:
        saveHMA()
        time.sleep(1)
        pyautogui.keyDown("alt")
        pyautogui.press("f4")
        pyautogui.keyUp("alt")
        time.sleep(1)
        HMA_IS_OPEN = False
    