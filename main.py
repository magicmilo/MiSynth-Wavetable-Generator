#coding: utf-8
#!/usr/bin/env python3
#Initial test code for MiSynth Wave Generator
#Opens Wave Files And Cuts And Plays Them As The FPGA will
#Synth plays back 2048 samples at frequency of note
#Effective sample rate is 901,120Hz @ 440Hz

import math
import struct
import os
import wave
import wx
import audiothread
import wavehandle
import sdisp
import queue
import sys
import threading
import numpy as np

class MyFrame(wx.Frame):
    def __init__(self, parent, title, wavehandle):
        wx.Frame.__init__(self, parent, -1, title, size=(1024, 662))
        self.wavehandle = wavehandle

        self.scale = 8
        self.shift = 0

        # Create the menubar
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(wx.ID_OPEN, "Open\tAlt-O", "Open Wave")
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit")

        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnOpenButton, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnQuitButton, id=wx.ID_EXIT)

        # and put the menu on the menubar
        menuBar.Append(menu, "&Actions")
        self.SetMenuBar(menuBar)
        #self.CreateStatusBar()

        self.wavepanel = WavePanel(self, self.getscale, self.setsector)
        self.wavepanel.SetBackgroundColour(wx.Colour(32,55,91))
        self.buttonpanel = wx.Panel(self, -1, pos=(0, 512), size=(1024, 40))
        self.textpanel = sdisp.TextPanel(self)

        totalseconds = self.wavehandle.gettotaltime()
        shiftseconds = self.wavehandle.framestoseconds(self.shift)
        self.timestamp = wx.StaticText(self.wavepanel, -1,
                                       ("Time: " + str(shiftseconds)
                                        + "/" + str(totalseconds)),
                                       pos=(2, 2),
                                       style=wx.ALIGN_LEFT)
        self.timestamp.SetForegroundColour((217, 66, 244))

        # Now create the Panel to put the other controls on.
        btnOpen = wx.Button(self.buttonpanel, wx.ID_OPEN, "Open",
                            pos=(2, 0), size=(80, 40))
        btnExport = wx.Button(self.buttonpanel, -1, "Export",
                              pos=(84, 0), size=(80, 40))
        btnQuit = wx.Button(self.buttonpanel, wx.ID_EXIT, "Quit",
                            pos=(166, 0), size=(80, 40))
        self.btnPlay = wx.ToggleButton(self.buttonpanel, -1, "Play",
                                       pos=(943, 0), size=(80, 40))

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnOpenButton, btnOpen)
        self.Bind(wx.EVT_BUTTON, self.OnExportButton, btnExport)
        self.Bind(wx.EVT_BUTTON, self.OnQuitButton, btnQuit)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnPlayButton, self.btnPlay)
        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)
        self.wavepanel.Bind(wx.EVT_PAINT, self.onPaint)
        self.contentNotSaved = False
        self.fileloaded = False
        self.quadrant = -1
        self.Centre()

    def setsector(self, sector):
        self.quadrant = abs(sector)
        self.DrawWave()

    def getscale(self):
        return self.scale

    def getSample(self, sector):
        print("obtaining sample")
        if self.quadrant == -1:
            self.setsector(1)
        sample = self.wavehandle.getaudiodata(self.shift, 0, sector)
        return sample

    def onPaint(self, event):
        print("Drawing")
        self.DrawWave()

    def OnPlayButton(self, event):
        if self.btnPlay.GetValue():
            self.audiohandle = audiothread.AudioHandler()
            if self.fileloaded:
                self.audiohandle.setsample(self.getSample(self.quadrant), 2048)
            self.audiohandle.start()
        else:
            self.audiohandle.stop()
            self.audiohandle = None

    def onMouseWheel(self, event):
        if self.wavepanel.mouseOver:
            if self.wavepanel.ctrlDown:
                if event.GetWheelRotation() > 0:
                    if(self.scale > 1):
                        self.scale = self.scale >> 1
                else:
                    if(self.scale < 2097151):
                        self.scale = self.scale << 1
                self.DrawWave()
            else:
                if event.GetWheelRotation() > 0:
                    if(self.shift > 0):
                        self.shift -= 2000
                else:
                    if (self.shift < 10000000):
                        self.shift += 2000
                self.DrawWave()

    def OnOpenButton(self, evt):
        """Event handler for the button click."""
        if self.contentNotSaved:
            if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return
        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open .wav file.", wildcard="WAV files (*.wav)|*.wav",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with wave.open(pathname, 'r') as file:
                    self.wavehandle.loadwave(file)
                    self.DrawWave()
                    self.fileloaded = True
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def OnExportButton(self, evt):
        print("Export")

    def OnQuitButton(self, evt):
        self.Close()

    def DrawWave(self):
        dc = wx.PaintDC(self.wavepanel)
        dc.Clear()
        totalseconds = self.wavehandle.gettotaltime()
        shiftseconds = self.wavehandle.framestoseconds(self.shift)
        self.timestamp.SetLabel("Time: " + str(shiftseconds) + "/" + str(
                                           totalseconds))

        dc.SetBrush(wx.Brush(wx.Colour(16,28,45), wx.SOLID))
        dc.DrawRectangle(256, 0, 512, 512)
        # Centre Line
        pointdata = self.wavehandle.getdrawpoints(self.shift)

        for x in range(1, 1024): #Ugly
            if(x > 256) and (x < 768):
                dc.SetPen(wx.Pen((0, 255, 242), 1, wx.PENSTYLE_SOLID))
            else:
                dc.SetPen(wx.Pen((183, 204, 163), 1, wx.PENSTYLE_SOLID))
            dc.DrawLine(x-1, pointdata[x-1], x, pointdata[x])
            #dc.DrawPoint(x, pointdata[x])
            if(x == 256) or (x==768):
                dc.SetPen(wx.Pen((0, 0, 0), 1, wx.PENSTYLE_DOT))
                dc.DrawLine(x, 0, x, 512)
            if(x == 496) or (x == 528):
                dc.SetPen(wx.Pen((0, 0, 0), 1, wx.PENSTYLE_DOT))
                dc.DrawLine(x, 0, x, 512)


class WavePanel(wx.Panel): #just handles mouseover events
    def __init__(self, parent, getter, sender):
        wx.Panel.__init__(self, parent, pos=(0,0),size=(1024, 512))
        self.mouseOver = False
        self.ctrlDown = False
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseOver)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Bind(wx.EVT_KEY_UP, self.onKeyRelease)
        self.Bind(wx.EVT_LEFT_DOWN, self.onMouseClick)
        self.getter = getter
        self.sender = sender

    def onMouseClick(self, event):
        if self.mouseOver:
            x, y = self.ScreenToClient(wx.GetMousePosition())
            sector = abs(x // (2048 / self.getter()))
            self.sender(sector)

    def onMouseOver(self, event):
        self.mouseOver = True

    def onMouseLeave(self, event):
        self.mouseOver = False

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_CONTROL:
            self.ctrlDown = True

    def onKeyRelease(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_CONTROL:
            self.ctrlDown = False

class MyApp(wx.App):
    def OnInit(self):
        waveHandle = wavehandle.WaveHandler()
        frame = MyFrame(None, "MiSynth Editor", waveHandle)
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

if __name__ == '__main__':
    app = MyApp(redirect=True)
    app.MainLoop()
