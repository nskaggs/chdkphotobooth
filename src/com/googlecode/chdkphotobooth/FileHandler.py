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
import time
import re
import glob
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders


GMAIL_USERNAME = "varun.mehta.r@gmail.com"
GMAIL_PASSWORD = "iq0zero7"

class FileHandler(object):
    '''
    This class is responsible for all the file handling of dumping files from the camera to local directory, renaming and moving the files to respective locations. This method does not care of the main process.
    '''


    def mail(self, to, subject, text, attach):
        msg = MIMEMultipart()
        
        msg['From'] = "Varun Mehta"
        msg['To'] = to
        msg['Subject'] = subject
        
        msg.attach(MIMEText(text))
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attach, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                'attachment; filename="%s"' % os.path.basename(attach))
        msg.attach(part)
        
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        mailServer.sendmail(GMAIL_USERNAME, to, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()

    def __init__(self, main):
        '''
        Constructor
        '''
        super(FileHandler, self).__init__()
        self.main = main

    def dumpCameraFiles(self):
        print 'dumping files'
        self.main.statusBar.push(0, 'Grabbing Files from Camera')
        self.finalFileName = self.main.getEmail() + "-" + time.strftime("%Y%m%d%H%M%S", time.localtime())
        email = self.main.getEmail()
        self.newDestinationDir = self.main.EVENT_SPACE + "/" + email + "/" + self.finalFileName
        os.makedirs(self.newDestinationDir)

        while gtk.events_pending():
            gtk.main_iteration()
        #get files and then delete all files
        os.chdir(self.newDestinationDir)
        os.system('gphoto2 -P --force-overwrite')
        os.system('gphoto2 -DR')

    def renameMoveFiles(self):
        print 'renaming and moving files'
        #rename all files to user email + filename, and move to email + timestamp dir
        #make dir
        email = self.main.getEmail()
        newDestinationDir = self.main.EVENT_SPACE + "/" + email + "/" + self.finalFileName
        os.mkdir(newDestinationDir)

        #do JPGS
#        self.renamer("*.JPG", r"^(.*)\.JPG$", email + r" \1.JPG")
#        for jpg in self.filterbyext(os.listdir(self.main.EVENT_SPACE), 'JPG'):
#            shutil.move(jpg, newDestinationDir)
#
#        #do AVIS
#        self.renamer("*.AVI", r"^(.*)\.AVI$", email + r" \1.AVI")
#        for avi in self.filterbyext(os.listdir(self.main.EVENT_SPACE), 'AVI'):
#            shutil.move(avi, newDestinationDir)

    def createFavor6(self):
        print 'create favor'
        self.main.statusBar.push(0, 'Creating PhotoBoothStrip Preview')
        while gtk.events_pending():
            gtk.main_iteration()
        num = 0
        for jpg in self.filterbyext(os.listdir(os.getcwd()), 'JPG'):
            num += 1
            os.system('convert -scale 592x444 -rotate 90 ' + jpg + ' ' + self.main.getEmail() + str(num) + '.jpg')
        os.system("convert /opt/photobooth-files/PhotoBoothStrip_6.jpg -draw \"image over 8,4 444,592 '" + self.main.getEmail() + "1.jpg'\" -draw \"image over 8,602  444,592  '" + self.main.getEmail() + "2.jpg'\" -draw \"image over 8,1201 444,592 '" + self.main.getEmail() + "3.jpg'\" -draw \"image over 747,4 444,592 '" + self.main.getEmail() + "4.jpg'\" -draw \"image over 747,602 444,592 '" + self.main.getEmail() + "5.jpg'\" -draw \"image over 747,1201 444,592 '" + self.main.getEmail() + "6.jpg'\" " + self.finalFileName + ".jpg")
    
    def createFavor4(self):
        print 'create favor'
        self.main.statusBar.push(0, 'Creating PhotoBoothStrip Preview ' + os.getcwd())
        while gtk.events_pending():
            gtk.main_iteration()
        num = 0
        for jpg in self.filterbyext(os.listdir(os.getcwd()), 'JPG'):
            num += 1
            os.system('convert -scale 729x546 -rotate 90 ' + jpg + ' ' + self.main.getEmail() + str(num) + '.jpg')
        os.system("convert /opt/photobooth-files/PhotoboothDiwali4.jpg -draw \"image over 8,8 546,729 '" + self.main.getEmail() + "1.jpg'\" -draw \"image over 8,772  546,729  '" + self.main.getEmail() + "2.jpg'\" -draw \"image over 646,8 546,729 '" + self.main.getEmail() + "3.jpg'\" -draw \"image over 646,772 546,729 '" + self.main.getEmail() + "4.jpg'\" " + self.finalFileName + ".jpg")
        time.sleep(2)
        self.printImages()

    def createFavor2(self):
        print 'create favor'
        self.main.statusBar.push(0, 'Creating PhotoBoothStrip Preview ' + os.getcwd())
        while gtk.events_pending():
            gtk.main_iteration()
        num = 0
        for jpg in self.filterbyext(os.listdir(os.getcwd()), 'JPG'):
            num += 1
            os.system('convert -scale 1114x835 -rotate 90 ' + jpg + ' ' + self.main.getEmail() + str(num) + '.jpg')
        os.system("convert /opt/photobooth-files/OperativeHalloweenTemplate.jpg -draw \"image over 0,0 835,1114 '" + self.main.getEmail() + "1.jpg'\" -draw \"image over 964,0  835,1114  '" + self.main.getEmail() + "2.jpg'\" " + self.finalFileName + ".jpg")
        time.sleep(2)
        self.printImages()

    def createOperativeFavor2(self):
        print 'create favor'
        self.main.statusBar.push(0, 'Creating PhotoBoothStrip Preview ' + os.getcwd())
        while gtk.events_pending():
            gtk.main_iteration()
        num = 0
        for jpg in self.filterbyext(os.listdir(os.getcwd()), 'JPG'):
            num += 1
            os.system('convert -scale 1088x817 ' + jpg + ' ' + self.main.getEmail() + str(num) + '.jpg')
        os.system("convert /opt/photobooth-files/OperativeHalloweenTemplateBlack.jpg -draw \"image over 19,16 1088,817 '" + self.main.getEmail() + "1.jpg'\" -draw \"image over 19,967  1088,817  '" + self.main.getEmail() + "2.jpg'\" " + self.finalFileName + ".jpg")
        time.sleep(2)
        self.printImages()


    def printImages(self):
        print 'printing images'
        self.main.statusBar.push(0, 'Printing Images')
        while gtk.events_pending():
            gtk.main_iteration()
        os.system("lpr " + self.finalFileName + ".jpg")
        os.system("cp " + self.finalFileName + ".jpg /opt/eventspace/operative.halloween")
        self.main.statusBar.push(0, 'Sending Email')
        self.mail(self.main.getEmail(), "Operative Halloween Party - Photobooth ", "Booo! Your Halloween Photo!", "/opt/eventspace/operative.halloween/" + self.finalFileName + ".jpg")

        
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
