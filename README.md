Pipulator
---------
Emulate the Bethesda Pipboy Protocol as either the App or the fallout4 game instance.

Requirements
------------
 - netcat (optional)
 - Python 2.7 +
 - The Bethesda PipBoy App
 - Fallout4 for PC

Usage
-----
Built by reverse engineering comms between my Android App and PC game.

To proxy between your game and your app, just run:
```bash
  python pipulator_proxy.py -a [actual game address]
```
Then:
 - Open android app, Connection Setup -> PC
 - select the pipulator from the list


For testing, here's some useful commands:
```bash
  cd [this directory]
  nc [actual_PC_IP] 27000 > captures/gestalt.bin
  while true; do python tcp_fakeserver.py; echo; done &
  python pipulator_proxy.py
```

Known Bugs
----------
 - not complete
 - this is a hack.
 - you might be able to get this working with iOS and an Xbox/PS4, but I don't have either, so I can't say with any certainty.  I do know that smartglass works differently than a PC server would.
 - not quite Python3 compatible.

FAQ
---
 ** None, cause nobody knows this exists yet.