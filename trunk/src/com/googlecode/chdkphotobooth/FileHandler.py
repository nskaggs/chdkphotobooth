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
import gtk
import os
import shutil
import time

class FileHandler(object):
    '''
    This class is responsible for all the file handling of dumping files from the camera to local directory, renaming and moving the files to respective locations. This method does not care of the main process.
    '''


    def __init__(self, mainFrame):
        '''
        Constructor
        '''
        super(FileHandler, self).__init__()
        self.parentFrame = mainFrame

    def dumpCameraFiles(self):
        print 'dumping files'
        self.status.set_label('Grabbing Files from Camera')
        while gtk.events_pending():
            gtk.main_iteration()
        #get files and then delete all files
        os.chdir(self.eventSpaceTmp)
        os.system('gphoto2 -P --force-overwrite')
        os.system('gphoto2 -DR')

    def renameMoveFiles(self):
        print 'renaming and moving files'
        #rename all files to user email + filename, and move to email + timestamp dir
        #make dir
        email = self.getEmail()
        newDestinationDir = "/opt/eventspace" + "/" + email + " - " + time.strftime("%Y%m%d%H%M%S", time.localtime())
        os.mkdir(email + time.strftime("%Y%m%d%H%M%S", time.localtime()))

        #do JPGS
        self.renamer("*.JPG", r"^(.*)\.JPG$", email + r" \1.JPG")
        for jpg in self.filterbyext(os.listdir(self.eventSpaceTmp), 'JPG'):
            shutil.move(jpg, newDestinationDir)

        #do AVIS
        self.renamer("*.AVI", r"^(.*)\.AVI$", email + r" \1.AVI")
        for avi in self.filterbyext(os.listdir(self.eventSpaceTmp), 'AVI'):
            shutil.move(avi, newDestinationDir)

    def createFavor(self):
        print 'create favor'
        self.status.set_label('Creating PhotoBoothStrip Preview')
        while gtk.events_pending():
            gtk.main_iteration()
        num = 0
        for jpg in self.filterbyext(os.listdir(os.getcwd()), 'JPG'):
            num += 1
            os.system('convert -scale 592x444 -rotate 90 ' + jpg + ' temp' + str(num) + '.jpg')
        os.system("convert PhotoBoothStrip_6.jpg -draw \"image over 8,4 444,592 'temp1.jpg'\" -draw \"image over 8,602  444,592  'temp2.jpg'\" -draw \"image over 8,1201 444,592 'temp3.jpg'\" -draw \"image over 747,4 444,592 'temp4.jpg'\" -draw \"image over 747,602 444,592 'temp5.jpg'\" -draw \"image over 747,1201 444,592 'temp6.jpg'\" print.jpg")
        
