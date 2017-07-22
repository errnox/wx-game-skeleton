import wx
import random
import time


class RenderTimer(wx.Timer):
    def __init__(self, parent=None):
        pane = wx.BasicDrawPane()
        wx.RenderTimer.__init__(pane)
        self.Notify()
        self.start()


class Game(wx.App):
    def MainLoop(self):
        evtloop = wx.EventLoop()
        old = wx.EventLoop.GetActive()
        wx.EventLoop.SetActive(evtloop)

        while self.keepGoing:
            while evtloop.Pending():
                evtloop.Dispatch()

            time.sleep(0.02)
            self.ProcessIdle()
            self.check_keys()

        wx.EventLoop.SetActive(old)

    def OnInit(self):
        self.frame = Animator(None, -1, "Test")
        self.frame.Show(True)
        self.SetTopWindow(self.frame)

        self.keepGoing = True
        return True

    def check_keys(self):
        if wx.GetKeyState(ord('P')):
            print 'Pausing'
            return
        if wx.GetKeyState(wx.WXK_LEFT):
            self.frame.board.player.move_left(self.frame.board.player.pace)
            self.frame.board.player.color = 1
            self.frame.board.Refresh()
        if wx.GetKeyState(wx.WXK_RIGHT):
            self.frame.board.player.move_right(self.frame.board.player.pace)
            self.frame.board.player.color = 2
            self.frame.board.Refresh()
        if wx.GetKeyState(wx.WXK_DOWN):
            self.frame.board.player.move_down(self.frame.board.player.pace)
            self.frame.board.player.color = 3
            self.frame.board.Refresh()
        if wx.GetKeyState(wx.WXK_UP):
            self.frame.board.player.move_up(self.frame.board.player.pace)
            self.frame.board.player.color = 4
            self.frame.board.Refresh()
        if wx.GetKeyState(wx.WXK_SPACE):
            self.frame.board.throw_ball()

        self.frame.board.check_collisions()


class Animator(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(500, 400))

        self.board = Board(self)
        self.board.SetFocus()
        self.board.main_loop()

        self.Centre()
        self.Show(True)


class Board(wx.Panel):
    ID_TIMER = 1
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.squareHeight = 100
        self.squareWidth = 100
        self.ball_free = True

        self.entities = []  # Z-order
        self.ball = Entity(pos=[100, 200], width=5, color='#CCFFCC',
                           pace=10, type='ball')
        self.entities.append(self.ball)
        self.player = Entity(pos=[10, 20], color=4, pace=10)
        self.entities.append(self.player)

        self.ball = self.entities[0]
        self.player = self.entities[1]

        self.halo = self.player.pace + 10

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)

    def main_loop(self):
        # This could be fleshed out to a proper game loop.
        # Here is an example (without time step):
        #
        # while True:
        #     self.render()
        #     time.sleep(0.1)
        pass

    def render(self):
        dc = wx.PaintDC(self)
        size = self.GetClientSize()

        for entity in self.entities:
            if entity.visible:
                if entity.type == 'square':
                    self.drawSquare(
                        dc, entity.x, entity.y, entity.color,
                        entity.width, entity.height)
                if entity.type == 'ball':
                    self.drawBall(
                        dc, entity.x, entity.y, entity.color,
                        entity.width)

        if self.ball.x < 100:
            self.SetBackgroundColour('black')
        else:
            self.SetBackgroundColour('dark grey')

        # self.check_collisions()

    def OnPaint(self, event):
        self.render()

    def OnKeyDown(self, event):
        pass

    def OnTimer(self, event):
        if event.GetId() == Board.ID_TIMER:
            pass
            event.Skip()

    def drawSquare(self, dc, x, y, shape, width, height):
        colors = ['#000000', '#CC6666', '#66CC66', '#6666CC',
                  '#CCCC66', '#CC66CC', '#66CCCC', '#DAAA00']

        light = ['#000000', '#F89FAB', '#79FC79', '#7979FC',
                 '#FCFC79', '#FC79FC', '#79FCFC', '#FCC600']

        dark = ['#000000', '#803C3B', '#3B803B', '#3B3B80',
                 '#80803B', '#803B80', '#3B8080', '#806200']

        pen = wx.Pen(light[shape])
        pen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(pen)

        # Light reflection
        dc.DrawLine(x, y + height - 1, x, y)
        dc.DrawLine(x, y, x + width - 1, y)

        darkpen = wx.Pen(dark[shape])
        darkpen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(darkpen)

        # Shadow
        dc.DrawLine(x + 1, y + height - 1,
            x + width - 1, y + height - 1)
        dc.DrawLine(x + width - 1,
        y + height - 1, x + width - 1, y + 1)

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(colors[shape]))
        dc.DrawRectangle(x + 1, y + 1, width - 2,
        height - 2)

        if self.player.has_ball:
            c = 5
        else:
            c = 6

        dc.SetBrush(wx.Brush(colors[c]))
        dc.DrawCircle(x, y, 5)

    def drawBall(self, dc, x, y, color, radius):
        pen = wx.Pen(color)
        pen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(pen)

        dc.SetBrush(wx.Brush(color))
        dc.DrawCircle(x, y, radius)

        darkpen = wx.Pen('#333333')
        darkpen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(darkpen)

        dc.SetBrush(wx.Brush(color))
        dc.DrawCircle(x+1, y+1, radius+1)

        lightpen = wx.Pen('#CCCCCC')
        lightpen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(lightpen)

    def check_collisions(self):
        # gap = max([self.player.width, self.player.height]) + 3  # dynamic gap
        gap = 5  # static gap
        if self.ball_free:  # and not self.player.has_ball:
            if self.player.x >= self.ball.x-self.halo and self.player.x <= self.ball.x+self.halo and  self.player.y >= self.ball.y-self.halo and self.player.y <= self.ball.y+self.halo:
                print '-' * 90
                # self.ball.x = self.player.x + self.player.width / 2 - gap
                # self.ball.y = self.player.y + self.player.height / 2 - gap

                self.ball.x = self.player.x
                self.ball.y = self.player.y

                self.ball_free = False
                self.player.has_ball = True
                self.ball.visible = False
        else:
            self.player.has_ball = False
            self.ball_free = True

    def throw_ball(self):
        print self.player.direction
        buff = 5
        if self.player.has_ball:
        # if not self.ball_free:
            if self.player.direction == 'right':
                self.ball.x = self.player.x + self.player.width / 2 + self.halo + buff
                self.ball.y = self.player.y  + self.player.height / 2  # + self.halo
            if self.player.direction == 'left':
                self.ball.x = self.player.x + self.player.width / 2 - self.halo - buff - 10
                self.ball.y = self.player.y  + self.player.height / 2  # + self.halo
            if self.player.direction == 'up':
                self.ball.x = self.player.x  + self.player.width / 2  # - self.halo
                self.ball.y = self.player.y + self.player.height / 2 - self.halo - buff - 10
            if self.player.direction == 'down':
                self.ball.x = self.player.x  + self.player.width / 2  # - self.halo
                self.ball.y = self.player.y + self.player.height / 2 + self.halo + buff
            self.Refresh()
            # self.ball_free = True
            # self.player.has_ball = False
            self.ball_free = False
            self.player.has_ball = True
            self.ball.visible = True


class Entity(object):
    def __init__(self, pos=[0, 0], color=0, pace=10, width=20, height=20,
                 type='square', direction='no', has_ball=False, visible = True):
        # self.pos = pos
        self.x = pos[0] - width / 2
        self.y = pos[1] - height / 2
        self.width = width
        self.height = height
        self.color = color
        self.pace = pace
        self.type = type
        self.direction = direction
        self.has_ball = has_ball
        self.visible = visible

    def move_up(self, n):
        # self.x += n
        self.y -= n
        self.direction = 'up'

    def move_down(self, n):
        # self.x -= n
        self.y += n
        self.direction = 'down'

    def move_right(self, n):
        # self.y += n
        self.x += n
        self.direction = 'right'

    def move_left(self, n):
        # self.y -= n
        self.x -= n
        self.direction = 'left'


if __name__ == '__main__':
    game = Game()
    game.MainLoop()

    # This is an alternative approach:
    #
    # app = wx.App()
    # Animator(None, -1, 'Animator')
    # app.MainLoop()
