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
import time
import gtk

class ProcessPhotos(object):
    '''
    classdocs
    '''


    def __init__(self, main, fileHandler):
        '''
        Constructor
        '''
        self.main = main
        self.fileHandler = fileHandler
        
        
    def takePic(self, widget, child):
        child.sendline('lua post_levent_to_ui("ModeDialToAuto")')
        print 'switched mode to auto'
        #wait for mode switch
        time.sleep(3)
        print 'mode switched to auto'
        print 'snapping pics'
        self.main.statusBar.push(0, 'Taking Pictures')
        #take 4 pictures; hardcoded for speed
        child.sendline('lua shoot();shoot();')

#        #need to pause because camera execution is not accounted for
        for i in range(3):
#            widget.progressbar.set_fraction(i * .25 + .25)
            while gtk.events_pending():
                        gtk.main_iteration()
            time.sleep(5)

        child.expect('<conn>')
        child.sendline('quit')
        child.expect(pexpect.EOF)
        print 'pics snapped'        

        
    def displayImages(self):
        print 'displaying images'
        self.image1.set_from_file("temp1.jpg")
        self.image2.set_from_file("temp2.jpg")
#       self.image3.set_from_file("temp3.jpg")
#       self.image4.set_from_file("temp4.jpg")
#       self.image5.set_from_file("temp5.jpg")
#       self.image6.set_from_file("temp6.jpg")
        self.imageStrip.set_from_file("print.jpg")
        

    def onPicClick(self, widget):
        widget = self.main
        #widget.progressbar.set_fraction(.25)
#        widget.status.set_label('Starting')
        while gtk.events_pending():
            gtk.main_iteration()
        child = widget.reconnectCamera()
        self.takePic(widget, child)
        self.fileHandler.dumpCameraFiles()
        self.fileHandler.createOperativeFavor2()
#        self.fileHandler.renameMoveFiles()
#        self.displayImages()
        widget.statusBar.push(0, 'Done')
#        widget.progressbar.set_fraction(1)
        while gtk.events_pending():
            gtk.main_iteration()
            
        #self.resetDisplay()
        
    def onPrintClick(self, widget):
        self.printImages()        
