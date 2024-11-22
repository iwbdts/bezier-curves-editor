"""
This is my Bezier Curves simulator

"""
import uuid
import pygame

from pygame.locals import (# pylint: disable=no-name-in-module
MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN,
K_s, K_d, K_w, K_q, K_n, K_l, K_p,
)
pygame.init()  # pylint: disable=no-member
width, height = 500, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Rysowanko krzywych Beziera")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class BezierCurve:
    """Represents a Bezier curve and provides methods to draw and manipulate it."""

    def __init__(self, control_points):
        """Initializes the Bezier curve object."""
        self.control_points = control_points
        self.curve_points = []

    def replace(self, prev_point, new_point):
        """Replaces a point with a new point"""
        for i, point in enumerate(self.control_points):
            if prev_point == point:
                self.control_points[i] = new_point
                break

    def bezier(self, t, control_points):
        """Calculates Bezier points"""
        s = 1 - t
        n = len(control_points)
        n_over_i = 1
        control_point_i_x = control_points[0][0]
        control_point_i_y = control_points[0][1]
        t_pow_i = 1

        for i in range(1, n):
            n_over_i = n_over_i * (n - i) // i
            t_pow_i = t_pow_i * t
            control_point_i_x = (control_point_i_x * s + n_over_i
                                 * control_points[i][0] * t_pow_i)
            control_point_i_y = \
                (control_point_i_y
                 * s + n_over_i * control_points[i][1] * t_pow_i)

        return control_point_i_x, control_point_i_y

    def redraw_curve(self):
        """Redraws a curve"""
        if len(self.control_points) > 1:
            m = 200
            self.curve_points = \
                [self.bezier
                 (j / m, self.control_points) for j in range(m - 1)]
            self.curve_points.append(self.control_points[-1])
            self.draw_control_lines()
            self.draw_curve()

    def draw_control_lines(self):
        """Draws control lines"""
        if self == ACTIVE_CURVE:
            if len(self.control_points) > 1 and CONTROL_LINES_ON:
                (pygame.draw.lines
                 (screen, BLACK, False, self.control_points, 1))
            if CONTROL_POINTS_ON:
                for p in self.control_points:
                    pygame.draw.circle(screen, RED, (p[0], p[1]), radius=3)

    def draw_curve(self):
        """Draws the curve"""
        color = BLUE
        if ACTIVE_CURVE == self:
            color = GREEN
        if len(self.curve_points) > 1:
            pygame.draw.lines(screen, color, False, self.curve_points, 2)


def draw_grid():
    """Draws grid"""
    grid_size = 10
    for x in range(0, width, grid_size):
        (pygame.draw.line
         (screen, (245, 245, 245), (x, 0), (x, height), 1))
    for y in range(0, height, grid_size):
        (pygame.draw.line
         (screen, (245, 245, 245), (0, y), (width, y), 1))


def generate_unique_filename():
    """Generates an unique filename"""
    return str(uuid.uuid4())[:8]


RUNNING = True
curves = [BezierCurve([])]
ACTIVE_CURVE_INDEX = 0
ACTIVE_CURVE = curves[0]
init_pos = pygame.mouse.get_pos()
DRAGGING_POS = (-1, -1)
POINT_DRAGGING = False
CONTROL_LINES_ON, CONTROL_POINTS_ON = True, True
screen.fill(WHITE)
draw_grid()
pygame.display.update()
clock = pygame.time.Clock()

if __name__ == "__main__":
    while RUNNING:
        clock.tick(60)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:  # pylint: disable=no-member

                RUNNING = False

            elif event.type == MOUSEBUTTONDOWN:
                init_pos = pygame.mouse.get_pos()
                for a in ACTIVE_CURVE.control_points:
                    if (
                            a[0] - 3 <= init_pos[0] <= a[0] + 3
                            and a[1] - 3 <= init_pos[1] <= a[1] + 3
                    ):
                        DRAGGING_POS = a
                        POINT_DRAGGING = True
                        # print("detected point dragging!:", dragging_pos)
                        break

            elif event.type == pygame.MOUSEMOTION:  # pylint: disable=no-member
                final_pos = pygame.mouse.get_pos()
                if POINT_DRAGGING:
                    ACTIVE_CURVE.replace(DRAGGING_POS, final_pos)
                    DRAGGING_POS = final_pos

            elif event.type == MOUSEBUTTONUP:
                final_pos = pygame.mouse.get_pos()
                if POINT_DRAGGING:
                    # print("point dragging over!")
                    ACTIVE_CURVE.replace(DRAGGING_POS, final_pos)
                    POINT_DRAGGING = False
                    # print("replacing", dragging_pos, "with", final_pos)
                else:
                    ACTIVE_CURVE.control_points.append(final_pos)

            elif event.type == KEYDOWN:
                if event.key == K_s:
                    # S - zapisuje obrazek
                    screen.fill(WHITE)
                    draw_grid()
                    for curve in curves:
                        curve.redraw_curve()
                    pygame.display.update()
                    FILENAME = f"drawn_image_{generate_unique_filename()}.png"
                    pygame.image.save(screen, FILENAME)
                    print(f"Image saved as {FILENAME}")

                if event.key == K_d:
                    # D - usuwa ostatni pkt kontrolny
                    ACTIVE_CURVE.control_points \
                        = ACTIVE_CURVE.control_points[0:-1]

                if event.key == K_w:
                    # zmienia aktywna krzywa na nastepna
                    ACTIVE_CURVE_INDEX \
                        = (ACTIVE_CURVE_INDEX + 1) % len(curves)
                    ACTIVE_CURVE = curves[ACTIVE_CURVE_INDEX]

                if event.key == K_q:
                    # zmienia aktywna krzywa na poprzednia
                    ACTIVE_CURVE_INDEX \
                        = (ACTIVE_CURVE_INDEX - 1) % len(curves)
                    ACTIVE_CURVE = curves[ACTIVE_CURVE_INDEX]

                if event.key == K_n:
                    # nowa krzywa
                    ACTIVE_CURVE = BezierCurve([])
                    curves.append(ACTIVE_CURVE)
                    ACTIVE_CURVE_INDEX = len(curves)

                if event.key == K_l:
                    # wylacza/wlacza linie pktow kontrolnych
                    CONTROL_LINES_ON = not CONTROL_LINES_ON

                if event.key == K_p:
                    # wylacza/wlacza pkty kontrolne
                    CONTROL_POINTS_ON = not CONTROL_POINTS_ON

            if curves:
                screen.fill(WHITE)
                draw_grid()
                for curve in curves:
                    curve.redraw_curve()
            pygame.display.update()

    pygame.quit() # pylint: disable=no-member
