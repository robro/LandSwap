# MTGA Basic Land Swapper

Easily change basic land art from exported MTGA decklists using a simple graphical interface.

![screenshot](screenshot.png?raw=true "MTGA Basic Land Swapper")

## Prerequisites
- [**Python 3.x**](https://www.python.org/downloads/)
  - Includes the GUI module Tkinter
- [**Pipenv**](https://github.com/pypa/pipenv)
  - Manages dependencies and creates a virtual environment to run the app
  
## Installation
If you don't already have Python 3.x, [download the latest version](https://www.python.org/downloads/) and run the installer, making sure that the **Add Python 3.x to PATH** option is checked. When finished, you will probably need to sign out first to update your environment variables. After signing back in, verify the installation by opening a shell and running:
```
$ python --version
```
Which should output something like `Python 3.7.3`. Next, if you don't already have [Pipenv](https://github.com/pypa/pipenv), install it by running:
```
$ pip install pipenv
```
Once installed, navigate to the application directory created either from cloning this repository or extracting the downloaded .zip file. Then simply run:
```
$ pipenv install
```
This creates a virtual environment and installs all dependencies for this project. It might take a bit but when finished you will be ready to run the app!

## Usage
If you've followed the installation instructions above, navigate to the application directory and run:
```
$ pipenv run python landswap.py
```
After a moment the application window should appear. Click the `Import decklist` button in the upper left corner after first exporting a decklist from MTGA or one of the various decklist sharing websites. The decklist should then appear in the text box below. If any basic lands were found they will be highlighted in the decklist and their images to the right will also be highlighted.

To change the land artwork, select the land of your choice from the dropdown menu below each image. Alternatively, use the `Prev` and `Next` buttons to cycle through the available options. The decklist will update automatically to reflect your changes.

When you're finished, click the `Copy to clipboard` button and then import the new decklist into MTGA.

To import another decklist, click the `Clear` button to clear the current decklist and start over.
  
## Legal
MTGA Basic Land Swapper is unofficial Fan Content permitted under the [Fan Content Policy](https://company.wizards.com/fancontentpolicy). Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.
