import pygame
from pygame.locals import *
pygame.init()

import numpy as np

import sys
import time
from math import sqrt, pi, sin, cos, radians
from random import randint, random
from itertools import combinations
import os
class Wall(pygame.sprite.Sprite):
    def __init__(self, topleft, bottomright, colour):
        # These variables correspond to its INITIAL properties.
        pygame.sprite.Sprite.__init__(self)

        self.position = topleft.astype(float)
        self.size = abs(bottomright.astype(float) - self.position)

        self.colour = colour
        self.image = pygame.Surface(size).convert()
        self.image.fill(colour)

        self.rect.topleft = tuple(round(coor) for coor in self.position)

    def teleport(self, coordinates):
        self.position = coordinates.astype(float)
        self.rect.center = tuple(round(coor) for coor in self.position)
def getDistance(pos1, pos2):
    return np.sqrt(((pos1 - pos2) ** 2).sum())


def toCartesian(r, a):
    '''
    Magnitude r and Angle θ (in degrees) to cartesian
    '''
    return r * cos(radians(a)), -r * sin(radians(a))


class Particle(pygame.sprite.Sprite):
    def __init__(self, mass, radius, colour, position, velocity):
        # These variables correspond to its INITIAL properties.
        # position and velocity are numpy arrays (2d vectors)

        pygame.sprite.Sprite.__init__(self)

        # Assigning arguments as object properties
        self.mass = mass
        self.radius = radius

        self.position = position.astype(float)  # Initial position
        self.velocity = velocity.astype(float)  # pixels per second

        # Setting the image of the particle
        self.colour = colour
        self.image = pygame.Surface((int(2 * radius),) * 2).convert_alpha()
        self.image.fill((0, 0, 0, 0))


        # Coordinates to pygame rect
        self.rect = self.image.get_rect()
        self.rect.center = position.copy()
        self.prevpos = position.copy()

        self.currentlyColliding = []  # For wall collisions
        self.updateProperties()

    def testParticleCollision(self, particle, n=1):
        '''
        n is the number of divisions the collision checks from prevpos
        '''
        collided = False

        prevcurrS = self.position - self.prevpos
        prevcurrP = particle.position - particle.prevpos

        for i in range(1, n + 1):
            betweenS = self.prevpos + prevcurrS * i / n
            betweenP = particle.prevpos + prevcurrP * i / n

            if getDistance(betweenS, betweenP) <= self.radius + particle.radius:
                collided = True
                break

        if not (particle in self.currentlyColliding) or not (self in particle.currentlyColliding):
            if collided:
                self.position = betweenS
                particle.position = betweenP

                self.currentlyColliding.append(particle)
                particle.currentlyColliding.append(self)

                self.particleCollision(particle)

        if not collided:
            try:
                self.currentlyColliding.remove(particle)
                particle.currentlyColliding.remove(self)
            except ValueError:
                pass

        return collided

    def particleCollision(self, particle):
        self.updateProperties()
        particle.updateProperties()

        m1 = self.mass
        m2 = particle.mass

        x1 = self.position
        x2 = particle.position

        v1 = self.velocity
        v2 = particle.velocity
        self.velocity = v1 - (x1 - x2) * 2 * m2 / (m1 + m2) * np.dot(v2 - v1, x2 - x1) / getDistance(x1, x2) ** 2
        particle.velocity = v2 - (x2 - x1) * 2 * m1 / (m2 + m1) * np.dot(v1 - v2, x1 - x2) / getDistance(x2, x1) ** 2

        self.updateProperties()
        particle.updateProperties()

    def testWallCollision(self, res):
        if self.position[0] < -10:
            self.position[0] *= -1
            self.velocity[0] += -1
        if self.position[1] < -10:
            self.position[1] *= -1
            self.velocity[1] *= -1
        if self.position[0] > 1480:
            self.position[0] -= 100
            self.velocity[0] += -1
        if self.position[1] > 1950:
            self.position[1] -= 100
            self.velocity[1] *= -1
        if self.position[0] < 470 and self.position[1] < 470 or self.position[0] < 470 and self.position[1] > 970:
            self.position = [500, self.position[1]]
        if self.position[0] > 970 and self.position[1] < 470 or self.position[0] > 970 and self.position[1] > 970:
            self.position = [900, self.position[1]]
        if self.rect.left <= 0 and not 'Left Wall' in self.currentlyColliding or self.rect.left <= 480 and self.rect.top >= 0 and self.rect.bottom <= 480 and not 'Left Wall' in self.currentlyColliding or self.rect.left <= 480 and self.rect.top >= 960 and self.rect.bottom <= 1440 and not 'Left Wall' in self.currentlyColliding or self.rect.left <= 480 and self.rect.top >= 1440 and self.rect.bottom <= 1920 and not 'Left Wall' in self.currentlyColliding:
            self.currentlyColliding.append('Left Wall')
            self.velocity[0] *= -1
            return True
        if self.rect.left > 0 and 'Left Wall' in self.currentlyColliding or self.rect.left > 480 and 'Left Wall' in self.currentlyColliding:
            if 'Left Wall' in self.currentlyColliding:
                self.currentlyColliding.remove('Left Wall')
        if self.rect.right >= res[0] and not 'Right Wall' in self.currentlyColliding or self.rect.right >= 960 and self.rect.top >= 0 and self.rect.bottom <= 480 and not 'Right Wall' in self.currentlyColliding or self.rect.right >= 960 and self.rect.top >= 960 and self.rect.bottom < 1440 and not 'Right Wall' in self.currentlyColliding or self.rect.right >= 960 and self.rect.top >= 1440 and self.rect.bottom <= 1920 and not 'Right Wall' in self.currentlyColliding:
            self.currentlyColliding.append('Right Wall')
            self.velocity[0] *= -1
            return True
        if self.rect.right < res[0] and 'Right Wall' in self.currentlyColliding or self.rect.right < 960 and 'Right Wall' in self.currentlyColliding:
            if 'Right Wall' in self.currentlyColliding:
                self.currentlyColliding.remove('Right Wall')
        if self.rect.top <= 0 and not 'Top Wall' in self.currentlyColliding or self.rect.top <= 480 and self.rect.left >= 0 and self.rect.right <= 480 and not 'Top Wall' in self.currentlyColliding or self.rect.top <= 480 and self.rect.left >= 960 and self.rect.right <= 1440 and not 'Top Wall' in self.currentlyColliding:
            self.currentlyColliding.append('Top Wall')
            self.velocity[1] *= -1
            return True
        if self.rect.top > 0 and 'Top Wall' in self.currentlyColliding or self.rect.top > 480 and 'Top Wall' in self.currentlyColliding:
            if 'Top Wall' in self.currentlyColliding:
                self.currentlyColliding.remove('Top Wall')
        if self.rect.bottom >= res[1] and not 'Bottom Wall' in self.currentlyColliding or self.rect.bottom >= 960 and self.rect.left >= 0 and self.rect.right <= 480 and not 'Bottom Wall' in self.currentlyColliding or self.rect.bottom >= 960 and self.rect.left >= 960 and self.rect.right <= 1440 and not 'Bottom Wall' in self.currentlyColliding:
            self.currentlyColliding.append('Bottom Wall')
            self.velocity[1] *= -1
            return True
        if self.rect.bottom <= res[1] and 'Bottom Wall' in self.currentlyColliding or self.rect.bottom < 960 and 'Bottom Wall' in self.currentlyColliding:
            if 'Bottom Wall' in self.currentlyColliding:
                self.currentlyColliding.remove('Bottom Wall')

        return False

    def shift(self, change):
        self.prevpos = self.position.copy()

        self.position += change
        try:
            self.rect.center = tuple(round(x) for x in self.position)
        except:
            print(self.position)

    def updatePosition(self, milli):
        self.shift(self.velocity * milli / 1000)

    def updateProperties(self):
        self.speed = np.sqrt((self.velocity ** 2).sum())

        # For inspection only
        self.momentum = self.mass * self.velocity
        self.KE = 0.5 * self.mass * self.speed ** 2

# SETTINGS

X, Y = (1440, 1920)  # Resolution of display window

edges = 50  # Number of initial particles

number_of_smallgons = 32  # Layers of polygon for fractal-like look
dark = (0, 0, 0)  # Dark colour of smallgons (fades from dark to light)
light = (191, 127, 255)  # Light colour of smallgons
background_colour = (0, 0, 0)

particle_radius = 15  # pixels
particle_speed = 300  # pixels per second

boxes = 4  # For optimising collision checks (number of rows and columns)
show_boxes = True
checks = 1  # Number of in-between-frames collision checks
count = 0
check = True
def new_polygon(biggon, ratio):
    """
    Given a polygon (biggon), this function returns the coordinates of
    the smaller polygon whose corners split the edges of the biggon by
    the given ratio.
    """
    smallgon = []
    L = len(biggon)
    
    for i in range(L):
        new_vertex = (biggon[i][0] *ratio + biggon[(i+1)%L][0] *(1-ratio),
                      biggon[i][1] *ratio + biggon[(i+1)%L][1] *(1-ratio), )
        smallgon.append(new_vertex)
        
    return tuple(smallgon)

def refresh_boxes():
    '''
    Just a macro for adjusting the number of boxes.
    Uses global variables.
    '''
    BoxesGroup.empty()
    width = round(X/boxes)
    height = round(Y/boxes)
    for r in range(boxes):
        for c in range(boxes):
            box = pygame.sprite.Sprite()
            box.rect = pygame.Rect((r*width, c*height), (width, height))
            BoxesGroup.add(box)
            
# Initialise Display
screen = pygame.Surface((1440, 1920))
screen2 = pygame.display.set_mode((480, 640))
pygame.display.set_caption("Collisions and Polygons | FPS: ")

# Initialise global variables
the_ratio = 0.0

ParticlesGroup = pygame.sprite.Group()
BoxesGroup = pygame.sprite.Group()
refresh_boxes()

clock = pygame.time.Clock()

# For arranging particles in a circle
big_polygon = [(X//2+Y//3*cos(radians(t)),Y//2+Y//3*sin(radians(t)))
           for t in np.arange(0, 360, 360/edges)]
for i in range(len(big_polygon)):
    if big_polygon[i][0] < 480 and big_polygon[i][1] < 480 or big_polygon[i][0] < 480 and big_polygon[i][1] > 960:
        big_polygon[i] = (500, big_polygon[i][1])
    if big_polygon[i][0] > 960 and big_polygon[i][1] < 480 or big_polygon[i][0] > 960 and big_polygon[i][1] > 960:
        big_polygon[i] = (900, big_polygon[i][1])
polygon_sprite_track = []  # Ordering the particles (for polygon drawing)

# Spawn particles
for i, eachC in enumerate(big_polygon):
    particle = Particle(1, particle_radius, (255,255,255),
                        np.array(eachC),
                        np.array(toCartesian(particle_speed, [t for t in np.arange(0, 360, 360/edges)][-i])))
    ParticlesGroup.add(particle)
    polygon_sprite_track.append(particle)

rects = [(480, 0), (480, 480), (480, 960), (480, 1440), (0, 480), (960, 480)]
names = [r"up.bmp", r"front.bmp", r"down.bmp", r"back.bmp", r"left.bmp", r"right.bmp"]
if sys.platform == "win32":
    import ctypes.wintypes

    CSIDL_PERSONAL = 5
    SHGFP_TYPE_CURRENT = 0

    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    sides = os.path.join(buf.value, r"WOWCube\sides")
else:
    sides = os.path.expanduser('~/OneDrive/Documents/WOWCube/sides')
## MAIN GAME LOOP ##
while True:
    milli = clock.tick()
    fps = clock.get_fps()
    
    mpos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    events = pygame.event.get()

    for e in events:
        # Quitting the game
        if e.type == QUIT:
            pygame.quit()
            sys.exit()

    # Set Background
    screen.fill(background_colour)
    
    # Collision with each other (by Boxes)
    by_box = pygame.sprite.groupcollide(BoxesGroup, ParticlesGroup, 0, 0)
    for eachBox in by_box:
        for eachP in combinations(by_box[eachBox], 2):
            eachP[0].testParticleCollision(eachP[1])
    
    # Update particles then draw to screen
    for eachP in ParticlesGroup:
        # Collision with wall (sophisticated, to counter big lag)
        eachP.testWallCollision(screen.get_size())
        
        # Move particles
        eachP.updatePosition(milli)
        screen.blit(eachP.image, eachP.rect)

    # Increase the_ratio
    the_ratio += 0.1 *milli/1000
    the_ratio = the_ratio % 1
    
    # Find corners of the big polygon (connecting the particles together)
    for i, eachParticle in enumerate(polygon_sprite_track):
        big_polygon[i] = tuple(int(each) for each in eachParticle.position)

    # Get coordinates of the small polygons
    smallgons = [big_polygon]
    for i in range(number_of_smallgons):
        smallgons.append(new_polygon(smallgons[i], the_ratio))

    # Draw the small polygons on the screen
    # pygame.draw.aalines(surface, color, closed, points, width=1)
    for i, each in enumerate(smallgons):
        colour = (int(dark[0]+(light[0]-dark[0])*sqrt(-~i/len(smallgons))),
                  int(dark[1]+(light[1]-dark[1])*sqrt(-~i/len(smallgons))),
                  int(dark[2]+(light[2]-dark[2])*sqrt(-~i/len(smallgons)))),
        int_coors = [(round(coor[0]), round(coor[1])) for coor in each]
        r = light[0]
        g = light[1]
        b = light[2]
        if r + 5 >= 230:
            check = False
        if g + 5 >= 230:
            check = False
        if b + 5 >= 230:
            check = False
        if r - 5 <= 30 or b - 5 <= 30 or g - 5 <= 30:
            check = True
        if count == 10:
            if check == True:
                light = (r + randint(0, 5), g + randint(0, 5), b + randint(0, 5))
            else:
                light = (r - randint(0, 5), g - randint(0, 5), b - randint(0, 5))
            count = 0
        count += 1
        try:
            pygame.draw.aalines(screen, colour, True, int_coors, 1)
        except:
            pass

    # Draw Boxes for collision checks
    if show_boxes:
        for i in range(1, boxes):
            pygame.draw.line(screen, (127, 0, 0),
                             [round(i*X/(boxes - 1)), 0],
                             [round(i*X/(boxes - 1)), Y],
                             1)
            pygame.draw.line(screen, (127, 0, 0),
                             [0, round(i*Y/boxes)],
                             [X, round(i*Y/boxes)],
                             1)
    for i, j in zip(rects, names):
        rect = pygame.Rect(i[0], i[1], 480, 480)
        screenshot = screen.subsurface(rect)
        if j == r"back.bmp":
            screenshot = pygame.transform.rotate(screenshot, 180)
        try:
            pygame.image.save(screenshot, os.path.join(sides, j))
        except:
            pass
    scaled = pygame.transform.scale(screen, screen2.get_size())
    screen2.blit(scaled, (0, 0))
    # Update Display
    pygame.display.flip()

    # Update caption, show FPS
    pygame.display.set_caption("Collisions and Polygons | " +
                               "FPS: " + str(round(fps,3))
                               )
