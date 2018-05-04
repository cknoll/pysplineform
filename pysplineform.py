# -*- coding: utf-8 -*-

"""
This module allows to interactively place points in the plane which will be
interpolated by a spline.

This can, e.g., be used to manually describe a geometric path or a time-signal.
"""


from ipydex import IPS, ST, ip_syshook, sys

import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm
stdcolormap = matplotlib.cm.viridis



# this serves to prevent some strange error messages after closing the figure
mpl.cbook._BoundMethodProxy._destroy = lambda x, y: None


class ManagedCurve(object):

    def __init__(self, N):
        self.N = N
        self.pointlist = []
        self.curve = None

    def draw_curve(self):

        nodes = np.array([p.getxy() for p in self.pointlist])

        xx, yy = nodes.T

        # strongly inspired by https://stackoverflow.com/a/29841948/333403
        tck, u = interpolate.splprep( [xx, yy] ,s = 0 )
        xnew, ynew = interpolate.splev( np.linspace( 0, 1, 100), tck, der=0)

        if self.curve is None:
            self.curve, = plt.plot(xnew, ynew, '-g')
        else:
            self.curve.set_data(xnew, ynew)

        self.curve.figure.canvas.draw()

    def nearest_existing_points_idx(self, xy, successor=False):
        """
        Given x, y find the two neares consecutive points.
        x,y is then sorted in between.

        return: the index of the nearest point or optimal successor
        """
        nodes = np.array([p.getxy() for p in self.pointlist])
        sdiff = np.sum((nodes - np.array(xy))**2, axis=1)


        idxmin1 = np.argmin(sdiff)

        if not successor:
            return idxmin1

        if idxmin1 == 0:
            idxmin2 = 1
        elif idxmin1 == self.N - 1:
            idxmin2 = self.N - 2
        else:
            if sdiff[idxmin1-1] < sdiff[idxmin1+1]:
                idxmin2 = idxmin1 - 1
            else:
                idxmin2 = idxmin1 + 1

        return max(idxmin1, idxmin2)

    def _new_point(self, event):
        # add new point:
        xy = event.xdata, event.ydata

        idx = self.nearest_existing_points_idx(xy, successor=True)
        pnt = DraggablePoint(event.xdata, event.ydata)
        # remove it from the end of the list:
        self.pointlist.pop()
        # and insert it at the desired position (before idx)
        self.pointlist.insert(idx, pnt)

        self.N += 1
        self.draw_curve()

    def _remove_point(self, event):
        if self.N <= 4:
            print("Need at least 4 points for spline.")
            return

        xy = event.xdata, event.ydata
        idx = self.nearest_existing_points_idx(xy)
        pnt = self.pointlist.pop(idx)
        pnt.rect.remove()
        self.curve.remove()
#        IPS()
        self.N -= 1
        self.curve = None
        self.draw_curve()


    def onclick(self, event):
        if event.dblclick and event.button == 1:
            return self._new_point(event)
        elif event.button != 1:
            self._remove_point(event)





    def onkey(self, event):

        if not event.key in ['x', 'y', 'a']: return

        if event.key == 'a':
            self.draw_curve()
            return



class DraggablePoint(object):
    manager = None

    def __init__(self, x, y, color=None):

        if color == None:
            fraction = len(self.manager.pointlist)/self.manager.N
            print(fraction)
            color = stdcolormap(fraction)


        rect, = plt.plot([x], [y], 'o', c=color)

        self.init(rect)

        self.manager.pointlist.append(self)

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
        self.manager.draw_curve()

    def disconnect(self):
        'disconnect all the stored connection ids'
        if self.connected == False: return
        else : self.connected = False

        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)



if __name__ == '__main__':


    np.random.seed(1)

    fig = plt.figure()
    mc = ManagedCurve(N=4)
    cid = fig.canvas.mpl_connect('key_press_event', mc.onkey)
    connection_id = fig.canvas.mpl_connect('button_press_event', mc.onclick)

    DraggablePoint.manager = mc

    for x, y in np.random.rand(mc.N, 2):
        DraggablePoint(x, y)

    mc.draw_curve()

    plt.show()






