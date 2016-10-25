#Arcade Browser for XBMC/Linux

To my surprise, I was recently asked if I still have the source code to my old XBMC plugin _Arcade Browser_.
Arcade-browser was a nice GUI for browsing ROMs for multiple emulators using a remote control.

## Changelog

#### 2010 v0.2b3

* Arcade Browser is no longer maintained.
* See this fork: [Rom Collection Browser](https://github.com/maloep/rom-collection-browser)
* http://forum.kodi.tv/showthread.php?tid=48983&pid=571066#pid571066

#### 2009 v0.2

* Public release
* http://forum.kodi.tv/showthread.php?tid=48983

#### 2008 v0.1

* Rom browser for personal use

###Old readme follows.

---

Arcade Browser 0.2b for XBMC *LINUX*!
==================

By Sander AKA Redsandro
[http://www.rednet.nl/en/vision/articles/222](https://web.archive.org/web/20110817104514/http://www.rednet.nl/en/vision/articles/222)

Created: 2008-07-24  
Updated: 2010-01-27

Quick notes:
------------

This version is **NOT for XBOX**, **NOT for Windows** and **NOT for Mac OS**.

This version is not compatible with your `autoexec.py`.
Arcade Browser will try to backup your original script and then destroy it just for fun.

In order to do that, make sure you have write permissions for `/usr/share/XBMC/scripts` (and `autoexec.py` if it's there already).



Readme:
-------

I started building a Linux Media Center out of an old Pentium 3 when my laptop - from which I watched movies on television - broke down. And I always wanted to bring my arcade collection to the television in a way that it's actually fon to due. I got me XBMC since my brother recommended it and it saved me a lot of trouble getting MythTV to work. No TV in there, but I could not use the analog TV card anyway since our analog signal is replaced with digital.

XBMC is great. For this script I used `2.1a2-hardy2` as it comes out of the (Synaptic) box, with Ubuntu 8.04.
No changes. Default skin.

Now for the Arcade part..

You know how it works. A bit of google and so I tried some emulator scripts and they all didn't work. I checked them out and didn't get what all these weird files are being used for but I guess it makes sense if I wasn't such an XBMC n00b. Also things get confusing when there's 1 original and 3 ports of the software. Luckily it's not like an emulator script is a 3d engine or something so I decided I might as well make one myself. Just very plain simple what I want, not thinking about skins, languages, xbox-native binaries, whatever... and it's a good excuse to learn a bit of python.

So.. expect no options whatsoever. I think it's only compatible with the default skin, but actually I don't even know how skins work. I mean, if using other skins keeps fonts and colors the same, then it probably will work.

Just check out `emulators.ini` and you'll know what to do.



Quick setup:
------

* Copy everything to `\home\user\.xbmc\scripts\My Scripts\Arcade Browser` and give it write permission.
  * Note that images go inside `.\images`.
* Give `/usr/share/XBMC/scripts` write permission for user.
* Manually edit `emulators.ini`. The file explains itself.
* Run the script. All ROMs will be indexed according to your `settings.ini`. If anything goes wrong, it's probably your fault.



Change History:
---------------

####v0.3 Does not exist. To do:
* Option to blacklist or favourite certain ROMs with RED and GREEN on the remote.
* Switch lists: All, Blacklisted, or Favourited (remember choice in ab.cfg ofcourse)
* Save space separated file of all blacklisted files so it can easily be pasted in a terminal combined with the magic letters `rm` to quickly rid all garbage.

####v0.2b# Work in Progress/To Do:
* Cancel the autoselect (0.2b2) when you navigate before the list is fully loaded. All code seems to get ignored while list is being loaded. Probably a separate thread does the trick. But I can't figure it out.
  * In the same way, launching a game should happen immediately, not waiting until after the list is fully loaded.
  * Also, select the game while it is being added to the list, not when the list is complete. This code also doesn't work in the current form.
* Is there a trick to build long lists faster?
* If ROM has a description and/or a preview image, display. If not, display emulator pic/desc.

####v0.2b3 (2010-01-27)
* Fixed solo mode

####v0.2b2 (2009-02-30)
* Implemented the xml cache.
* Win32 apps through wine now work with the file selector.
* Last launched game will be selected when you return from the emulator.
  * The selection will only come through when the ROM list is fully loaded. (Yes this can be an issue, try having 2000 items.)

####v0.1b3 (2008-08-03)
* Experimental xml caching of ROMs to speed up loading. Why? My Media Center is a slow 800MHz machine.
* Support aided by shellscripts, not very friendly. Never got to finish it because certain things broke and XBMC (2.1a2-hardy2) had too many bugs that only affected my computer.
* Multiple minor tweaks

####0.1b2 (2008-07-24)
* Different layout and fixes for sound problems in chainloaded emulators

####0.1b (2008-07-07)
* Initial version, browsing directly from disk.
