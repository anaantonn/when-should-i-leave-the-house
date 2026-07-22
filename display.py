import datetime
import math
import sys
import time as time_module

import pygame

import main


pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
x = screen.get_width()
y = screen.get_height()
clock = pygame.time.Clock()
running = True

white = (255, 255, 255)
black = (0, 0, 0)
gray = (180, 180, 180)
red = (220, 50, 50)

font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 20)
font_small = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 14)
line_height = font.get_height()

tram_img = pygame.image.load("images/tram.png").convert_alpha()
bus_img  = pygame.image.load("images/bus.png").convert_alpha()

tram_img_small = pygame.transform.scale(tram_img, (200, 100))
bus_img_small  = pygame.transform.scale(bus_img,  (200, 100))

busRect_1 = bus_img_small.get_rect(center=(x // 8, y // 4))
busRect_2 = bus_img_small.get_rect(center=(x // 8, (y // 4) * 3))
tramRect_1 = tram_img_small.get_rect(center=((x // 2) + (x // 8) + 10, y // 4))
tramRect_2 = tram_img_small.get_rect(center=((x // 2) + (x // 8) + 10, (y // 4) * 3))
bus3_x = x - 120
busRect_3 = bus_img_small.get_rect(center=(bus3_x, y // 2))

float_offset = 0.0
float_speed = 0.05
amplitude = 10

fetch_interval = 10
last_fetch = 0
station_data = {}

def draw_datetime():
    now = datetime.datetime.now()
    date_surface = font.render(now.strftime("%A %d-%m-%Y"), True, white)
    time_surface = font.render(now.strftime("%H:%M:%S"), True, white)

    screen.blit(date_surface, date_surface.get_rect(center=(x // 2, y // 8)))
    screen.blit(time_surface, time_surface.get_rect(center=(x // 2, y // 8 + line_height + 10)))

def draw_station_data(data):
    all_lines = []
    for station in data.values():
        all_lines.extend(station["lines"])

    trams = [l for l in all_lines if l["type"] == "TRAM" or l["suspended"]]
    buses = [l for l in all_lines if l["type"] == "BUS" and not l["suspended"]]

    tram_slots = [tramRect_1, tramRect_2]
    bus_slots  = [busRect_1, busRect_2, busRect_3]

    for i, line in enumerate(trams):
        if i >= len(tram_slots):
            break
        rect = tram_slots[i]
        draw_y = rect.centery - line_height
        draw_x = rect.right + 10

        name_s = font.render(line["name"], True, gray if line["suspended"] else line["color"])
        dir_s  = font_small.render("WARNING: Verifică InfoTB" if line["suspended"] else line["direction"], True, red if line["suspended"] else gray)

        screen.blit(name_s, (draw_x, draw_y))
        screen.blit(dir_s,  (draw_x, draw_y + line_height + 4))

        if not line["suspended"]:
            arr_s = font.render(line["arriving"], True, white)
            screen.blit(arr_s, (draw_x, draw_y + line_height + font_small.get_height() + 8))

    for i, line in enumerate(buses):
        if i >= len(bus_slots):
            break
        rect = bus_slots[i]
        draw_y = rect.centery - line_height
        draw_x = rect.left - 10

        name_s = font.render(line["name"], True, line["color"])
        dir_s  = font_small.render(line["direction"], True, gray)
        arr_s  = font.render(line["arriving"], True, white)

        screen.blit(name_s, (draw_x - name_s.get_width(), draw_y))
        screen.blit(dir_s,  (draw_x - dir_s.get_width(),  draw_y + line_height + 4))
        screen.blit(arr_s,  (draw_x - arr_s.get_width(),  draw_y + line_height + font_small.get_height() + 8))

def draw_floating_images():
        rects  = [tramRect_1, tramRect_2, busRect_1, busRect_2, busRect_3]
        phases = [0, math.pi, math.pi / 2, math.pi * 1.5, math.pi / 4]
        images = [tram_img_small, tram_img_small, bus_img_small, bus_img_small, bus_img_small]

        for img, rect, phase in zip(images, rects, phases):
            bob = int(math.sin(float_offset + phase) * amplitude)
            screen.blit(img, (rect.x, rect.y + bob))

while running:
    float_offset += float_speed

    now = time_module.time()
    if now - last_fetch >= fetch_interval:
        station_data = main.fetch_all_stations()
        last_fetch = now

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                pygame.quit()
                sys.exit()

    screen.fill(black)
    draw_datetime()
    draw_station_data(station_data)
    draw_floating_images()

    pygame.display.flip()
    clock.tick(60)
