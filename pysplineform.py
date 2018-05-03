# -*- coding: utf-8 -*-
from ipydex import IPS, ST, ip_syshook, sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


def _destroy2(self, wk):
    print(self)
    print("----")
    print(self._destroy_callbacks)
    for callback in self._destroy_callbacks:
        try:
            callback(self)
        except ReferenceError:
            pass

mpl.cbook._BoundMethodProxy._destroy = lambda x, y: None


class DraggablePoint(object):

    def __init__(self, x, y, color="b"):

        rect, = plt.plot([x], [y], 'o', c=color)

        self.init(rect)

        pointlist.append(self)

    def init(self, rect):
        self.rect = rect
        self.press = None
        self.connected = False
        self.active = 0

        self.activate()

    def activate(self):
        self.active = 1
        self.rect.set_ms(8)
        self.connect()

    def connect(self):
        if self.connected == True: return
        else : self.connected = True

        'connect to all the events we need'
        self.cidpress = self.rect.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.rect.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.rect.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)


    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.rect.axes: return

        contains, attrd = self.rect.contains(event)
        if not contains: return
        x0, y0 = self.rect._x[0], self.rect._y[0]
        #print 'event contains', x0, y0
        self.press = x0, y0, event.xdata, event.ydata

    def getxy(self):
        return self.rect._x[0], self.rect._y[0]

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.press is None: return
        if event.inaxes != self.rect.axes: return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress

        self.rect.set_xdata(np.r_[x0+dx])
        self.rect.set_ydata(np.r_[y0+dy])

        self.draw_new()

    def draw_new(self):
        self.rect.figure.canvas.draw()

    def on_release(self, event):
        'on release we reset the press data'
        self.press = None
        #self.rect.figure.canvas.draw()
        self.draw_new()

    def disconnect(self):
        'disconnect all the stored connection ids'
        if self.connected == False: return
        else : self.connected = False

        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)


pointlist = []


if __name__ == '__main__':


    fig = plt.figure()

    N = 2
    for x, y in np.random.rand(N, 2):
        DraggablePoint(x, y)

    plt.show()

    for p in pointlist:
        print(p.getxy())




