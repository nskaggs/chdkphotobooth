#!/usr/local/bin/python

import pexpect
import os
import time
import gtk
import re
import glob
import shutil
import subprocess

class PhotoBooth(gtk.Window):
    def __init__(self):
        super(PhotoBooth, self).__init__()
        
        self.set_title("Photobooth")
        self.set_size_request(1024, 768)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", gtk.main_quit)

        fixed = gtk.Fixed()

        #TODO: create embed video display?
        #TODO: create reset button?
        #TODO: ask for email to send to person later?
        
        self.greeting = gtk.Label("Input your name and then choose an activity")
        self.entry = gtk.Entry(30)
        self.pic = gtk.Button("Take Pictures")
        self.movieStart = gtk.Button("Record Video")
        self.movieStop = gtk.Button("Stop Recording")
        self.moviePlay = gtk.Button("Playback Video")
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
        
        self.pic.connect("clicked", self.onPicClick)
        self.printbtn.connect("clicked", self.onPrintClick)
        self.movieStart.connect("clicked", self.onMovieStartClick)
        self.movieStop.connect("clicked", self.onMovieStopClick)
        self.moviePlay.connect("clicked", self.onMoviePlayClick)
#        self.entry.connect("key-press-event", self.onInputEnter)
        self.entry.set_text("Wedding Guest")
        
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

        fixed.put(self.greeting, 10, 15)
        fixed.put(self.entry, 300, 10)
        fixed.put(self.status, 500, 15)

        fixed.put(self.pic, 10, 50)
        fixed.put(self.progressbar, 10, 90)

        fixed.put(self.movieStart, 700, 50)
        fixed.put(self.movieStop, 700, 90)
        fixed.put(self.moviePlay, 830, 90)

        fixed.put(self.image1btn, 10, 150)
        fixed.put(self.image2btn, 10, 350)
        fixed.put(self.image3btn, 150, 150)
        fixed.put(self.image4btn, 150, 350)
        fixed.put(self.imageStripbtn, 300, 150)
        fixed.put(self.printbtn, 20, 550)
        
        self.add(fixed)
        self.show_all()
        self.initCamera()
        self.resetDisplay()

    def connectionCheck(self, child):
        #TODO: put max interations on this
        print 'connecting camera'
        self.status.set_label('connecting camera')
        child.sendline('r')
        i = child.expect (['<conn>', 'ERROR: Could not open session!', 'ERROR: Could not close session!', '<    >'])
        if i==0:
            print 'camera connected'
            return 0
        else:
            return 1

    def reconnectCamera(self):
        child = pexpect.spawn('ptpcam --chdk',timeout=15)
        check = self.connectionCheck(child)
        while check == 1:
            check = self.connectionCheck(child)

        #do this twice :-)
        #check = self.connectionCheck(child)
        #while check == 1:
        #    check = self.connectionCheck(child)
        
        return child

    def quitSession(self):
        child = pexpect.spawn('ptpcam --chdk',timeout=15)
        check = self.connectionCheck(child)
        while check == 1:
            check = self.connectionCheck(child)
        child.sendline('quit')
        print 'quit old session'
        child.expect(pexpect.EOF)

    def initCamera(self):
        self.quitSession()
        child = self.reconnectCamera()
        #open lens
        child.sendline('lua post_levent_to_ui("PressRecButton")')
        print 'opening lens'
        child.expect('<conn>')
        #wait for operations to complete
        time.sleep(5)
        print 'lens opened'
        #TODO:Turning off display seems to turn off camera
        #print 'turning off display'
        #turn off display
        #child.sendline('lua post_levent_to_ui("PressDispButton");post_levent_to_ui("UnpressDispButton");post_levent_to_ui("PressDispButton");post_levent_to_ui("UnpressDispButton");')
        #child.expect('<conn>')
        #wait for operations to complete
        #time.sleep(5)
        #print 'display off'
        return child

    def takePic(self, child):
        child.sendline('lua post_levent_to_ui("ModeDialToAuto")')
        print 'switched mode to auto'
        #wait for mode switch
        time.sleep(3)
        print 'mode switched to auto'
        print 'snapping pics'
        self.status.set_label('Taking Pictures')
        #take 4 pictures; hardcoded for speed
        child.sendline('lua shoot();shoot();shoot();shoot();')

        #need to pause because camera execution is not accounted for
        for i in range(3):
            self.progressbar.set_fraction(i*.25+.25)
            while gtk.events_pending():
                        gtk.main_iteration()
            time.sleep(10)

        child.expect('<conn>')
        child.sendline('quit')
        child.expect(pexpect.EOF)
        print 'pics snapped'

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

    def dumpCameraFiles(self):
        print 'dumping files'
        self.status.set_label('Grabbing Files from Camera')
        while gtk.events_pending():
            gtk.main_iteration()
        #get files and then delete all files
        os.system('gphoto2 -P --force-overwrite')
        os.system('gphoto2 -DR')

    def renameMoveFiles(self):
        print 'renaming and moving files'
        #rename all files to user name + filename, and move to name + timestamp dir
        #make dir
        name = self.getName()
        newdest = os.getcwd() + "/" + name + time.strftime("%Y%m%d%H%M%S", time.localtime())
        os.mkdir(name + time.strftime("%Y%m%d%H%M%S", time.localtime()))

        #do JPGS
        self.renamer("*.JPG", r"^(.*)\.JPG$", name + r" \1.JPG")
        for jpg in self.filterbyext(os.listdir(os.getcwd()),'JPG'):
             shutil.move(jpg,newdest)

        #do AVIS
        self.renamer("*.AVI", r"^(.*)\.AVI$", name + r" \1.AVI")
        for avi in self.filterbyext(os.listdir(os.getcwd()),'AVI'):
             shutil.move(avi,newdest)

    def createFavor(self):
        print 'create favor'
        self.status.set_label('Creating PhotoBoothStrip Preview')
        while gtk.events_pending():
            gtk.main_iteration()
        num = 0
        for jpg in self.filterbyext(os.listdir(os.getcwd()),'JPG'):
            num += 1
            os.system('convert -scale 120x90 -rotate 90 ' + jpg + ' temp' + str(num) + '.jpg')
        os.system("convert PhotoBoothStrip.jpg -draw \"image over 19,55 90,120 'temp1.jpg'\" -draw \"image over 19,203  90,120  'temp2.jpg'\" -draw \"image over 152,55 90,120 'temp3.jpg'\" -draw \"image over 152,203 90,120 'temp4.jpg'\" print.jpg")

    def createMovie(self):
        print 'create movie'
        self.status.set_label('Processing video')
        while gtk.events_pending():
            gtk.main_iteration()
        for avi in self.filterbyext(os.listdir(os.getcwd()),'AVI'):
            os.system('cp ' + avi + ' temp.avi')
    
    def displayImages(self):
        print 'displaying images'
        self.image1.set_from_file("temp1.jpg")
        self.image2.set_from_file("temp2.jpg")
        self.image3.set_from_file("temp3.jpg")
        self.image4.set_from_file("temp4.jpg")
        self.imageStrip.set_from_file("print.jpg")

    def playMovie(self):
        self.status.set_label('Playing video')
        while gtk.events_pending():
            gtk.main_iteration()
        movie = 'temp.avi'
        p = subprocess.Popen(['mplayer',  '-vf rotate 270 ' + movie])

    def printImages(self):
        print 'printing images'
        self.status.set_label('Printing Images')
        while gtk.events_pending():
            gtk.main_iteration()
        os.system('lpr print.jpg')

    def getName(self):
        name = self.entry.get_text()
        delchars = ''.join(c for c in map(chr, range(256)) if not c.isalpha())
        name = name.translate(None, delchars)
        return name

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

    def onPicClick(self, widget):
        self.progressbar.set_fraction(.25)
        self.status.set_label('Starting')
        while gtk.events_pending():
            gtk.main_iteration()
        child = self.reconnectCamera()
        self.takePic(child)
        self.dumpCameraFiles()
        self.createFavor()
        self.renameMoveFiles()
        self.displayImages()
        self.status.set_label('Done')
        self.progressbar.set_fraction(1)
        while gtk.events_pending():
            gtk.main_iteration()
        #self.resetDisplay()
        
    def onPrintClick(self, widget):
        self.printImages()

    def onInputEnter(self, widget):
        self.resetDisplay()

    def resetDisplay(self):
        print 'reset display'
        self.progressbar.set_fraction(0)
        self.entry.set_text("User")
        self.image1.set_from_file("")
        self.image2.set_from_file("")
        self.image3.set_from_file("")
        self.image4.set_from_file("")
        self.imageStrip.set_from_file("PhotoBoothStrip.jpg")
        self.status.set_label('Ready to start')
        os.system('rm temp1.jpg temp2.jpg temp3.jpg temp4.jpg print.jpg temp.avi')

#utility functions

    def renamer(self, files, pattern, replacement):
        for pathname in glob.glob(files):
            basename = os.path.basename(pathname)
            new_filename= re.sub(pattern, replacement, basename)
            if new_filename != basename:
                os.rename(pathname,os.path.join(os.path.dirname(pathname), new_filename))

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
