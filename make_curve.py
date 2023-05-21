import pygame
import math
import numpy as np


class MakeCurve():

    def __init__(self):
        self.pts = []
        self.pts_x = []
        self.pts_y = []
        self.pts_x_margin = []
        self.pts_y_margin = []
        self.vec_t = []
        self.vec_x = []
        self.vec_y = []
        self.pressed_point_index = []
        self.pressed_t_point_index = []

        self.npoints = 0
        self.timer = 0
        self.old_pressed = 0
        self.old_button1 = 0
        self.old_npressed = 0
        self.curve_tightness = 0.5
        self.bold_margin = 5
        self.width = 900
        self.height = 600
        self.ncircles = 1000

        self.mid = False
        self.done = False
        self.double_click = False
        self.show_delete_button = False
        self.do_move_point = False
        self.do_move_t_point = False
        self.clear_line = False

        self.background_color = (255, 255, 255)
        self.menu_button_pos = (670, 10, 140, 23)
        self.clear_button_pos = (690, 38, 140, 23)
        self.clear_line_button_pos = (690, 66, 140, 23)
        self.show_line_button_pos = (690, 94, 140, 23)
        self.linear_button_pos = (690, 122, 140, 23)
        self.delete_button_pos = (690, 150, 140, 23)

        self.poly_button_pos = (670, 185, 140, 23)
        self.lagrange_button_pos = (690, 213, 140, 23)
        self.bezier_button_pos = (690, 241, 140, 23)
        self.hermite_button_pos = (690, 269, 140, 23)
        self.spline_button_pos = (690, 297, 140, 23)

        self.min_point = [50, 580]
        self.max_point = [750, 580]
        self.tangent = [[50, 50], [50, 50]]

        self.clock = pygame.time.Clock()

        self.poly_function = None

    def reset(self):
        self.show_display()
        self.__init__()

    def show_display(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), 0, 32)
        pygame.display.set_caption("Make Curve")
        self.screen.fill((255, 255, 255))
        self.font = pygame.font.SysFont("consolas", 14)

    def draw_point(self, ptx, pty, thick=3, point_color=(0, 0, 0), bold_point=True, fill_point=False):
        if bold_point:
            w = 3
            if fill_point:
                w = 0
            rect_area = (ptx - self.bold_margin, pty - self.bold_margin,
                         2 * self.bold_margin, 2 * self.bold_margin)
            pygame.draw.rect(self.screen, point_color, rect_area, w)
        pygame.draw.circle(self.screen, point_color, [ptx, pty], thick)

    def ncr(self, n, r):
        f = math.factorial
        return f(n) / f(r) / f(n - r)

    def tangent_point(self, pts):
        return [self.curve_tightness * (pts[2][i] - pts[0][i]) for i in range(len(pts[0]))]

    def spline_base(self, pts):
        npoints = len(pts)
        Z = [[0 for _ in range(npoints)] for __ in range(npoints)]
        Y = [3 for _ in range(npoints)]
        Z[0][0] = 2
        Z[npoints - 1][npoints - 1] = 2
        for i in range(npoints):
            if i != npoints - 1 and i != 0:
                Z[i][i] = 4
            if i > 0:
                Z[i][i - 1] = 1
                Z[i - 1][i] = 1
            if i == 0:
                Y[i] *= pts[i + 1] - pts[i]
            elif i == npoints - 1:
                Y[i] *= pts[i] - pts[i - 1]
            else:
                Y[i] *= pts[i + 1] - pts[i - 1]
        D = np.matmul(np.linalg.inv(Z), np.transpose(Y))
        return D

    def lagrange_polynomial(self, pts, t, vec_t):
        npoints = len(pts)
        qt = 0
        for i in range(npoints):
            Lt = 1
            for j in range(npoints):
                if i != j:
                    Lt *= (t - vec_t[j]) / (vec_t[i] - vec_t[j])
            qt += pts[i] * Lt
        return qt

    def bezier_polynomial(self, pts, t, vec_t):
        npoints = len(pts)
        p = 0
        for i in range(npoints):
            b = self.ncr(npoints-1, i) * t**i * (1-t)**(npoints-1-i)
            p += pts[i] * b
        return p

    def hermite_polynomial(self, pts, t, tangent):
        tpow2 = t**2
        tpow3 = t**3
        h0 = 2*(tpow3) - 3*(tpow2) + 1
        h1 = -2*(tpow3) + 3*(tpow2)
        h2 = tpow3 - 2*(tpow2) + t
        h3 = tpow3 - tpow2
        return pts[0]*h0 + pts[1]*h1 + tangent[0]*h2 + tangent[1]*h3

    def spline_polynomial(self, pts, t, vec_t):
        a = pts[0]
        b = vec_t[0]
        c = 3 * (pts[1] - pts[0]) - 2*vec_t[0] - vec_t[1]
        d = 2 * (pts[0] - pts[1]) + vec_t[0] + vec_t[1]
        return a + b*t + c*t**2 + d*t**3

    def draw_polynomial(self, vec_x, vec_y, vec_t, line_color=(255, 0, 0), thick=1, bold_point=False, update_poly=True):
        if self.clear_line:
            self.screen.fill((255, 255, 255))
        npoints = len(vec_x)
        ub_loop = npoints - 1
        if self.poly_function == "hermite":
            ub_loop = npoints
        if self.poly_function == "spline":
            Dx = self.spline_base(vec_x)
            Dy = self.spline_base(vec_y)
        for i in range(ub_loop):
            for t in range(self.ncircles):
                loop_t = i + t / self.ncircles
                if update_poly == False or self.poly_function == "bezier" or self.poly_function == "hermite" or self.poly_function == "spline":
                    loop_t = t / self.ncircles
                if update_poly == False:
                    qt_x = self.lagrange_polynomial(
                        vec_x, t=loop_t, vec_t=vec_t)
                    qt_y = self.lagrange_polynomial(
                        vec_y, t=loop_t, vec_t=vec_t)
                    self.draw_point(int(qt_x), int(
                        qt_y), point_color=line_color, thick=thick, bold_point=bold_point)
                elif self.poly_function != "hermite" and update_poly:
                    if self.poly_function == "spline":
                        vec_tx = Dx[i: i + 2]
                        vec_ty = Dy[i: i + 2]
                        vec_xsub = vec_x[i: i + 2]
                        vec_ysub = vec_y[i: i + 2]
                    else:
                        vec_tx = vec_t
                        vec_ty = vec_t
                        vec_xsub = vec_x
                        vec_ysub = vec_y
                    qt_x = self.curve_function(
                        vec_xsub, t=loop_t, vec_t=vec_tx)
                    qt_y = self.curve_function(
                        vec_ysub, t=loop_t, vec_t=vec_ty)
                    self.draw_point(int(qt_x), int(
                        qt_y), point_color=line_color, thick=thick, bold_point=bold_point)
                elif self.poly_function == "hermite":
                    if i > 0:
                        tangent_x = [self.tangent[i][0]
                                     for i in range(i - 1, i + 1)]
                        tangent_y = [self.tangent[i][1]
                                     for i in range(i - 1, i + 1)]
                        if i < npoints - 1:
                            self.mid = True
                            vec_xh = vec_x[i - 1:i + 2]
                            vec_yh = vec_y[i - 1:i + 2]
                        else:
                            self.mid = False
                            vec_xh = vec_x[i - 1:i + 1]
                            vec_yh = vec_y[i - 1:i + 1]
                        qt_x = self.curve_function(
                            vec_xh, t=loop_t, tangent=tangent_x)
                        qt_y = self.curve_function(
                            vec_yh, t=loop_t, tangent=tangent_y)
                        self.draw_point(int(qt_x), int(
                            qt_y), point_color=line_color, thick=thick, bold_point=bold_point)

    def add_new_point(self):
        self.draw_point(self.ptx, self.pty)
        self.pts.append(self.pt)
        self.pts_x.append(self.ptx)
        self.pts_y.append(self.pty)
        self.pts_x_margin.extend(
            [self.ptx - i for i in range(self.bold_margin)])
        self.pts_x_margin.extend(
            [self.ptx + i for i in range(self.bold_margin)])
        self.pts_y_margin.extend(
            [self.pty - i for i in range(self.bold_margin)])
        self.pts_y_margin.extend(
            [self.pty + i for i in range(self.bold_margin)])
        self.vec_t.append(self.npoints)
        if self.npoints > 1:
            self.tangent[0] = [0, 0]
            self.tangent[self.npoints - 1] = [0, 0]
            self.tangent.insert(
                self.npoints - 1, self.tangent_point(self.pts[self.npoints - 2: self.npoints + 1]))

    def draw_new_point(self, add_point=True):
        if add_point:
            self.add_new_point()
        if self.npoints > 0:
            if self.poly_function != None:
                self.update_line(self.pts_x, self.pts_y, move_point=False)
                self.poly_function = self.old_poly_function
                self.draw_polynomial(self.pts_x, self.pts_y,
                                     self.vec_t, line_color=(0, 0, 100))
            else:
                self.draw_polynomial(self.pts_x[self.npoints - 1:self.npoints + 1], self.pts_y[self.npoints - 1:self.npoints + 1],
                                     vec_t=[0, 1], line_color=(255, 0, 0), thick=1, update_poly=False)
        if self.poly_function == "lagrange":
            self.make_scroll_bar(self.npoints)

    def find_point(self):
        ptx_index = [int(i / (self.bold_margin * 2))
                     for i, x_axis in enumerate(self.pts_x_margin) if x_axis == self.ptx]
        pty_index = [int(i / (self.bold_margin * 2))
                     for i, y_axis in enumerate(self.pts_y_margin) if y_axis == self.pty]
        pt_index = [i for i in ptx_index if i in pty_index]
        return pt_index

    def delete_point(self):
        self.pts.remove(self.pts[self.old_pressed_point_index[0]])
        self.pts_x.remove(self.pts_x[self.old_pressed_point_index[0]])
        self.pts_y.remove(self.pts_y[self.old_pressed_point_index[0]])
        self.vec_t.remove(self.vec_t[self.old_pressed_point_index[0]])
        for i in range(self.old_pressed_point_index[0], self.npoints - 1):
            self.vec_t[i] -= 1
        self.vec_t[0] = 0
        [self.pts_x_margin.remove(self.pts_x_margin[i]) for i in range((self.old_pressed_point_index[0] + 1) * self.bold_margin * 2 - 1,
                                                                       self.old_pressed_point_index[0] * self.bold_margin * 2, -1)]
        [self.pts_y_margin.remove(self.pts_y_margin[i]) for i in range((self.old_pressed_point_index[0] + 1) * self.bold_margin * 2 - 1,
                                                                       self.old_pressed_point_index[0] * self.bold_margin * 2, -1)]
        self.npoints = self.npoints - 2

    def update_line(self, pts_x, pts_y, move_point):
        self.screen.fill((255, 255, 255))
        npoints = len(pts_x)
        for i in range(npoints):
            self.draw_point(pts_x[i], pts_y[i])
            if i > 0:
                self.draw_polynomial(pts_x[i - 1: i + 1], pts_y[i - 1: i + 1], vec_t=[
                                     0, 1], line_color=(255, 0, 0), thick=1, bold_point=False, update_poly=False)
        if self.poly_function == "lagrange":
            if move_point:
                self.make_scroll_bar(npoints)
            else:
                self.make_scroll_bar(len(self.pts))

    def option_button(self, pos, button_color=(211, 211, 211)):
        pygame.draw.rect(self.screen, button_color, pos)

    def is_point_in_button(self, pos):
        if pos[0] <= self.ptx <= pos[0]+pos[2] and pos[1] <= self.pty <= (pos[1]+pos[3]):
            return True
        else:
            return False

    def print_text(self, msg, text_color, pos=(15, 15)):
        textSurface = self.font.render(msg, True, text_color, None)
        textRect = textSurface.get_rect()
        textRect.topleft = pos
        self.screen.blit(textSurface, textRect)

    def show_button(self, msg, button_pos, msg_pos, button_color=(211, 211, 211), text_color=(0, 0, 0), highlight_button=True):
        pt_in_button = self.is_point_in_button(button_pos)
        if pt_in_button and highlight_button:
            make_darker_color = (50, 50, 50)
            button_color = tuple(
                map(lambda i, j: i - j, button_color, make_darker_color))
        self.option_button(button_pos, button_color)
        self.print_text(msg=msg, text_color=text_color, pos=msg_pos)

    def change_point(self):
        press_id = self.old_pressed_point_index[0]
        self.pts[press_id] = [self.pts_x[press_id], self.pts_y[press_id]]
        lb = press_id * self.bold_margin * 2
        ub = (press_id + 1) * self.bold_margin * 2
        self.pts_x_margin[lb: ub] = [self.ptx - i for i in range(self.bold_margin)]+[
            self.ptx + i for i in range(self.bold_margin)]
        self.pts_y_margin[lb: ub] = [self.pty - i for i in range(self.bold_margin)]+[
            self.pty + i for i in range(self.bold_margin)]

    def move_point(self):
        self.pts_x[self.pressed_point_index[0]] = self.ptx
        self.pts_y[self.pressed_point_index[0]] = self.pty
        self.update_line(self.pts_x, self.pts_y, move_point=True)
        if self.poly_function == "hermite":
            if 1 < self.pressed_point_index[0] < self.npoints - 2:
                pts = self.pts[self.pressed_point_index[0] -
                               2:self.pressed_point_index[0] + 3]
                pts[2][0] = self.ptx
                pts[2][1] = self.pty
                self.tangent[self.pressed_point_index[0] -
                             1] = self.tangent_point(pts[0:3])
                self.tangent[self.pressed_point_index[0]
                             ] = self.tangent_point(pts[1:4])
                self.tangent[self.pressed_point_index[0] +
                             1] = self.tangent_point(pts[2:5])
            elif self.pressed_point_index[0] == 1:
                pts = self.pts[0:self.pressed_point_index[0] + 3]
                pts[1][0] = self.ptx
                pts[1][1] = self.pty
                self.tangent[self.pressed_point_index[0]
                             ] = self.tangent_point(pts[0:3])
                self.tangent[self.pressed_point_index[0] +
                             1] = self.tangent_point(pts[1:4])
            elif self.pressed_point_index[0] == self.npoints - 2:
                pts = self.pts[self.pressed_point_index[0] - 2:self.npoints]
                pts[2][0] = self.ptx
                pts[2][1] = self.pty
                self.tangent[self.pressed_point_index[0] -
                             1] = self.tangent_point(pts[0:3])
                self.tangent[self.pressed_point_index[0]
                             ] = self.tangent_point(pts[1:4])
            elif self.pressed_point_index[0] == 0:
                pts = self.pts[self.pressed_point_index[0]:self.npoints + 3]
                pts[0][0] = self.ptx
                pts[0][1] = self.pty
                self.tangent[self.pressed_point_index[0] +
                             1] = self.tangent_point(pts[0:3])
            elif self.pressed_point_index[0] == self.npoints - 1:
                pts = self.pts[self.pressed_point_index[0] -
                               2:self.pressed_point_index[0] + 1]
                pts[2][0] = self.ptx
                pts[2][1] = self.pty
                self.tangent[self.pressed_point_index[0] -
                             1] = self.tangent_point(pts[0:3])
        if self.poly_function != None:
            self.draw_polynomial(self.pts_x, self.pts_y,
                                 self.vec_t, line_color=(0, 0, 100))
        self.show_menu_button()

    def highlight_point(self):
        self.draw_point(self.pts_x[self.pressed_point_index[0]], self.pts_y[self.pressed_point_index[0]],
                        point_color=(0, 0, 0), bold_point=True, fill_point=True)

    def make_scroll_bar(self, npoints):
        self.vec_tx_margin = []
        self.vec_tx_margin.extend(
            [self.min_point[0] - i for i in range(self.bold_margin)])
        self.vec_tx_margin.extend(
            [self.min_point[0] + i for i in range(self.bold_margin)])
        self.vec_ty_margin = [self.min_point[1] - i for i in range(self.bold_margin)] + [
            self.min_point[1] + i for i in range(self.bold_margin)]
        if npoints > 0:
            self.show_scroll_bar()
            self.add_scroll_bar_point()
        self.vec_tx_margin.extend(
            [self.max_point[0] - i for i in range(self.bold_margin)])
        self.vec_tx_margin.extend(
            [self.max_point[0] + i for i in range(self.bold_margin)])

    def add_scroll_bar_point(self):
        npoints = len(self.vec_t)
        for i in range(1, npoints):
            x_scpt = int(self.max_point[0] - ((self.max_point[0] - self.min_point[0]) * (
                self.vec_t[npoints - 1] - self.vec_t[i]) / (self.vec_t[npoints - 1] - self.vec_t[0])))
            self.draw_point(x_scpt, self.min_point[1], thick=3, point_color=(
                105, 105, 105), bold_point=True, fill_point=False)
            self.vec_tx_margin.extend(
                [x_scpt - i for i in range(self.bold_margin)])
            self.vec_tx_margin.extend(
                [x_scpt + i for i in range(self.bold_margin)])

    def show_scroll_bar(self):
        self.option_button(pos=(30, 570, 740, 20),
                           button_color=(255, 255, 255))
        self.draw_point(self.min_point[0], self.min_point[1], thick=3, point_color=(
            105, 105, 105), bold_point=True, fill_point=False)
        self.draw_point(self.max_point[0], self.max_point[1], thick=3, point_color=(
            105, 105, 105), bold_point=True, fill_point=False)
        self.draw_polynomial([self.min_point[0], self.max_point[0]], [self.min_point[1], self.max_point[1]], vec_t=[
                             0, 1], line_color=(105, 105, 105), thick=1, update_poly=False)

    def find_vect_point(self):
        ptx_index = [int(i / (self.bold_margin * 2))
                     for i, x_axis in enumerate(self.vec_tx_margin) if x_axis == self.ptx]
        pty_index = [int(i / (self.bold_margin * 2))
                     for i, y_axis in enumerate(self.vec_ty_margin) if y_axis == self.pty]
        if len(ptx_index) < 0 and len(pty_index) < 0:
            ptx_index = []
        return ptx_index

    def change_vect(self):
        npoints = len(self.vec_t)
        press_id = self.pressed_t_point_index[0]
        self.vec_t[press_id] = self.vec_t[npoints - 1] - ((self.max_point[0] - self.ptx) * (
            self.vec_t[npoints - 1] - self.vec_t[0]) / (self.max_point[0] - self.min_point[0]))
        lb = press_id * self.bold_margin * 2
        ub = (press_id + 1) * self.bold_margin * 2
        self.vec_tx_margin[lb: ub] = [self.vec_t[press_id] - i for i in range(
            self.bold_margin)]+[self.ptx + i for i in range(self.bold_margin)]

    def move_vect_point(self):
        self.screen.fill((255, 255, 255))
        self.change_vect()
        if self.poly_function == "lagrange":
            self.make_scroll_bar(len(self.vec_t))
        self.update_line(self.pts_x, self.pts_y, move_point=False)
        if self.poly_function != None:
            self.draw_polynomial(self.pts_x, self.pts_y,
                                 self.vec_t, line_color=(0, 0, 100))
        self.show_menu_button()

    def show_menu_button(self):
        self.show_button(msg="View", button_pos=self.menu_button_pos, msg_pos=(
            675, 15), button_color=(161, 161, 161), highlight_button=False)
        self.show_button(
            msg="Reset", button_pos=self.clear_button_pos, msg_pos=(695, 43))
        self.show_button(
            msg="Clear Line", button_pos=self.clear_line_button_pos, msg_pos=(695, 71))
        self.show_button(
            msg="Show Line", button_pos=self.show_line_button_pos, msg_pos=(695, 99))
        self.show_button(msg="Clear Curve",
                         button_pos=self.linear_button_pos, msg_pos=(695, 127))

        self.show_button(msg="Curve Options", button_pos=self.poly_button_pos, msg_pos=(
            675, 190), button_color=(161, 161, 161), highlight_button=False)
        self.show_button(
            msg="Lagrange", button_pos=self.lagrange_button_pos, msg_pos=(695, 218))
        self.show_button(
            msg="Bezier", button_pos=self.bezier_button_pos, msg_pos=(695, 246))
        self.show_button(
            msg="Hermite", button_pos=self.hermite_button_pos, msg_pos=(695, 274))
        self.show_button(
            msg="Spline", button_pos=self.spline_button_pos, msg_pos=(695, 302))

        live_pos = "Current position: ("+str(self.ptx)+","+str(self.pty)+")"
        self.show_caption(live_pos, (10, 10, 225, 15))
        self.show_caption("Tips: Double click to move point",
                          (10, 30, 225, 15))

    def show_caption(self, msg, pos):
        self.option_button(pos, button_color=(255, 255, 255))
        self.show_button(msg, pos, pos[0:2], button_color=(
            255, 255, 255), highlight_button=False)

    def run(self):
        self.show_display()
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.pressed = -1
                    if self.timer == 0:
                        self.timer = 0.001
                    elif self.timer <= 0.5:
                        self.double_click = True
                        self.timer = 0
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.pressed = 1
                elif event.type == pygame.QUIT:
                    self.done = True
                else:
                    self.pressed = 0

            self.button1, self.button2, self.button3 = pygame.mouse.get_pressed()
            self.ptx, self.pty = pygame.mouse.get_pos()
            self.pt = [self.ptx, self.pty]

            self.show_menu_button()

            if self.old_pressed == -1 and self.pressed == 1 and self.old_button1 == 1 and self.button1 == 0:
                if self.is_point_in_button(self.linear_button_pos):
                    self.poly_function = None
                    self.clear_line = False
                    self.update_line(self.pts_x, self.pts_y, move_point=False)
                elif self.is_point_in_button(self.clear_line_button_pos):
                    self.clear_line = True
                elif self.is_point_in_button(self.show_line_button_pos):
                    self.clear_line = False
                elif self.is_point_in_button(self.lagrange_button_pos):
                    self.poly_function = "lagrange"
                elif self.is_point_in_button(self.bezier_button_pos):
                    self.poly_function = "bezier"
                elif self.is_point_in_button(self.hermite_button_pos):
                    self.poly_function = "hermite"
                elif self.is_point_in_button(self.spline_button_pos):
                    self.poly_function = "spline"

                if self.poly_function == None:
                    self.curve_function = self.lagrange_polynomial
                elif self.poly_function == "lagrange":
                    self.curve_function = self.lagrange_polynomial
                elif self.poly_function == "bezier":
                    self.curve_function = self.bezier_polynomial
                elif self.poly_function == "hermite":
                    self.curve_function = self.hermite_polynomial
                elif self.poly_function == "spline":
                    self.curve_function = self.spline_polynomial

                if self.poly_function != None:
                    if self.clear_line == False:
                        self.update_line(
                            self.pts_x, self.pts_y, move_point=False)
                    self.draw_polynomial(
                        self.pts_x, self.pts_y, self.vec_t, line_color=(0, 0, 100))

                if self.is_point_in_button(self.clear_button_pos):
                    self.reset()
                elif self.do_move_t_point:
                    self.do_move_t_point = False
                elif self.do_move_point:
                    self.change_point()
                    self.do_move_point = False
                    self.show_delete_button = False
                elif self.old_npressed > 0 and self.is_point_in_button(self.delete_button_pos):
                    self.delete_point()
                    self.update_line(self.pts_x, self.pts_y, move_point=False)
                    if self.poly_function != None:
                        self.draw_polynomial(
                            self.pts_x, self.pts_y, self.vec_t, line_color=(0, 0, 100))
                    self.pressed_point_index = []
                    self.show_delete_button = False
                elif self.ptx < 690:
                    if self.npoints == 0:
                        self.draw_new_point(add_point=True)
                    elif self.npoints > 0:
                        self.pressed_point_index = self.find_point()
                        if self.poly_function == "lagrange":
                            if self.npoints > 1:
                                self.pressed_t_point_index = self.find_vect_point()
                        ntpressed = len(self.pressed_t_point_index)
                        npressed = len(self.pressed_point_index)
                        if self.double_click:
                            if npressed > 0:
                                self.do_move_point = True
                            elif ntpressed > 0:
                                self.do_move_t_point = True
                            self.double_click = False
                        elif npressed == 0 and ntpressed == 0:
                            self.draw_new_point(add_point=True)
                        elif npressed > 0 and self.double_click == False and self.show_delete_button == False:
                            self.show_delete_button = True
                            self.highlight_point()
                self.old_pressed_point_index = self.pressed_point_index
                self.old_npressed = len(self.old_pressed_point_index)

            self.npoints = len(self.pts)

            if self.show_delete_button:
                self.show_button(
                    msg="Delete", button_pos=self.delete_button_pos, msg_pos=(695, 155))
            if self.do_move_point:
                self.move_point()
            elif self.do_move_t_point:
                self.move_vect_point()

            pygame.display.update()
            self.old_pressed = self.pressed
            self.old_button1 = self.button1
            self.old_poly_function = self.poly_function

            if self.timer != 0:
                self.timer += 0.001
                if self.timer >= 0.5:
                    self.double_click = False
                    self.timer = 0

        pygame.quit()


if __name__ == '__main__':
    g = MakeCurve()
    g.run()
