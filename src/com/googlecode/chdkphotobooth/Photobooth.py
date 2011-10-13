'''
#This file is part of CHDKPhotobooth.
#CHDKPhotobooth is free software: you can redistribute it and/or modify it under the terms of
#the GNU General Public License as published by the Free Software Foundation, either version 3
#of the License, or (at your option) any later version.
#CHDKPhotobooth is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
#without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
#See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with CHDKPhotobooth.
#If not, see http://www.gnu.org/licenses/

This class is responsible for the UI and the build up

Created on Sep 15, 2011

@author: varun
'''
#!/usr/local/bin/python

import pexpect
import os
import time
import gtk
import re
import glob

from com.googlecode.chdkphotobooth import FileHandler, ProcessPhotos, \
    ProcessMovies
from ConfigParser import SafeConfigParser
from datetime import date
    
# configuration
DATABASE = '/tmp/photobooth.db'
TITLE = 'Photo Booth'
EVENT = 'Halloween 2011'
EVENT_SPACE = '/tmp/eventspace/halloween'
WIDTH = 600
HEIGHT = 700
DISPLAY_TEXT = '/opt/photobooth-files/welcome.txt'
TERMS_CONDITIONS = '/opt/photobooth-files/toc.txt'

class PhotoBooth(gtk.Window):
    def __init__(self):
        super(PhotoBooth, self).__init__()
        
        #Read the application configuration.
        self.readConfig()
        
        # checks to see if event space has been created, if not, then create one.
        if os.access(EVENT_SPACE, os.F_OK):
            print 'Path ' + EVENT_SPACE + ' already exists'
        else :
            print 'Path ' + EVENT_SPACE + ' does not exists, creating dir...'
            os.mkdir(EVENT_SPACE)
        
        pp = ProcessPhotos.ProcessPhotos(self)
        pm = ProcessMovies.ProcessMovies(self)
        fh = FileHandler.FileHandler(self)

        self.initGUI(pp, pm, fh)
        self.show_all()
#        self.initCamera()
        self.resetDisplay()
        
    def initGUI(self, pp, pm, fh):
                        
        self.set_title(TITLE + " - " + EVENT)
        self.set_size_request(WIDTH, HEIGHT)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", gtk.main_quit)

#        fixed = gtk.Fixed()
        mainVBox = gtk.VBox(False, 10)
        mainVBox.pack_start(self.logoHeader())
        mainVBox.pack_end(self.formFrame())
                
        self.add(mainVBox)
        
        self.email = gtk.Entry(30)

        self.pic = gtk.Button("Take Pictures")
        self.movieStart = gtk.Button("Record Video")
        self.movieStop = gtk.Button("Stop Recording")
        self.moviePlay = gtk.Button("Play back Video")
        self.printbtn = gtk.Button("Print Images")
        self.progressbar = gtk.ProgressBar(adjustment=None)
        self.status = gtk.Label("Ready to start")

        self.image1 = gtk.Image()
        self.image1btn = gtk.Button()
        self.image1btn.add(self.image1)
        self.image2 = gtk.Image()
        self.image2btn = gtk.Button()
        self.image2btn.add(self.image2)
        self.image3 = gtk.Image()
        self.image3btn = gtk.Button()
        self.image3btn.add(self.image3)
        self.image4 = gtk.Image()
        self.image4btn = gtk.Button()
        self.image4btn.add(self.image4)
        self.imageStrip = gtk.Image()
        self.imageStripbtn = gtk.Button()
        self.imageStripbtn.add(self.imageStrip)
        
        self.pic.connect("clicked", pp.onPicClick)
#        self.printbtn.connect("clicked", self.onPrintClick)
#        self.movieStart.connect("clicked", pm.onMovieStartClick)
#        self.movieStop.connect("clicked", pm.onMovieStopClick)
#        self.moviePlay.connect("clicked", pm.onMoviePlayClick)
#        self.email.connect("key-press-event", self.onInputEnter)
        self.email.set_text("Photo booth User")
        
        self.pic.set_size_request(120, 30)
        self.movieStart.set_size_request(250, 30)
        self.movieStop.set_size_request(120, 30)
        self.moviePlay.set_size_request(120, 30)
        self.progressbar.set_size_request(200, 30)
        self.printbtn.set_size_request(240, 30)

        self.image1btn.set_size_request(120, 160)
        self.image2btn.set_size_request(120, 160)
        self.image3btn.set_size_request(120, 160)
        self.image4btn.set_size_request(120, 160)
        self.imageStrip.set_size_request(288, 432)

#        fixed.put(self.greeting, 10, 15)
#        fixed.put(self.email, 300, 10)
#        fixed.put(self.inputFrame, 10,10)
#        fixed.put(self.status, 500, 15)
#
#        fixed.put(self.pic, 10, 50)
#        fixed.put(self.progressbar, 10, 90)
#
#        fixed.put(self.movieStart, 700, 50)
#        fixed.put(self.movieStop, 700, 90)
#        fixed.put(self.moviePlay, 830, 90)
#
#        fixed.put(self.image1btn, 10, 150)
#        fixed.put(self.image2btn, 10, 350)
#        fixed.put(self.image3btn, 150, 150)
#        fixed.put(self.image4btn, 150, 350)
#        fixed.put(self.imageStripbtn, 300, 150)
#        fixed.put(self.printbtn, 20, 550)
        
#        return fixed

    def logoHeader(self):
        '''
        This function builds the logo for the widget.
        '''
        logoImage = gtk.Image()
        logoImage.set_padding(10, 10)
        logoImage.set_alignment(0.0, 0.0)
        logoImage.set_from_file("/opt/photobooth-files/logo.png")
        
        return logoImage
    
    def formFrame(self):
        '''
        The form frame had all the required text fields, which capture the user email address, and the acceptance of the terms and conditions.
        '''
        inputFrame = gtk.Frame()
        frameLbl = gtk.Label()
        frameLbl.set_padding(10, 10)
        frameLbl.set_markup("<span size=\"x-large\">Photo Booth - "  +  EVENT + "</span>")
        inputFrame.set_label_widget(frameLbl)
        inputFrame.set_size_request(600, 600)
        inputFrame.set_border_width(10)

        vBox = gtk.VBox(False, 5)
        
#        h1Box = gtk.HBox(True, 5)
#        lblClientName = gtk.Label("Name")
#        txtClientName = gtk.Entry(45)
#        h1Box.add(lblClientName)
#        h1Box.add(txtClientName)
#        vBox.add(h1Box)

        howToUse = gtk.TextView()
        howToUse.set_cursor_visible(False)
        howToUse.set_border_width(15)
        howToUse.set_wrap_mode(gtk.WRAP_WORD)
        howToBuffer = howToUse.get_buffer()
        howToBuffer.set_text(DISPLAY_TEXT)
        vBox.pack_start(howToUse)


        h2Box = gtk.HBox(True, 5)
        lblEmail = gtk.Label()
        lblEmail.set_alignment(0.2, 0.5)
        lblEmail.set_padding(10, 10)
        lblEmail.set_markup("<span size=\"large\">Email Address</span>")
        txtEmail = gtk.Entry(45)
        h2Box.add(lblEmail)
        h2Box.add(txtEmail)
        vBox.add(h2Box)

        
        h3Box = gtk.HBox(True, 5)
        radioBtn = gtk.RadioButton(None, "photo")
        h3Box.pack_start(radioBtn, True, True, 5)
        radioBtn = gtk.RadioButton(radioBtn, "video")
        h3Box.pack_start(radioBtn, True, True, 5)
        vBox.add(h3Box)

        btnContinue = gtk.Button("Start")
        vBox.add(btnContinue)

        #TODO: create embed video display?
        #TODO: create reset button?
        #TODO: ask for email to send to person later?

        inputFrame.add(vBox)
        
        return inputFrame        
        
    def readConfig(self):
        '''
        This function is responsible for reading the application configuration, some time in the future,
        we should be able to read and write this using a gtk_dialog box.
        '''
        parser = SafeConfigParser()
        parser.read('photobooth.ini')
                
        #[application_setting]
        self.TITLE = parser.get('application_setting', 'title')
        self.EVENT = parser.get('application_setting', 'event_name')
        self.EVENT_SPACE = parser.get('application_setting', 'event_space')
        self.WIDTH = parser.get('application_setting', 'width')
        self.HEIGHT = parser.get('application_setting', 'height')

        # [database setting]
        self.DATABASE = parser.get('database', 'location')
        
    def connectionCheck(self, child):
        #TODO: put max interations on this
        print 'connecting camera'
        self.status.set_label('connecting camera')
        child.sendline('r')
        i = child.expect (['<conn>', 'ERROR: Could not open session!', 'ERROR: Could not close session!', '<    >'])
        if i == 0:
            print 'camera connected'
            return 0
        else:
            return 1

    def reconnectCamera(self):
        child = pexpect.spawn('ptpcam --chdk', timeout=15)
        check = self.connectionCheck(child)
        while check == 1:
            check = self.connectionCheck(child)

        #do this twice :-)
        #check = self.connectionCheck(child)
        #while check == 1:
        #    check = self.connectionCheck(child)
        
        return child

    def quitSession(self):
        child = pexpect.spawn('ptpcam --chdk', timeout=15)
        check = self.connectionCheck(child)
        while check == 1:
            check = self.connectionCheck(child)
        child.sendline('quit')
        print 'quitting old session'
        child.expect(pexpect.EOF)

    def initCamera(self):
        self.quitSession()
        child = self.reconnectCamera()
        #open lens
        child.sendline('mode 1')
        #child.sendline('lua post_levent_to_ui("PressRecButton")')
        print 'opening lens'
        child.expect('<conn>')
        #wait for operations to complete
        time.sleep(5)
        print 'lens opened'
        #TODO:Turning off display seems to turn off camera
        #print 'turning off display'
        #turn off display
        child.sendline('lua post_levent_to_ui("PressDispButton");post_levent_to_ui("UnpressDispButton");post_levent_to_ui("PressDispButton");post_levent_to_ui("UnpressDispButton");')
        child.expect('<conn>')
        #wait for operations to complete
        #time.sleep(5)
        #print 'display off'
        return child

    def printImages(self):
        print 'printing images'
        self.status.set_label('Printing Images')
        while gtk.events_pending():
            gtk.main_iteration()
        os.system('lpr print.jpg')

    def getEmail(self):
        email = self.email.get_text()
        delchars = ''.join(c for c in map(chr, range(256)) if not c.isalpha())
        email = email.translate(None, delchars)
        return email

    def onInputEnter(self, widget):
        self.resetDisplay()

    def resetDisplay(self):
        print 'reset display'
        self.progressbar.set_fraction(0)
        self.email.set_text("enter email address...")
        self.image1.set_from_file("")
        self.image2.set_from_file("")
        self.image3.set_from_file("")
        self.image4.set_from_file("")
        self.imageStrip.set_from_file("PhotoBoothStrip_6.jpg")
        self.status.set_label('Ready to start')
        os.system('rm temp1.jpg temp2.jpg temp3.jpg temp4.jpg temp5.jpg temp6.jpg print.jpg temp.avi')

#utility functions

    def renamer(self, files, pattern, replacement):
        for pathname in glob.glob(files):
            basename = os.path.basename(pathname)
            new_filename = re.sub(pattern, replacement, basename)
            if new_filename != basename:
                os.rename(pathname, os.path.join(os.path.dirname(pathname), new_filename))

    def filterbyext(self, filelist, ext):
        returnfiles = []
        for item in filelist:
            x = item.split(".")
            try:
                if str(x[1]) == ext:
                    returnfiles.append(item)
            except IndexError:
                pass
        return returnfiles

PhotoBooth()
gtk.main()
