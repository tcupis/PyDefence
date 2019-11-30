# PyDefence v1.0

PyDefence is a new medieval tower defence game by Tom Cupis 
as part of his A-level computer science coursework. It is 
completely customisable with by adding and editing the 
map/units/towers within their respected folders. Within the 
program is a mapping tool for creating and saving maps as well 
as the main game.

## Setting up the game:
```
[Windows]: run 'get-required-packages.bat'
[PIP]: pip install pillow 
```

## Modding notes:

All units and towers (and maps, but use the mapping tool for 
editing these files), are contained in json files which are 
easily readable and should be editable, all new units and towers 
must contain the required attributes and associated image files 
(found within the texture pack)


## Bug reporting:

All bugs should be reported on the github issues page

Bug reports should contain:

	- Description of the bug

	- Steps to repeat the bug

	- The debug log (found in data/debug.data, debug mode must be turned on in the settings menu)

	- System info (OS, OS version, PC specs etc.)


Please visit https://tcupis.itch.io/pydefence for updates and patches.

Server notes:
The server file can be found in the server folder.
The server uses port 1000 [TCP] by default and the client can
be configured to join a domain/ip of your choice.