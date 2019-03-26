# MTGA Basic Land Swapper

Easily change basic land art from exported MTGA decklists using a simple graphical interface.

![screenshot](screenshot.png?raw=true "MTGA Basic Land Swapper")

## Prerequisites

- ### [Python 3.x](https://www.python.org/downloads/)
  - Includes the GUI module Tkinter
- ### [Pillow](https://github.com/python-pillow/Pillow)
  ```
  pip install Pillow
  ```
- ### [pyperclip](https://github.com/asweigart/pyperclip)
  ```
  pip install pyperclip
  ```
  
## Usage

After downloading or cloning the repository, open a command prompt and navigate to the application directory and enter:
```
python landswap.py
```
In Bash you can also use:
```
./landswap.py
```
After a moment the application window should appear. Click the `Import decklist` button in the upper left corner after first exporting a decklist from MTGA or one of the various decklist sharing websites. The decklist should then appear in the text box below. If any basic lands were found they will be highlighted in the decklist and their images to the right will also be highlighted.

To change the land artwork, select the land of your choice from the dropdown menu below each image. Alternatively, use the `Prev` and `Next` buttons to cycle through the available options. The decklist will update automatically to reflect your changes.

When you're finished, click the `Copy to clipboard` button and then import the new decklist into MTGA.

To import another decklist, click the `Clear` button to clear the current decklist and start over.
  
## Legal
  
MTGA Basic Land Swapper is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.
