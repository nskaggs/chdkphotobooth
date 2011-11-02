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

Created on Sep 15, 2011

@author: varun
'''
import pexpect
import os
import time
import gtk
import subprocess

class ProcessMovies(object):
    '''
    classdocs
    '''


    def __init__(self, main, fileHandler):
        '''
        Constructor
        '''
        super(ProcessMovies, self).__init__()
        self.main = main
        self.fileHandler = fileHandler
        

    def startVid(self, child):
        child.sendline('lua post_levent_to_ui("ModeDialToMovie")')
        print 'switched mode to movie'
        #wait for mode switch
        time.sleep(3)
        print 'mode switched to movie'
        child.expect('<conn>')
        child.sendline('lua press("shoot_half");press("shoot_full");release("shoot_full");release("shoot_half");')
        print 'starting movie'
        child.expect('<conn>')
        time.sleep(3)
        self.status.set_label('Recording Movie')
        while gtk.events_pending():
            gtk.main_iteration()

    def stopVid(self, child):
        child.sendline('lua press("shoot_half");press("shoot_full");release("shoot_full");release("shoot_half");')
        print 'ending movie'
        child.expect('<conn>')
        child.sendline('quit')
        #wait for exit
        time.sleep(2)
        self.status.set_label('Movie Stopped')
        while gtk.events_pending():
            gtk.main_iteration()
        print 'exiting movie mode'
        child.expect(pexpect.EOF)
        
    def createMovie(self):
        print 'create movie'
        self.status.set_label('Processing video')
        while gtk.events_pending():
            gtk.main_iteration()
        for avi in self.filterbyext(os.listdir(os.getcwd()), 'AVI'):
            os.system('cp ' + avi + ' temp.avi')
    
    def playMovie(self):
        self.status.set_label('Playing video')
        while gtk.events_pending():
            gtk.main_iteration()
        movie = 'temp.avi'
        p = subprocess.Popen(['mplayer', '-vf rotate 270 ' + movie])
        

    def onMovieStartClick(self, widget):
        self.status.set_label('Starting')
        while gtk.events_pending():
            gtk.main_iteration()
        child = self.reconnectCamera()
        self.startVid(child)

    def onMovieStopClick(self, widget):
        child = self.reconnectCamera()
        self.stopVid(child)
        self.dumpCameraFiles()
        self.createMovie()
        self.renameMoveFiles()
        self.status.set_label('Done')
        while gtk.events_pending():
            gtk.main_iteration()

    def onMoviePlayClick(self, widget):
        self.playMovie()        
