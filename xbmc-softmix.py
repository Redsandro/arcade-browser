# XBMC-starter for older or cheaper soundcards that don't support hardware audiomixing
# Redsandro, 2008-07-29

import os, threading

HOMEDIR="/home/redsandro/.xbmc/scripts/Arcade\ Browser"

class KeepAlsaBusy (threading.Thread):
	def run (self):
		os.system('mplayer -ao alsa -input file='+HOMEDIR+'/mplayer.cmd /usr/share/xbmc/skin/Project\ Mayhem\ III/sounds/back.wav')

KeepAlsaBusy().start()
os.system('xbmc')
# Command to kill the thread here if you want mplayer to quit together with xbmc
# I just don't know how to do that.. yet. So please tell me :)

#import sys
#sys.exit(1)
