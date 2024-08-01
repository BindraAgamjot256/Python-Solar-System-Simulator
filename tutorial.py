import pygame
import math
import random
import time as t

pygame.init()

WIN = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Solar system simulator")

WIDTH, HEIGHT = 800, 800
VENUS = (255, 255, 255)
SUN = (255, 255, 0)
EARTH = (100, 149, 237)
MARS = (188, 39, 50)
MERCURY = (80, 78, 81)
JUPITER = (201, 144, 57)
URANUS = (173, 216, 230)
NEPTUNE = (0, 0, 139)
PLUTO = (139, 69, 19)
ERIS = (153, 153, 255)
SATURN = (255, 255, 102)
ASTEROID = (255, 50, 50)

FONT = pygame.font.SysFont("montserrat", 16)
FONT_LARGE = pygame.font.SysFont("montserrat", 24)

class Planet:
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 250 / AU
    TIMESTEP = 3600 * 24

    def __init__(self, x, y, radius, color, mass, name):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.name = name
        self.orbit = []
        self.sun = False
        self.asteroid = False
        self.distance_to_sun = 0
        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win, zoom, offset_x, offset_y):
        x = self.x * self.SCALE * zoom + WIDTH / 2 + offset_x
        y = self.y * self.SCALE * zoom + HEIGHT / 2 + offset_y
        radius = self.radius * zoom

        if len(self.orbit) > 2 and not(self.asteroid):
            updated_points = [(px * self.SCALE * zoom + WIDTH / 2 + offset_x,
                               py * self.SCALE * zoom + HEIGHT / 2 + offset_y)
                              for (px, py) in self.orbit]
            pygame.draw.lines(win, self.color, False, updated_points, 2)

        pygame.draw.circle(win, self.color, (int(x), int(y)), int(radius))

        if not self.sun:
            distance_text = FONT.render(f"{self.name}: {round((self.distance_to_sun / 149597870700), 2)} AU", True, VENUS)
            win.blit(distance_text, (x - distance_text.get_width() / 2, y - distance_text.get_height() / 2))

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

def generate_starry_background():
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((0, 0, 0))
    num_stars = 200
    for _ in range(num_stars):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.circle(bg, VENUS, (x, y), 2)
    return bg

def initialize_planets():
    sun = Planet(0, 0, 30, SUN, 1.98892e30, "Sun")
    sun.sun = True

    earth = Planet(-1 * Planet.AU, 0, 16, EARTH, 5.9742e24, "Earth")
    earth.y_vel = 29.783e3

    mars = Planet(-1.524 * Planet.AU, 0, 12, MARS, 6.39e23, "Mars")
    mars.y_vel = 24.077e3

    mercury = Planet(0.387 * Planet.AU, 0, 8, MERCURY, 3.30e23, "Mercury")
    mercury.y_vel = -47.4e3

    venus = Planet(0.723 * Planet.AU, 0, 14, VENUS, 4.8685e24, "Venus")
    venus.y_vel = -35.02e3

    jupiter = Planet(5.2 * Planet.AU, 0, 69, JUPITER, 1.898e27, "Jupiter")
    jupiter.y_vel = 13.07e3

    saturn = Planet(9.58 * Planet.AU, 0, 58, SATURN, 5.683e26, "Saturn")
    saturn.y_vel = 9.69e3

    uranus = Planet(19.22 * Planet.AU, 0, 25, URANUS, 8.681e25, "Uranus")
    uranus.y_vel = 6.81e3

    neptune = Planet(30.05 * Planet.AU, 0, 24, NEPTUNE, 1.024e26, "Neptune")
    neptune.y_vel = 5.43e3

    asteroids = []
    listPlanets = [mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, sun]

    def orbital_velocity(distance):
        return math.sqrt(sun.G * sun.mass / distance)

    for _ in range(250):
        distance_from_sun = random.uniform(2.2 * Planet.AU, 3.2 * Planet.AU)
        angle = random.uniform(0, 2 * math.pi)
        x = distance_from_sun * math.cos(angle)
        y = distance_from_sun * math.sin(angle)
        radius = random.uniform(4, 12)
        mass = random.uniform(1e19, 1e20)
        asteroid = Planet(x, y, radius, VENUS, mass, "")
        asteroid.sun = True
        asteroid.asteroid = True
        # Compute velocity for a stable orbit
        speed = random.choice([orbital_velocity(distance_from_sun),-orbital_velocity(distance_from_sun)])
        asteroid.x_vel = -speed * math.sin(angle)
        asteroid.y_vel = speed * math.cos(angle)
        
        asteroids.append(asteroid)
        
    listPlanets.extend(asteroids)
    return listPlanets


def handle_events():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        return 0, 10
    if keys[pygame.K_s]:
        return 0, -10
    if keys[pygame.K_a]:
        return 10, 0
    if keys[pygame.K_d]:
        return -10, 0
    return 0, 0

def main():
    run = True
    clock = pygame.time.Clock()
    zoom = 1.0
    zoom_speed = 0.1
    time_speed = 60
    is_paused = False

    offset_x, offset_y = 0, 0
    planets = initialize_planets()
    starry_background = generate_starry_background()

    while run:
        clock.tick(time_speed)
        WIN.blit(starry_background, (0, 0))

        dx, dy = handle_events()
        offset_x += dx
        offset_y += dy

        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            for i in planets:
                if i.TIMESTEP == 0:
                    i.TIMESTEP = 3600 * 24
                elif i.TIMESTEP == 3600 * 24:
                    i.TIMESTEP = 3600 * 12
                elif i.TIMESTEP == 3600 * 12:
                    i.TIMESTEP = 0
            t.sleep(1)

        if keys[pygame.K_f]:
            time_speed = 60 if time_speed == 60000 else time_speed * 10
            t.sleep(1)

        if not is_paused:
            for planet in planets:
                planet.update_position(planets)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoom *= (1 + zoom_speed)
                elif event.button == 5:
                    zoom /= (1 + zoom_speed)

        for planet in planets:
            planet.draw(WIN, zoom, offset_x, offset_y)

        time_text = FONT_LARGE.render(f"Speed: {time_speed // 60}x", True, VENUS)
        WIN.blit(time_text, (10, 10))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
