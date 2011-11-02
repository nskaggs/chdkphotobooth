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
import re
import gtk
import gtk.glade
import sys

from com.googlecode.chdkphotobooth import FileHandler, ProcessPhotos, \
    ProcessMovies
from ConfigParser import SafeConfigParser
import gobject
    
# configuration
DATABASE = '/tmp/photobooth.db'
TITLE = 'Photo Booth'
EVENT = 'Halloween 2011'
EVENT_SPACE = '/tmp/eventspace/halloween'
WIDTH = 600
HEIGHT = 750
HOW_TO_FILE = '/opt/photobooth-files/welcome.txt'
TERMS_CONDITIONS = '/opt/photobooth-files/toc.txt'
COUNTDOWN_TIME = 2 #time in seconds
BUILDER = gtk.Builder()

class PhotoBooth(gtk.Window):
    def __init__(self):
        super(PhotoBooth, self).__init__()
        
        
        #Read the application configuration.
        self.readConfig()
        
        # checks to  see if event space has been created, if not, then create one.
        if os.access(EVENT_SPACE, os.F_OK):
            print 'Path ' + EVENT_SPACE + ' already exists'
        else :
            print 'Path ' + EVENT_SPACE + ' does not exists, creating dir...'
            os.makedirs(EVENT_SPACE)
        
        self.fh = FileHandler.FileHandler(self)
        self.pp = ProcessPhotos.ProcessPhotos(self, self.fh)
        self.pm = ProcessMovies.ProcessMovies(self, self.fh)
        
        BUILDER.add_from_file("photobooth_ui.glade")
        BUILDER.connect_signals(self)
        
        # Get all the elements initalized
        self.startPhotoboothBtn = BUILDER.get_object("startPhotoboothBtn")
        self.lblValidationMessage = BUILDER.get_object("lblValidationMessage")
        self.emailFld = BUILDER.get_object("emailFld")
        self.fullnameFld = BUILDER.get_object("fullnameFld")
        self.tos = BUILDER.get_object("acceptTermsChk")
        self.progressBar = BUILDER.get_object("progressBar")
        self.progressBar.set_text("You have " + str(COUNTDOWN_TIME) + " seconds before the camera starts clicking...")
        self.timerLbl = BUILDER.get_object("timerLbl")
        self.statusBar = BUILDER.get_object("statusbar")        

        # self.initGUI(pp, pm, fh)
        # self.show_all() 
        # self.initCamera()
        self.resetDisplay()
                
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
        
        
    def onStartClicked(self, widget):
        self.countdownTimer()

    def validateFieldsAndEnableStart(self, widget):
        '''
            Validate all the fields to check if the data has been provided by the user.
        '''
#        if (self.validateFullName() & self.validateEmail() & self.tos.get_active()):
        if (self.validateEmail()):
            self.startPhotoboothBtn.set_sensitive(True)
            self.lblValidationMessage.set_markup("")
        else :
            self.startPhotoboothBtn.set_sensitive(False)
            self.lblValidationMessage.set_markup("<span size=\"large\" color=\"red\">Please enter valid data to proceed</span>")
        
    def validateFullName(self):
        self.fullname = self.fullnameFld.get_text()
        size = len(self.fullname.strip())
        if (size > 6): 
            return True
        else: 
            return False
    
    def validateEmail(self):
        self.email = self.emailFld.get_text()
        size = len(self.email.strip())
        if (size > 6): 
            qtext = '[^\\x0d\\x22\\x5c\\x80-\\xff]'
            dtext = '[^\\x0d\\x5b-\\x5d\\x80-\\xff]'
            atom = '[^\\x00-\\x20\\x22\\x28\\x29\\x2c\\x2e\\x3a-\\x3c\\x3e\\x40\\x5b-\\x5d\\x7f-\\xff]+'
            quoted_pair = '\\x5c[\\x00-\\x7f]'
            domain_literal = "\\x5b(?:%s|%s)*\\x5d" % (dtext, quoted_pair)
            quoted_string = "\\x22(?:%s|%s)*\\x22" % (qtext, quoted_pair)
            domain_ref = atom
            sub_domain = "(?:%s|%s)" % (domain_ref, domain_literal)
            word = "(?:%s|%s)" % (atom, quoted_string)
            domain = "%s(?:\\x2e%s)*" % (sub_domain, sub_domain)
            local_part = "%s(?:\\x2e%s)*" % (word, word)
            addr_spec = "%s\\x40%s" % (local_part, domain)
            
            
            email_address = re.compile('\A%s\Z' % addr_spec)  
            if email_address.match(self.email):
                return True
            else:
                return False
        else: 
            return False

    def countdownTimer(self):
        self.counter = COUNTDOWN_TIME
        fraction = 1.0 / COUNTDOWN_TIME
        while self.counter >= 0:
            gobject.timeout_add(1000 * self.counter, self.updateCountdownLbl, COUNTDOWN_TIME - self.counter, fraction)
            self.counter -= 1

    def updateCountdownLbl(self, counter, fraction):
        if (counter > 0 and counter > 9):
            self.timerLbl.set_text("00:" + str(counter))
            self.progressBar.set_fraction(self.progressBar.get_fraction() + fraction)
        elif (counter > 0 and counter < 10): 
            self.timerLbl.set_text("00:0" + str(counter))
            self.progressBar.set_fraction(self.progressBar.get_fraction() + fraction)
        else :
            self.timerLbl.set_text("Session in progress...")
            self.progressBar.set_fraction(self.progressBar.get_fraction() + fraction)
            # Time to trigger the camera!
            self.initCamera()
            self.pp.onPicClick(self)
            self.resetDisplay()
                
    def connectionCheck(self, child):
        #TODO: put max interations on this
        print 'connecting camera'
        self.statusBar.push(0, "Initializing Camera...")
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
        self.statusBar.push(0, "Resetting from older session...")
        print 'quitting old session'
        child.expect(pexpect.EOF)

    def initCamera(self):
        self.quitSession()
        child = self.reconnectCamera()
        self.statusBar.push(0, "Checking Lens...")
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
#        child.sendline('lua post_levent_to_ui("PressDispButton");post_levent_to_ui("UnpressDispButton");post_levent_to_ui("PressDispButton");post_levent_to_ui("UnpressDispButton");')
        child.expect('<conn>')
        #wait for operations to complete
        #time.sleep(5)
        #print 'display off'
        self.statusBar.push(0, "Connection Successful...")
        return child

    def getEmail(self):
#        email = self.email.get_text()
#        delchars = ''.join(c for c in map(chr, range(256)) if not c.isalpha())
#        email = email.translate(None, delchars)
        return self.email

    def onInputEnter(self, widget):
        self.resetDisplay()

    def resetDisplay(self):
        print 'reset display'
        self.startPhotoboothBtn.set_sensitive(False)
        self.lblValidationMessage.set_text("")
        self.fullnameFld.set_text("")
        self.emailFld.set_text("")
        self.tos.set_active(False)
        self.progressBar.set_fraction(0.0)
        self.timerLbl.set_text("Ready...")
        self.statusBar.push(0, "Ready for next person in line")
        os.chdir(self.EVENT_SPACE)        

PhotoBooth()
gtk.main()
