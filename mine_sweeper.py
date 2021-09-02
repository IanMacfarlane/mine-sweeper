import random
import pygame
import sys
from pygame.locals import *

fps = 30
grid_size = 15
cell_size = 50
window_size = grid_size * cell_size

# load assets
covered_image = pygame.image.load('covered.png')
uncovered_image = pygame.image.load('uncovered.png')
flagged_image = pygame.image.load('flagged.png')
one_image = pygame.image.load('1.png')
two_image = pygame.image.load('2.png')
three_image = pygame.image.load('3.png')
four_image = pygame.image.load('4.png')
five_image = pygame.image.load('5.png')
six_image = pygame.image.load('6.png')
seven_image = pygame.image.load('7.png')
eight_image = pygame.image.load('8.png')

# game over assets
mine_image = pygame.image.load('mine.png')
triggered_image = pygame.image.load('triggered.png')
incorrect_image = pygame.image.load('incorrect.png')

# initialize game variables

# track location of mines in grid
mine_locations = [[0 for i in range(grid_size)] for j in range(grid_size)]
first_click = True
game_over = False

# track player view of minefield that will be displayed
# contains: 'covered', 'uncovered', 'flagged', 'mine', int representing number of adjacent mines
mine_field = [['covered' for i in range(grid_size)] for j in range(grid_size)]
movement_tracker = [[0 for i in range(grid_size)] for j in range(grid_size)]


def game_loop(agent_locations):
    while True:
        process_input()

        if not game_over:
            for i in range(len(agent_locations)):
                agent_locations[i] = agent_move(agent_locations[i])

        render(agent_locations)
        fps_clock.tick(fps)


def process_input():
    global first_click
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                terminate()
        '''elif event.type == MOUSEBUTTONDOWN and not game_over:
            position = pygame.mouse.get_pos()

            # get x, y cell from position
            x = int(position[0]/cell_size)
            y = int(position[1]/cell_size)

            # if left click
            if event.button == 1:
                if first_click:
                    first_click = False
                    place_mines(x, y)
                uncover_cell(x, y)
            # if right click
            else:
                place_flag(x, y)'''


def agent_move(agent_location):
    # mine sweeper agent
    # TODO allow agent to guess

    # if adjacent mines
    if isinstance(mine_field[agent_location['y']][agent_location['x']], int):
        # if all adjacent mines have been flagged, uncover adjacent covered cells and remove adjacent mines
        if mine_field[agent_location['y']][agent_location['x']] == adjacent_flags(agent_location):
            uncover_adjacent(agent_location['x'], agent_location['y'])
        # compare number of adjacent mines to number of adjacent covered cells, if equal, flag adjacent covered cells
        if mine_field[agent_location['y']][agent_location['x']] == covered_adjacent(agent_location) + adjacent_flags(agent_location):
            flag_adjacent(agent_location)
        # if adjacent mines move along covered cells and mines right hand maze move
        if isinstance(mine_field[agent_location['y']][agent_location['x']], int):
            agent_location = follow_wall(agent_location)

    # if no adjacent mines and adjacent covered cells uncover adjacent covered cells
    elif mine_field[agent_location['y']][agent_location['x']] == 'uncovered' and covered_adjacent(agent_location) > 0:
        uncover_adjacent(agent_location['x'], agent_location['y'])
    # if no adjacent mines and no adjacent covered cells move up
    elif mine_field[agent_location['y']][agent_location['x']] == 'uncovered' and covered_adjacent(agent_location) == 0:
        agent_location = follow_wall(agent_location)

    return agent_location


def follow_wall(agent_location):

    movement_tracker[agent_location['y']][agent_location['x']] += 1
    if movement_tracker[agent_location['y']][agent_location['x']] % 10 == 0:
        agent_location['right_hand'] = 'down'

    if agent_location['right_hand'] == 'up':
        if agent_location['y'] == 0 or mine_field[agent_location['y'] - 1][agent_location['x']] == 'covered' or mine_field[agent_location['y'] - 1][agent_location['x']] == 'flagged':
            if agent_location['x'] != 0 and mine_field[agent_location['y']][agent_location['x'] - 1] != 'covered' and mine_field[agent_location['y']][agent_location['x'] - 1] != 'flagged':
                agent_location['x'] -= 1
            elif agent_location['y'] != grid_size - 1 and mine_field[agent_location['y'] + 1][agent_location['x']] != 'covered' and mine_field[agent_location['y'] + 1][agent_location['x']] != 'flagged':
                agent_location['y'] += 1
                agent_location['right_hand'] = 'left'
            else:
                agent_location['x'] += 1
                agent_location['right_hand'] = 'down'
        else:
            agent_location['y'] -= 1
            if agent_location['x'] != grid_size - 1 and (mine_field[agent_location['y']][agent_location['x'] + 1] == 'covered' or mine_field[agent_location['y']][agent_location['x'] + 1] == 'flagged'):
                agent_location['right_hand'] = 'right'

    elif agent_location['right_hand'] == 'left':
        if agent_location['x'] == 0 or mine_field[agent_location['y']][agent_location['x'] - 1] == 'covered' or mine_field[agent_location['y']][agent_location['x'] - 1] == 'flagged':
            if agent_location['y'] != grid_size - 1 and mine_field[agent_location['y'] + 1][agent_location['x']] != 'covered' and mine_field[agent_location['y'] + 1][agent_location['x']] != 'flagged':
                agent_location['y'] += 1
            elif agent_location['x'] != grid_size - 1 and mine_field[agent_location['y']][agent_location['x'] + 1] != 'covered' and mine_field[agent_location['y']][agent_location['x'] + 1] != 'flagged':
                agent_location['x'] += 1
                agent_location['right_hand'] = 'down'
            else:
                agent_location['y'] -= 1
                agent_location['right_hand'] = 'right'
        else:
            agent_location['x'] -= 1
            agent_location['right_hand'] = 'up'

    elif agent_location['right_hand'] == 'down':
        if agent_location['y'] == grid_size - 1 or mine_field[agent_location['y'] + 1][agent_location['x']] == 'covered' or mine_field[agent_location['y'] + 1][agent_location['x']] == 'flagged':
            if agent_location['x'] != grid_size - 1 and mine_field[agent_location['y']][agent_location['x'] + 1] != 'covered' and mine_field[agent_location['y']][agent_location['x'] + 1] != 'flagged':
                agent_location['x'] += 1
            elif agent_location['y'] != 0 and mine_field[agent_location['y'] - 1][agent_location['x']] != 'covered' and mine_field[agent_location['y'] - 1][agent_location['x']] != 'flagged':
                agent_location['y'] -= 1
                agent_location['right_hand'] = 'right'
            else:
                agent_location['x'] -= 1
                agent_location['right_hand'] = 'up'
        else:
            agent_location['y'] += 1
            agent_location['right_hand'] = 'left'

    elif agent_location['right_hand'] == 'right':
        if agent_location['x'] == grid_size - 1 or mine_field[agent_location['y']][agent_location['x'] + 1] == 'covered' or mine_field[agent_location['y']][agent_location['x'] + 1] == 'flagged':
            if agent_location['y'] != 0 and mine_field[agent_location['y'] - 1][agent_location['x']] != 'covered' and mine_field[agent_location['y'] - 1][agent_location['x']] != 'flagged':
                agent_location['y'] -= 1
            elif agent_location['x'] != 0 and mine_field[agent_location['y']][agent_location['x'] - 1] != 'covered' and mine_field[agent_location['y']][agent_location['x'] - 1] != 'flagged':
                agent_location['x'] -= 1
                agent_location['right_hand'] = 'up'
            else:
                agent_location['y'] += 1
                agent_location['right_hand'] = 'left'
        else:
            agent_location['x'] += 1
            #if agent_location['y'] == 0 and (mine_field[agent_location['y'] - 1][agent_location['x']] == 'covered' or mine_field[agent_location['y'] - 1][agent_location['x']] == 'flagged'):
            agent_location['right_hand'] = 'down'

    return agent_location


def adjacent_flags(agent_location):
    flags = 0
    if agent_location['y'] != 0 and mine_field[agent_location['y'] - 1][agent_location['x']] == 'flagged':
        flags += 1
    if agent_location['y'] != 0 and agent_location['x'] != grid_size - 1 and mine_field[agent_location['y'] - 1][agent_location['x'] + 1] == 'flagged':
        flags += 1
    if agent_location['x'] != grid_size - 1 and mine_field[agent_location['y']][agent_location['x'] + 1] == 'flagged':
        flags += 1
    if agent_location['y'] != grid_size - 1 and agent_location['x'] != grid_size - 1 and mine_field[agent_location['y'] + 1][agent_location['x'] + 1] == 'flagged':
        flags += 1
    if agent_location['y'] != grid_size - 1 and mine_field[agent_location['y'] + 1][agent_location['x']] == 'flagged':
        flags += 1
    if agent_location['y'] != grid_size - 1 and agent_location['x'] != 0 and mine_field[agent_location['y'] + 1][agent_location['x'] - 1] == 'flagged':
        flags += 1
    if agent_location['x'] != 0 and mine_field[agent_location['y']][agent_location['x'] - 1] == 'flagged':
        flags += 1
    if agent_location['y'] != 0 and agent_location['x'] != 0 and mine_field[agent_location['y'] - 1][agent_location['x'] - 1] == 'flagged':
        flags += 1
    return flags


def flag_adjacent(agent_location):
    if agent_location['y'] != 0 and mine_field[agent_location['y'] - 1][agent_location['x']] == 'covered':
        place_flag(agent_location['x'], agent_location['y'] - 1)
    if agent_location['y'] != 0 and agent_location['x'] != grid_size - 1 and mine_field[agent_location['y'] - 1][agent_location['x'] + 1] == 'covered':
        place_flag(agent_location['x'] + 1, agent_location['y'] - 1)
    if agent_location['x'] != grid_size - 1 and mine_field[agent_location['y']][agent_location['x'] + 1] == 'covered':
        place_flag(agent_location['x'] + 1, agent_location['y'])
    if agent_location['y'] != grid_size - 1 and agent_location['x'] != grid_size - 1 and mine_field[agent_location['y'] + 1][agent_location['x'] + 1] == 'covered':
        place_flag(agent_location['x'] + 1, agent_location['y'] + 1)
    if agent_location['y'] != grid_size - 1 and mine_field[agent_location['y'] + 1][agent_location['x']] == 'covered':
        place_flag(agent_location['x'], agent_location['y'] + 1)
    if agent_location['y'] != grid_size - 1 and agent_location['x'] != 0 and mine_field[agent_location['y'] + 1][agent_location['x'] - 1] == 'covered':
        place_flag(agent_location['x'] - 1, agent_location['y'] + 1)
    if agent_location['x'] != 0 and mine_field[agent_location['y']][agent_location['x'] - 1] == 'covered':
        place_flag(agent_location['x'] - 1, agent_location['y'])
    if agent_location['y'] != 0 and agent_location['x'] != 0 and mine_field[agent_location['y'] - 1][agent_location['x'] - 1] == 'covered':
        place_flag(agent_location['x'] - 1, agent_location['y'] - 1)


# returns number of adjacent covered cells
def covered_adjacent(agent_location):
    covered = 0
    if agent_location['y'] != 0 and mine_field[agent_location['y'] - 1][agent_location['x']] == 'covered':
        covered += 1
    if agent_location['y'] != 0 and agent_location['x'] != grid_size - 1 and mine_field[agent_location['y'] - 1][agent_location['x'] + 1] == 'covered':
        covered += 1
    if agent_location['x'] != grid_size - 1 and mine_field[agent_location['y']][agent_location['x'] + 1] == 'covered':
        covered += 1
    if agent_location['y'] != grid_size - 1 and agent_location['x'] != grid_size - 1 and mine_field[agent_location['y'] + 1][agent_location['x'] + 1] == 'covered':
        covered += 1
    if agent_location['y'] != grid_size - 1 and mine_field[agent_location['y'] + 1][agent_location['x']] == 'covered':
        covered += 1
    if agent_location['y'] != grid_size - 1 and agent_location['x'] != 0 and mine_field[agent_location['y'] + 1][agent_location['x'] - 1] == 'covered':
        covered += 1
    if agent_location['x'] != 0 and mine_field[agent_location['y']][agent_location['x'] - 1] == 'covered':
        covered += 1
    if agent_location['y'] != 0 and agent_location['x'] != 0 and mine_field[agent_location['y'] - 1][agent_location['x'] - 1] == 'covered':
        covered += 1
    return covered


def uncover_adjacent(x, y):
    if y != 0:
        uncover_cell(x, y-1)
    if y != 0 and x != grid_size - 1:
        uncover_cell(x+1, y-1)
    if x != grid_size - 1:
        uncover_cell(x+1, y)
    if y != grid_size - 1 and x != grid_size - 1:
        uncover_cell(x+1, y+1)
    if y != grid_size - 1:
        uncover_cell(x, y+1)
    if y != grid_size - 1 and x != 0:
        uncover_cell(x-1, y+1)
    if x != 0:
        uncover_cell(x-1, y)
    if y != 0 and x != 0:
        uncover_cell(x-1, y-1)


def place_mines(agent_locations):
    # randomly place mines throughout field not on cell x, y
    for y in range(len(mine_locations)):
        for x in range(len(mine_locations[y])):

            placeable = True
            for agent_location in agent_locations:
                if (x == agent_location['x'] and y == agent_location['y']) or (
                        x == agent_location['x'] and y == agent_location['y'] - 1) or (
                        x == agent_location['x'] + 1 and y == agent_location['y'] - 1) or (
                        x == agent_location['x'] + 1 and y == agent_location['y']) or (
                        x == agent_location['x'] + 1 and y == agent_location['y'] + 1) or (
                        x == agent_location['x'] and y == agent_location['y'] + 1) or (
                        x == agent_location['x'] - 1 and y == agent_location['y'] + 1) or (
                        x == agent_location['x'] - 1 and y == agent_location['y']) or (
                        x == agent_location['x'] - 1 and y == agent_location['y'] - 1):
                    placeable = False

            if placeable:
                if random.randint(1, 5) == 1:
                    mine_locations[y][x] = 1


def uncover_cell(x, y):
    if mine_field[y][x] == 'covered':
        # check for mine
        if mine_locations[y][x] == 1:
            set_game_over()
            mine_field[y][x] = 'triggered'
        else:
            # count number of adjacent mines
            mines = 0
            if y != 0 and mine_locations[y-1][x] == 1:
                mines += 1
            if y != 0 and x != grid_size - 1 and mine_locations[y-1][x+1] == 1:
                mines += 1
            if x != grid_size - 1 and mine_locations[y][x+1] == 1:
                mines += 1
            if y != grid_size - 1 and x != grid_size - 1 and mine_locations[y+1][x+1] == 1:
                mines += 1
            if y != grid_size - 1 and mine_locations[y+1][x] == 1:
                mines += 1
            if y != grid_size - 1 and x != 0 and mine_locations[y+1][x-1] == 1:
                mines += 1
            if x != 0 and mine_locations[y][x-1] == 1:
                mines += 1
            if y != 0 and x != 0 and mine_locations[y-1][x-1] == 1:
                mines += 1

            if mines == 0:
                mine_field[y][x] = 'uncovered'
                # if cell has no adjacent mines, recursively uncover all adjacent cells
                '''if y != 0:
                    uncover_cell(x, y-1)
                if y != 0 and x != grid_size - 1:
                    uncover_cell(x+1, y-1)
                if x != grid_size - 1:
                    uncover_cell(x+1, y)
                if y != grid_size - 1 and x != grid_size - 1:
                    uncover_cell(x+1, y+1)
                if y != grid_size - 1:
                    uncover_cell(x, y+1)
                if y != grid_size - 1 and x != 0:
                    uncover_cell(x-1, y+1)
                if x != 0:
                    uncover_cell(x-1, y)
                if y != 0 and x != 0:
                    uncover_cell(x-1, y-1)'''

            else:
                mine_field[y][x] = mines


def place_flag(x, y):
    if mine_field[y][x] == 'covered':
        mine_field[y][x] = 'flagged'
    elif mine_field[y][x] == 'flagged':
        mine_field[y][x] = 'covered'

    # check to see if every mine has been flagged
    game_won = True
    for y in range(len(mine_locations)):
        for x in range(len(mine_locations[y])):
            if mine_locations[y][x] == 1 and mine_field[y][x] != 'flagged':
                game_won = False
    if game_won:
        set_game_over()


def set_game_over():
    global game_over
    game_over = True
    # show all missed mines, and bad flags
    for y in range(len(mine_locations)):
        for x in range(len(mine_locations[y])):
            if mine_locations[y][x] == 1 and mine_field[y][x] != 'flagged':
                mine_field[y][x] = 'mine'

    for y in range(len(mine_field)):
        for x in range(len(mine_field[y])):
            if mine_field[y][x] == 'flagged' and mine_locations[y][x] != 1:
                mine_field[y][x] = 'incorrect'


def render(agent_locations):

    for y in range(len(mine_field)):
        for x in range(len(mine_field[y])):
            if mine_field[y][x] == 'covered':
                display_surf.blit(covered_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 'uncovered':
                display_surf.blit(uncovered_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 'flagged':
                display_surf.blit(flagged_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 1:
                display_surf.blit(one_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 2:
                display_surf.blit(two_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 3:
                display_surf.blit(three_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 4:
                display_surf.blit(four_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 5:
                display_surf.blit(five_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 6:
                display_surf.blit(six_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 7:
                display_surf.blit(seven_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 8:
                display_surf.blit(eight_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 'incorrect':
                display_surf.blit(incorrect_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 'mine':
                display_surf.blit(mine_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
            elif mine_field[y][x] == 'triggered':
                display_surf.blit(triggered_image, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))

    # draw agent
    for i in range(len(agent_locations)):
        pygame.draw.rect(display_surf, (255, 0, 0), pygame.Rect(agent_locations[i]['x'] * cell_size, agent_locations[i]['y'] * cell_size, cell_size, cell_size), 2)

    pygame.display.update()


def terminate():
    pygame.quit()
    sys.exit()


# initialize pygame
pygame.init()
fps_clock = pygame.time.Clock()
display_surf = pygame.display.set_mode((window_size, window_size))
basic_font = pygame.font.Font('freesansbold.ttf', 18)
pygame.display.set_caption('Mine Sweeper')

# initialize agent in random cell
agents = 5
agent_locations = []

for i in range(agents):

    cell_taken = True
    x = random.randint(0, grid_size - 1)
    y = random.randint(0, grid_size - 1)

    while cell_taken:
        cell_taken = False
        for agent_location in agent_locations:
            if x == agent_location['x'] and y == agent_location['y']:
                cell_taken = True
                x = random.randint(0, grid_size - 1)
                y = random.randint(0, grid_size - 1)

        if not cell_taken:
            print(str(x) + ', ' + str(y))
            agent_locations.append({'x': x, 'y': y, 'right_hand': 'up'})


place_mines(agent_locations)
for agent_location in agent_locations:
    uncover_cell(agent_location['x'], agent_location['y'])


game_loop(agent_locations)
