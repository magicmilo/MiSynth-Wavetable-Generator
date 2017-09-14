import wx

class TextPanel(wx.Panel):  # just handles mouseover events
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=(0, 424), size=(1024, 200))
        self.SetBackgroundColour(wx.Colour(220, 220, 220))

        names = ["File", "Sample Rate", "Playback Frequency",
                 "Upsampling Ratio", "Smoothing"]
        for i in range(0, 5):
            playfrequency = wx.StaticText(self, -1,
                                          names[i],
                                          pos=(5, (i * 20) + 4),
                                          style=wx.ALIGN_LEFT)