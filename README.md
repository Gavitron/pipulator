Pipulator
---------
Emulate the Bethesda Pipboy Protocol as either the App or the fallout4 game instance.

Requirements
------------
 - netcat (nc)
 - Python
 - The Bethesda PipBoy App
 - Fallout4 for PC

Usage
-----
Built by reverse engineering comms between my Android App and PC game.

```bash
 cd [this directory]
 nc [your_PC_IP] 27000 > repl.txt
 python handshake.py &
 python tcp_srv.py
```
 - Open android app, Connection Setup -> PC 
 - select your pipulator from the list


Known Bugs
----------
 - not complete
 - this is a hack.
 - you might be able to get this working with iOS and an Xbox/PS4, but I don't have either, so I can't say with any certainty.  I do know that smartglass works differently than a PC server would.

FAQ
---
 ** None, cause nobody knows this exists yet.