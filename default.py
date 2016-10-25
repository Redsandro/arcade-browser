# Arcade Browser - list ROMs and launch command line emulators
# Copyright (C) 2008-2010 Sander S AKA Redsandro <redsandro@gmail.com> (http://www.Redsandro.com/)
#
# File:		default.py
# Created:	2008-07-23
# Updated:	2010-01-27
#
# Notes:
# ######
#
# This script needs write permission on /usr/share/xbmc/scripts,
# So [user] either be in the group or have [others] write permissions.
#
# License:
# ########
#
# This script is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY WHATSOEVER. Use at your own risk.
#
# See <http://www.gnu.org/licenses/>.

import getpass, ntpath, os, re, sys, string, xbmc, xbmcgui
from xml.dom.minidom import Document, parseString

# Global constants
#

VERSION = "0.2b3"			# Version
INIFILE = "emulators.ini"	# Manually editable emulator file
XMLFILE = "romlist.xml"		# Cached roms
DEBUG = 'true'				# Set to true to dispaly script info at the bottom of the screen

# Paths
HOMEDIR = os.getcwd().replace(";","")+"/"	# script.dirname #SELFNOTE: Remove trail slash, it's uncommon
SCRIPTHOME = ntpath.dirname(ntpath.dirname(HOMEDIR)) # blaat/.xbmc/scripts/My Scripts
SCRIPTUSR = "/usr/share/xbmc/scripts"

# Distinct menus
MENU_EMULIST = int(1)
MENU_ROMLIST = int(2)

# Keymap
# See guilib/Key.h
ACTION_MOVE_UP =		int(3)
ACTION_MOVE_DOWN =		int(4)
ACTION_PARENT_DIR =		int(9)
ACTION_PREVIOUS_MENU =	int(10)
ACTION_SHOW_INFO =		int(11) # GREEN - 195
ACTION_CONTEXT_MENU =	int(117) # RED - 229
ACTION_SHOW_GUI =		int(18) # YELLOW - 213



class ArcadeBrowser(xbmcgui.Window):

	# Global vars
	currMenu = int(0)	# Where are we
	selEmu = int(-1)	# What is selected
	selRom = int(-1)
	numEmu = int(0)		# Emu's
	#emulators = ""
	prog = int(0)		# progress indicator
	busy = False
	abort = False
	romDesc = {}		# Descriptions
	romWhite = {}
	romBlack = {}

	# Constructor
	def __init__(self):
		self.setCoordinateResolution(6)

		#
		# Menu
		
		# Build screen
		self.addControl(xbmcgui.ControlImage(0,0, 720,576, HOMEDIR+'images/background.png'))
		self.addControl(xbmcgui.ControlLabel(56,45, 200, 145, 'Arcade Browser v'+VERSION, 'special12', '0xFFFFFFFF'))
		self.addControl(xbmcgui.ControlImage(211, 29, 64, 43, HOMEDIR+"images/rednet.png"))
		self.addControl(xbmcgui.ControlLabel(280, 50, 200, 100, 'www.REDnet.nl', 'font101', '0xFFCCCCFF'))
		self.addControl(xbmcgui.ControlLabel(56,65, 200, 135, 'Emulators', 'special13', '0xFFFFFF00'))

		# Define controls
		self.lstMain = xbmcgui.ControlList(50, 110, 320, 450, buttonTexture=HOMEDIR+"images/btn.png", buttonFocusTexture=HOMEDIR+"images/btnHili.png")
		self.lblTotal = xbmcgui.ControlLabel(340,526, 200,35, '', 'font10', '0xFFFFFF00', alignment=1)
		self.lblTitle = xbmcgui.ControlLabel(400, 65, 400, 35, '', 'special13', '0xFFFFFF00')
		self.txtDesc = xbmcgui.ControlTextBox(400, 330, 290, 300, 'font101', '0xFFFFCC88') # Out of screen on purpose - no 1/1 in textfield
		self.lblDebug = xbmcgui.ControlLabel(4, 560, 0, 0, '', 'font10', '0xFFFF8800')
		self.imgPreview = xbmcgui.ControlImage(400, 115, 256, 192, "")
		self.btnView = xbmcgui.ControlButton(400, 504, 80, 30, "Favorites")
		self.btnInit = xbmcgui.ControlButton(496, 504, 80, 30, "Reload")
		self.btnHelp = xbmcgui.ControlButton(592, 504, 80, 30, "Help")

		# Add controls
		self.addControl(self.lstMain)
		self.addControl(self.lblTotal)
		self.addControl(self.lblTitle)
		self.addControl(self.txtDesc)
		self.addControl(self.imgPreview)
		self.addControl(self.lblDebug)

		# Add button controls
		self.addControl(self.btnView)
		self.addControl(self.btnInit)
		self.addControl(self.btnHelp)

		# Link control navigation
		self.lstMain.controlLeft(self.btnHelp)
		self.lstMain.controlRight(self.btnView)
		self.btnView.controlLeft(self.lstMain)
		self.btnView.controlRight(self.btnInit)
		self.btnInit.controlLeft(self.btnView)
		self.btnInit.controlRight(self.btnHelp)
		self.btnHelp.controlLeft(self.btnInit)
		self.btnHelp.controlRight(self.lstMain)

		self.setFocus(self.lstMain)

		self.getConfig(HOMEDIR+INIFILE)
		if not self.selRom < 0:
			self.listRoms(self.selEmu)
		else:
			self.listEmulators(self.selEmu)



	def getConfig(self, fileName):

		# Read self.emulators.ini
		fh=open(fileName,"r")
		data = fh.read()
		fh.close()

		self.note("Parsing "+fileName+"...")
		data = re.compile("^\[(.+?)]([^[]+)", re.S|re.M).findall(data)
		if data == []:
			# Oh shit.
			popup("Error","No emulators configured.\nEdit emulators.ini.")
			return

		self.emulators = [{} for row in range(len(data))]

		key = 0
		for items in data:
			emulator = re.compile("^([^\s\=]+)\=([^\=]+?)[\s\n\r]*$", re.S|re.M).findall(items[1])
			if emulator == []:
				# Oh shit.
				#popup("Error","Emulator with index "+key+" contains errors. Fix emulators.ini.")
				popup("Error","Emulator '"+items[0]+"' contains errors. Fix emulators.ini.")
				return
			self.emulators[key]['emulator'] = items[0]
			self.note("Parsing "+fileName+" - "+items[0])
			# Defaults:
			self.emulators[key]['noescape'] = False
			self.emulators[key]['solo'] = True
			self.emulators[key]['diskprefix'] = '_Disk'
			for item in emulator:
				if   item[0] == "title":		self.emulators[key]['title'] = item[1]
				elif item[0] == "desc":			self.emulators[key]['desc'] = item[1]
				elif item[0] == "romdir":		self.emulators[key]['romdir'] = item[1]
				elif item[0] == "romext":		self.emulators[key]['romext'] = item[1]
				elif item[0] == "app":			self.emulators[key]['app'] = item[1]
				elif item[0] == "solo":			self.emulators[key]['solo'] = item[1]
				elif item[0] == "noescape":		self.emulators[key]['noescape'] = True
				elif item[0] == "diskprefix":	self.emulators[key]['diskprefix'] = item[1]
			key+= 1
		self.note("Parsing "+fileName+"... done.")

		# Read indices
		config = HOMEDIR+'ab.cfg'
		if os.path.isfile(config):
			fh = open(config,'r')
			data = fh.read()
			fh.close()
		
			config = re.compile("^([^\s\=]+)\=([^\=]+?)[\s\n\r]*$", re.S|re.M).findall(data)
			
			for val in config:
				try:
					if   val[0] == 'selEmu':	self.selEmu = int(val[1])
					elif val[0] == 'selRom':	self.selRom = int(val[1])
				except: pass
		#return



	def listEmulators(self, index):
		self.currMenu = MENU_EMULIST		# So event listener knows what state we are in
		self.numEmu = len(self.emulators)

		# Fill list
		self.lstMain.reset()
		for emulator in self.emulators:
			self.lstMain.addItem(xbmcgui.ListItem(emulator['title'], emulator['emulator'], "", ""))

		self.lstMain.selectItem(index)		# Why does this only work occasionally?
		#self.lstMain.selectItem(self.selEmu)
		self.setEmuDesc()
		self.setFocus(self.lstMain)



	def setEmuDesc(self):
		emu = self.emulators[self.selEmu]
		self.setDesc(emu['title'],emu['desc'],HOMEDIR+'images/consoles/'+emu['emulator']+'.png')



	def listRoms(self, index):
		self.busy = True
		strNote = "Listing ROMs for emulator '"+self.emulators[index]['emulator']+"'"
		self.note(strNote+"...")

		# Reset state
		self.currMenu = MENU_ROMLIST
		self.lstMain.reset()

		# Default description
		self.setEmuDesc()

		# Private globals
		emu = self.emulators[index]
		filenum = int(0)

		# Get ROM list
		try:
			roms = self.readXml(HOMEDIR+emu['emulator']+'.xml')
			roms = roms.getElementsByTagName('rom')

			# reset data
			self.romDesc = {}
			self.romWhite = {}
			self.romBlack = {}

			for rom in roms:
				if self.abort == True: # Dammit, also not working
					self.abort = False
					self.busy = False
					#quit()		# All not working because action does not fire until loading is complete.
					#break
					#return
				filenum += 1
				#romName = rom.getAttribute('filename')
				romName = rom.getAttribute('game')
				self.romDesc[romName] = roms[filenum-1].firstChild
				self.lstMain.addItem(xbmcgui.ListItem(romName, str(filenum), "", ""))
				# These redraws make onAction lag very badly, don't know if the cause was old XBMC or old hardware, I cannot test anymore due to new hardware. You can comment those 2 lines out.
				#self.note(strNote+"... "+self.getProgress()) # clutters the debug window, disable print in self.note
				self.lblTotal.setLabel(str(filenum) + " ROMs")

				# Select last selected ROM during file load (is faster)
				#if self.selRom == filenum:
				#	self.lstMain.selectItem(filenum)	# Does not seem to work in for loop :(
			if filenum == int(0):
				# No roms for this emulator
				self.lblTitle.setLabel("No ROMs found.")
				self.popup("Error","There are no valid ROMs \nfor this emulator.")
				self.listEmulators(index)
		except:
			# ROM path not found
			self.busy = False
			self.lblTitle.setLabel("No ROMs found.")
			self.lblTotal.setLabel("")
			if self.popYesNo("Error","No valid ROM cache found. Would you like to \nscan now?"):
				self.buildRomList(index)
				self.listRoms(index)
			else:
				self.listEmulators(index)

		# Make list met beschrijving en plaatjes

		# Select last selected ROM (very handy, but might be annoying on big lists (1500+)
		self.lstMain.selectItem(self.selRom) # If only this worked in the above list filling loop..

		# Update labels
		self.lblTitle.setLabel(self.lstMain.getSelectedItem().getLabel())
		self.lblTotal.setLabel(str(filenum) + " ROMs")
		self.note(strNote+"... Done.")
		self.busy = False



	def setDesc(self, title, desc, image):
		self.lblTitle.setLabel(title)
		self.txtDesc.setText(desc)
		self.imgPreview.setImage(image)
		self.lblTotal.setLabel(str(self.numEmu) + " Items")
		return



	#
	# Interaction block
	#



	# OnScreen choose/control
	#

	def onControl(self, control):
		if control == self.btnInit:
			self.doInit(True)
		elif control == self.btnHelp:
			self.doHelp()
		elif control == self.lstMain:	# Crashes on old XBMC (2008-05)
			if self.currMenu == MENU_EMULIST:
				try:
					self.listRoms(self.selEmu)
				except: pass
				return
			elif self.currMenu == MENU_ROMLIST:
				self.bootRom()
				return
		return



	# Remote control (or keyb/mouse/joy)
	#

	def onAction(self, action):
		try:
		    if action == ACTION_PREVIOUS_MENU or action == ACTION_PARENT_DIR:	# Back
				if self.currMenu == MENU_EMULIST:
					self.selRom = int(-1)
					self.saveState()
					self.close()
				else:
					if self.busy == True:	# Not working
						self.abort = True
					else:
						self.listEmulators(self.selEmu)
					return
		    if self.currMenu == MENU_ROMLIST:
				try:
					if self.getFocus() == self.lstMain:	# Main ROM list
						if action == ACTION_MOVE_UP or action == ACTION_MOVE_DOWN \
						or action == ACTION_PAGE_UP or action == ACTION_PAGE_DOWN:	# Navigation
							self.selRom = -1		# Lose the selection
						# Update info for selection- update anyway, I don't know if the above IF restricts mouse events
						self.selRom = self.lstMain.getSelectedPosition()
						self.lblTitle.setLabel(self.lstMain.getSelectedItem().getLabel())
						self.txtDesc.setText(self.romDesc[self.lstMain.getSelectedItem().getLabel()])
				except: pass
		    elif self.currMenu == MENU_EMULIST:
				try:
					if self.getFocus() == self.lstMain: # Emu list
						if action == ACTION_SHOW_GUI:
							self.doInit(False)
							return
						# Update info
						self.selEmu = self.lstMain.getSelectedPosition()
						self.setEmuDesc()
					return
				except: pass
		except: return
		return



	def bootRom(self):
		# Prepare command
		emu = self.emulators[self.selEmu]
		
		myXml = HOMEDIR+emu['emulator']+'.xml'		
		if os.path.isfile(myXml):
			xmlDoc = self.readXml(myXml)
		
		game = self.lstMain.getSelectedItem().getLabel()
		
		# no builtin support for xpath in python? libxml2, lxml or etree must be installed separately.
		#xp = '/ArcadeBrowser/emulators/' +emu['emulator'] +'/romlist/rom[@game=\'' +game +'\']'		
		#nodes = xpath.Evaluate(xp, xmlDoc.documentElement)
		
		filenames = []
							
		roms = xmlDoc.getElementsByTagName('rom')		
		for rom in roms:			
			if rom.getAttribute('game') == self.lstMain.getSelectedItem().getLabel():
				filename = rom.getAttribute('filename')
				filenames.append(filename)
				subroms = rom.getElementsByTagName('subrom')
				for subrom in subroms:					
					filename = subrom.getAttribute('filename')
					filenames.append(filename)
				#TODO break												
		
		
		cmd = emu['app']
		fileindex = int(0)

		for fname in filenames:
			obIndex = cmd.find('{')
			cbIndex = cmd.find('}')			
			if obIndex > -1 and cbIndex > 1:
				replString = cmd[obIndex+1:cbIndex]
			cmd = cmd.replace("{", "")
			cmd = cmd.replace("}", "")			
			if fileindex == 0:
				if (emu['noescape'] == True):
					#self.note("noescape")
					cmd = cmd.replace('%ROMPATH%', emu['romdir'])
					cmd = cmd.replace('%ROM%', fname)
				else:
					#self.note("DO escape")
					cmd = cmd.replace('%ROMPATH%', re.escape(emu['romdir']))
					cmd = cmd.replace('%ROM%', re.escape(fname))
				cmd = cmd.replace('%I%', str(fileindex))
			else:
				if (emu['noescape'] == True):
					#self.note("noescape")
					newrepl = replString
					newrepl = newrepl.replace('%ROMPATH%', emu['romdir'])
					newrepl = newrepl.replace('%ROM%', fname)
				else:
					#self.note("DO escape")
					newrepl = newrepl.replace('%ROMPATH%', re.escape(emu['romdir']))
					newrepl = newrepl.replace('%ROM%', re.escape(fname))
				newrepl = newrepl.replace('%I%', str(fileindex))
				cmd += ' ' +newrepl
				#self.note(fname +str(fileindex))
			
			fileindex += 1
			#self.note(fname)				
		
		# OR something like this:
		#params = {'app' : emu[app], 'path': romdir, 'rom': filename}
		#cmd = '%(app)s %(path)s/%(rom)s' % params

		self.txtDesc.setText('Launching '+game+' ...')
		#self.txtDesc.setText('Launching '+cmd+' ...') # debug		

		#self.note("Launch " +emu['solo'])
		# Solo mode for heavy emulators kills XBMC. We need autoexec.py to restart (XBMC with) Arcade Brower afterwards.
		if (emu['solo'] == 'true'):
			# Backup original autoexec.py
			autoexec = SCRIPTUSR+'/autoexec.py'
			self.doBackup(autoexec)

			# Write new autoexec.py
			fh = open(autoexec,'w') # truncate to 0
			fh.write("import xbmc\n")
			fh.write("xbmc.executescript('"+HOMEDIR+"default.py')\n")
			fh.close()

			# Remember selection
			self.saveState()
			
			cmd = re.escape(HOMEDIR)+'applaunch.sh '+cmd
		
		# Write DEBUG FILE
		try:
			debug = True # comment out
			if debug == True:
				fh = open(HOMEDIR+'debug.txt','w')
				fh.write(cmd)
				fh.close()
		except: pass

		# Fire command
		os.system(cmd)



	def doHelp(self):
		self.popup('Note', "Yeah..\nI used to explain here how to work aroundthe bugs in \nxbmc that caused a crash, but they are all fixed. :D\nExplicit help available online, maybe.")



	def doInit(self,all):
		if (all == True):
			if self.popYesNo('Rebuild ROM list', 'This will try to rebuild the list of ROMs from *ALL* \nemulators specified in emulators.ini. \nHave you manually edited that file to be correct? \n(All data will be lost if ROMs are offline!)'):
				for n in range(0, self.numEmu-1):
					self.buildRomList(n)
				return
		if self.popYesNo('Rebuild ROM list', 'Do you want to rebuild the ROMlist for '+self.emulators[self.selEmu]['emulator']+'?\n(Data might get lost if ROMs are offline.)\n\n(Yellow button (GUI) brings up this dialog.)'):
			self.buildRomList(self.selEmu)



	def buildRomList(self, index):
		strNote = 'Building ROMlist'
		self.note(strNote+"... ")

		# Vars
		myEmu = self.emulators[index]
		myXml = HOMEDIR+myEmu['emulator']+'.xml'
		romNodeList = False
		xAdded = int(0)
		xRemoved = int(0)
		xUnchanged = int(0)

		# Check for existing xml
		if os.path.isfile(myXml):
			xmlDoc = self.readXml(myXml)

			# Verify existing xml
			try:
				if xmlDoc.childNodes[0].nodeName == 'ArcadeBrowser' and \
				xmlDoc.childNodes[0].childNodes[0].nodeName == 'emulators' and \
				xmlDoc.childNodes[0].childNodes[0].childNodes[0].nodeName == myEmu['emulator'] and \
				xmlDoc.childNodes[0].childNodes[0].childNodes[0].childNodes[1].nodeName == 'romlist':
					romNodeList = xmlDoc.childNodes[0].childNodes[0].childNodes[0].childNodes[1].childNodes
					self.note('Using '+myEmu['emulator']+'.xml as reference.')
				else:
					raise IndexError
				del xmlDoc
			except:
				if not self.popYesNo('Destroy ROM list', 'Your previous list of ROMs if corrupted. \nThe file will be destroyed. (backup in script folder.) \nDo you want to continue?'):
					return False
				else:
					self.note('WARNING! - '+myEmu['emulator']+'.xml corrupted.')
		
		# read ROMs from disk
		if os.path.isdir(myEmu['romdir']):
			files = os.listdir(myEmu['romdir'])
			files.sort()
		else:
			files = []

		# Create ROM array
		myRoms = []
		myDesc = {}
		if not romNodeList == False:
			nodeNo = int(-1)
			for node in romNodeList:
				self.note(strNote+"... "+self.getProgress())
				nodeNo += 1
				if node.tagName == 'rom':
					fileName = node.getAttribute('filename')
					if fileName in (f for f in files):
						if fileName not in myRoms:
							myRoms.append(fileName)
							myDesc[fileName] = node.childNodes[0].firstChild.nodeValue
							xUnchanged+=1
						files.remove(node.getAttribute('filename'))
					else:
						#romNodeList[nodeNo].unlink();
						xRemoved+=1
			del romNodeList

		# Insert remaining (new) files
		for f in files:
			self.note(strNote+"... "+self.getProgress())
			if f.lower().endswith(myEmu['romext']) and f not in myRoms:
				myRoms.append(f)
				xAdded += 1
		myRoms.sort()

		

		# Create the minidom xDocument
		xDoc = Document()

		# Create the <xRoot> base element
		xRoot = xDoc.createElement("ArcadeBrowser")
		xRoot.setAttribute("version", VERSION)
		xDoc.appendChild(xRoot)
		xEmus = xDoc.createElement("emulators")
		xRoot.appendChild(xEmus)

		# Add emu data
		xEmu = xDoc.createElement(myEmu['emulator'])
		xEmu.setAttribute('title', myEmu['title'])
		xEmu.setAttribute('rompath', myEmu['romdir'])
		x = xDoc.createElement('description')
		x.appendChild(xDoc.createTextNode(myEmu['desc']))
		xEmu.appendChild(x)

		# Create new list
		xRoms = xDoc.createElement('romlist')

		romnum = int(0)

		# Insert ROMs in xml
		for rom in myRoms:
			
			subrom = False
			
			#build friendly romname
			romname = rom	
			dpIndex = rom.lower().find(myEmu['diskprefix'].lower())
			if dpIndex > -1:
				romname = rom[0:dpIndex]
			else:
				dpIndex = rom.lower().find('.' +myEmu['romext'].lower())
				if dpIndex > -1:
					romname = rom[0:dpIndex]

			if xRoms.hasChildNodes():				
				if xRoms.lastChild.attributes['game'].nodeValue == romname:
					xRom = xDoc.createElement('subrom')
					xRom.setAttribute('filename', rom)
					xRom.setAttribute('game', romname)
					xRoms.lastChild.appendChild(xRom)
					subrom = True						

			self.note(strNote+"... "+self.getProgress())		
			if not subrom:
				xRom = xDoc.createElement('rom')
				xRom.setAttribute('filename', rom)
				xRom.setAttribute('game', romname)
				#xRom.setAttribute('favorite', 'false')
				#xRom.setAttribute('blacklist', 'false')
				#SELFNOTE: Blacklist in easy one-per-line textfile. Human readable = easy to delete them manually.
				xRomDesc = xDoc.createElement('description')
				if rom in myDesc:
					desc = str(myDesc[rom])
				else:
					desc = 'No Description.'
				xRomDesc.appendChild(xDoc.createTextNode(desc))
				xRom.appendChild(xRomDesc)
				xRoms.appendChild(xRom)				

		xEmu.appendChild(xRoms)
		xEmus.appendChild(xEmu)

		# Write new romlist.xml
		self.doBackup(myXml)
		fh = open(myXml,'w') # truncate to 0
		fh.write(xDoc.toprettyxml(indent="	"))
		fh.close()

		self.note(strNote+"...  done.")
		self.note(str(xAdded)+" added, "+str(xRemoved)+" removed and "+str(xUnchanged)+" unchanged.")

		return
		
	def readXml(self, file):
		fh=open(file,"r")
		xmlDoc = fh.read()
		fh.close()
		#Strip tidyness
		xmlDoc = re.sub(r"[\t\n\r]",r"",xmlDoc)
		xmlDoc = xmlDoc.strip()
		xmlDoc = parseString(xmlDoc)
		return xmlDoc

	def saveState(self):
		try:
			fh = open(HOMEDIR+'ab.cfg','w')
			fh.write("[Arcade Browser Configuration]\n")
			fh.write("selEmu="+str(self.selEmu)+"\n")
			fh.write("selRom="+str(self.selRom)+"\n")
			fh.close()
		except: pass



	def popup(self,title,msg):  
		dialog = xbmcgui.Dialog()
		dialog.ok(title,msg)
		del dialog
		return



	def popYesNo(self,title,msg):
		dialog = xbmcgui.Dialog()
		return dialog.yesno(title, msg)



	# Debugging purposes
	def note(self,msg):
		self.lblDebug.setLabel(str(msg))
		print "Arcade Browser: "+msg
		return



	def doBackup(self,fName):
		if os.path.isfile(fName):
			for n in range(1, 999):
				if not os.path.isfile(fName+'.bak'+str(n)):
					os.rename(fName, fName+'.bak'+str(n))
					break



	def getProgress(self):
		self.prog += 1
		if self.prog >= 4:
			self.prog = 0;
		if self.prog == 0: return '|'
		elif self.prog == 1: return '/'
		elif self.prog == 2: return '-'
		else: return '\\'



# Selfnote: Script will not load if there are no write permissions on SCRIPTUSR
# Remove AB restart script
if os.path.isfile(SCRIPTUSR+'/autoexec.py'):
	os.remove(SCRIPTUSR+'/autoexec.py')

AB = ArcadeBrowser()
AB.doModal()
del AB
