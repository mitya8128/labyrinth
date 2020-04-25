"""
code for jumping_caves arcade (https://mitya8128.itch.io/jumping-caves)
based heavily on some of the examples from arcade.academy website
"""

import random
import arcade
import timeit
import time
import os

from pyo import*
from tkinter import*

def generate_melody():

    s = Server()
    s.boot()
    s.start()
    mod = Sine(freq=50, mul=50)
    mod2 = Sine(freq=100, mul=50)

    t = CosTable([(0, 0), (100, 1), (500, .3), (8191, 0)])
    beat = Beat(time=.125, taps=16, w1=[90, 80], w2=50, w3=35, poly=1).play()  # try taps=10 and larger poly
    trmid = TrigXnoiseMidi(beat, dist=12, mrange=(60, 96))
    trhz = Snap(trmid, choice=[0, 2, 3, 5, 7, 8, 10], scale=1)
    tr2 = TrigEnv(beat, table=t, dur=beat['dur'], mul=beat['amp'])

    mod = Sine(freq=50, mul=50)
    mod2 = Sine(freq=100, mul=50)

    a = Sine(freq=trhz + mod2, mul=tr2 * 0.2).out()
    s.gui(locals())

# Sprite scaling.
SPRITE_SCALING = 0.135
SPRITE_SIZE = 128 * SPRITE_SCALING
COIN_SCALING = 0.25

# How big the grid is
GRID_WIDTH = 400
GRID_HEIGHT = 300

# Parameters for cellular automata
# CHANCE_TO_START_ALIVE = 0.4  # initially 0.4
# DEATH_LIMIT = 3  # initially 3
# BIRTH_LIMIT = 4  # initially 4
# NUMBER_OF_STEPS = 4  # initially 4

# Physics
MOVEMENT_SPEED = 3  # initially 3
JUMP_SPEED = 18  # optimally 12
GRAVITY = 0.5  # initially 0.5

# How close the player can get to the edge before we scroll.
VIEWPORT_MARGIN = 300

# How big the window is
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Procedural Caves"
# If true, rather than each block being a separate sprite, blocks on rows
# will be merged into one sprite.
MERGE_SPRITES = False

# wallsprites
yellow = ":resources:images/tiles/grassCenter.png"
blue = ":resources:images/tiles/dirtCenter.png"

size = {'small':'small','medium':'medium', 'big':'big'}

def create_grid(width, height):
    """ Create a two-dimensional grid of specified size. """
    return [[0 for _x in range(width)] for _y in range(height)]


def initialize_grid(grid, CHANCE_TO_START_ALIVE):
    """ Randomly set grid locations to on/off based on chance. """
    height = len(grid)
    width = len(grid[0])
    for row in range(height):
        for column in range(width):
            if random.random() <= CHANCE_TO_START_ALIVE:
                grid[row][column] = 1


def count_alive_neighbors(grid, x, y):
    """ Count neighbors that are alive. """
    height = len(grid)
    width = len(grid[0])
    alive_count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            neighbor_x = x + i
            neighbor_y = y + j
            if i == 0 and j == 0:
                continue
            elif neighbor_x < 0 or neighbor_y < 0 or neighbor_y >= height or neighbor_x >= width:
                # Edges are considered alive. Makes map more likely to appear naturally closed.
                alive_count += 1
            elif grid[neighbor_y][neighbor_x] == 1:
                alive_count += 1
    return alive_count


def do_simulation_step(old_grid, DEATH_LIMIT, BIRTH_LIMIT):
    """ Run a step of the cellular automaton. """
    height = len(old_grid)
    width = len(old_grid[0])
    new_grid = create_grid(width, height)
    for x in range(width):
        for y in range(height):
            alive_neighbors = count_alive_neighbors(old_grid, x, y)
            if old_grid[y][x] == 1:
                if alive_neighbors < DEATH_LIMIT:
                    new_grid[y][x] = 0
                else:
                    new_grid[y][x] = 1
            else:
                if alive_neighbors > BIRTH_LIMIT:
                    new_grid[y][x] = 1
                else:
                    new_grid[y][x] = 0
    return new_grid


portal_sprite = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png", SPRITE_SCALING)

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=True)

        # Set the working directory
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.view_bottom = 0
        self.view_left = 0
        self.draw_time = 0
        self.processing_time = 0
        self.physics_engine = None
        self.game_over = False
        self.score = 0
        self.end_map_y = (GRID_HEIGHT * SPRITE_SIZE) + 10
        self.down_map = -300
        self.reload = False
        self.flag = None


        self.grid = None
        self.wall_list = None
        self.player_list = None
        self.player_sprite = None
       # self.portal_sprite = None
        self.coin_list = None
        #self.portal_list = None

        #global SPRITE_SCALING    #if it declare global strange ungluing of tiles
        # self.set_update_rate(1/55)    # for mac os

        arcade.set_background_color(arcade.color.BLACK)


    # setting up labyrinth characterstics
    def setup(self, SPRITE_SCALING, COIN_SCALING,CHANCE_TO_START_ALIVE,NUMBER_OF_STEPS,DEATH_LIMIT,BIRTH_LIMIT,wall_sprite):
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.portal_list = arcade.SpriteList()
        self.game_over = False
        self.reload = False

        # Create cave system using a 2D grid
        self.grid = create_grid(GRID_WIDTH, GRID_HEIGHT)
        initialize_grid(self.grid, CHANCE_TO_START_ALIVE)
        for step in range(NUMBER_OF_STEPS):
            self.grid = do_simulation_step(self.grid, DEATH_LIMIT, BIRTH_LIMIT)

        # Create sprites based on 2D grid
        if not MERGE_SPRITES:
            # This is the simple-to-understand method. Each grid location
            # is a sprite.
            for row in range(GRID_HEIGHT):
                for column in range(GRID_WIDTH):
                    if self.grid[row][column] == 1:
                        wall = arcade.Sprite(wall_sprite, SPRITE_SCALING)
                        wall._set_alpha(254)  # set sprites visibility (0-invisible,255-opaque)
                        wall.center_x = column * SPRITE_SIZE + SPRITE_SIZE / 2
                        wall.center_y = row * SPRITE_SIZE + SPRITE_SIZE / 2
                        self.wall_list.append(wall)
        else:
            # if there are multiple cells in a row with a wall,  merge them into one sprite, with a
            # repeating texture for each cell. This reduces our sprite count.

            for row in range(GRID_HEIGHT):
                column = 0
                while column < GRID_WIDTH:
                    while column < GRID_WIDTH and self.grid[row][column] == 0:
                        column += 1
                    start_column = column
                    while column < GRID_WIDTH and self.grid[row][column] == 1:
                        column += 1
                    end_column = column - 1

                    column_count = end_column - start_column + 1
                    column_mid = (start_column + end_column) / 2

                    wall = arcade.Sprite(wall_sprite, SPRITE_SCALING,
                                         repeat_count_x=column_count)
                    wall.center_x = column_mid * SPRITE_SIZE + SPRITE_SIZE / 2
                    wall.center_y = row * SPRITE_SIZE + SPRITE_SIZE / 2
                    wall.width = SPRITE_SIZE * column_count
                    self.wall_list.append(wall)

        # Set up and place the portal
        global portal_sprite
        #self.portal_sprite = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png", SPRITE_SCALING)
        #self.portal_sprite.alpha = 255
        #self.portal_sprite._set_alpha(254)
        self.portal_list.append(portal_sprite)

        placed_portal = False
        while not placed_portal:

            # Randomly position
            portal_sprite.center_x = 500
            portal_sprite.center_y = self.end_map_y + random.randrange(10)

            # Are we in a wall?
            walls_hit = arcade.check_for_collision_with_list(portal_sprite, self.wall_list)
            if len(walls_hit) == 0:
                # Not in a wall! Success!
                placed_portal = True

        # loop that places coins on the map
        for x in range(128, 1250, 20):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
            # Boolean variable if we successfully placed the coin
            coin_placed_successfully = False
            # Keep trying until success
            while not coin_placed_successfully:
                coin.center_x = random.randrange(GRID_WIDTH * SPRITE_SIZE)
                coin.center_y = random.randrange(GRID_HEIGHT * SPRITE_SIZE)
                # See if the coin is hitting a wall
                wall_hit_list = arcade.check_for_collision_with_list(coin, self.wall_list)
                # See if the coin is hitting another coin
                coin_hit_list = arcade.check_for_collision_with_list(coin, self.coin_list)
                if len(wall_hit_list) == 0 and len(coin_hit_list) == 0:
                    # It is!
                    coin_placed_successfully = True

            self.coin_list.append(coin)


        # Set up the player
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                           SPRITE_SCALING)
        self.player_list.append(self.player_sprite)

        # Randomly place the player. If we are in a wall, repeat until we aren't.
        placed = False
        while not placed:

            # Randomly position
            self.player_sprite.center_x = 64 + random.randrange(100)
            self.player_sprite.center_y = 250 + random.randrange(100)

            # Are we in a wall?
            walls_hit = arcade.check_for_collision_with_list(self.player_sprite, self.wall_list)
            if len(walls_hit) == 0:
                # Not in a wall! Success!
                placed = True

        # Physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list, gravity_constant=GRAVITY)

    def on_draw(self):
        """ Render the screen. """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        # Draw the sprites
        self.wall_list.draw()
        self.player_list.draw()
        self.coin_list.draw()

        # Draw info on the screen

        # sprite_count = len(self.wall_list)
        # output = f"Sprite Count: {sprite_count}"
        # arcade.draw_text(output,
        #                 self.view_left + 20,
        #                 self.height - 20 + self.view_bottom,
        #                 arcade.color.WHITE, 16)

        # output = f"Drawing time: {self.draw_time:.3f}"
        # arcade.draw_text(output,
        #                 self.view_left + 20,
        #                 self.height - 40 + self.view_bottom,
        #                 arcade.color.WHITE, 16)

        # output = f"Processing time: {self.processing_time:.3f}"
        # arcade.draw_text(output,
        #                 self.view_left + 20,
        #                 self.height - 60 + self.view_bottom,
        #                 arcade.color.WHITE, 16)

        output = f"Coins: {self.score:.3f}"
        arcade.draw_text(output,
                         self.view_left + 20,
                         self.height - 37 + self.view_bottom,
                         arcade.color.WHITE, 16)

        output = "Do not fall into the deep!"
        arcade.draw_text(output,
                         self.view_left + 20,
                         self.height - 57 + self.view_bottom,
                         arcade.color.WHITE, 16)

        #output = f"Size: {self.flag:.3f}"
        arcade.draw_text(self.flag,
                         self.view_left + 20,
                         self.height - 77 + self.view_bottom,
                         arcade.color.WHITE, 16)

        if self.game_over:
            arcade.draw_text("Game Over", self.view_left + 500, self.view_bottom + 400, arcade.color.WHITE, 30)
            arcade.draw_text(f"Collected coins: {self.score:.3f}", self.view_left + 500, self.view_bottom + 350,
                             arcade.color.WHITE, 30)

        self.draw_time = timeit.default_timer() - draw_start_time

        if self.reload:
            arcade.draw_text("You failed!", self.view_left + 500, self.view_bottom + 400, arcade.color.WHITE, 30)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
        elif key == arcade.key.W:
            arcade.set_background_color(arcade.color.WINDSOR_TAN)
        elif key == arcade.key.B:
            arcade.set_background_color(arcade.color.BLACK)
        elif key == arcade.key.KEY_1:
            global SPRITE_SCALING
            SPRITE_SCALING = 0.120
            self.flag = str(size['small'])
        elif key == arcade.key.KEY_2:
            SPRITE_SCALING = 0.130
            self.flag = str(size['medium'])
        elif key == arcade.key.KEY_3:
            SPRITE_SCALING = 0.135
            self.flag = str(size['big'])
        elif key == arcade.key.R:
            self.setup(SPRITE_SCALING, COIN_SCALING,0.4,4,3,4,yellow)
            self.score = 0

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_resize(self, width, height):

        arcade.set_viewport(self.view_left,
                            self.width + self.view_left,
                            self.view_bottom,
                            self.height + self.view_bottom)

    def on_update(self, delta_time):
        """ Movement and game logic """

        start_time = timeit.default_timer()

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()

        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + WINDOW_WIDTH - VIEWPORT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + WINDOW_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        if changed:
            arcade.set_viewport(self.view_left,
                                self.width + self.view_left,
                                self.view_bottom,
                                self.height + self.view_bottom)

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time
        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.coin_list.update()

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
        # Game over event
        if self.player_sprite.center_y >= self.end_map_y:
            self.game_over = True
        # Falling event
        if self.player_sprite.center_y < self.down_map:
            self.reload = True
            time.sleep(5.0)
            self.setup(SPRITE_SCALING, COIN_SCALING,0.4,4,3,4,yellow)
            self.score = 0
        # Check for collision with portal
        if arcade.check_for_collision(self.player_sprite, portal_sprite):
            # self.setup_2(SPRITE_SCALING, COIN_SCALING)
            self.setup(SPRITE_SCALING, COIN_SCALING, 0.3, 4, 2, 4,blue)    # 0.3,4,1,4,blue  #0.29,4,1,4,yellow


def main():
    generate_melody()
    game = MyGame()
    game.setup(SPRITE_SCALING, COIN_SCALING,0.4,4,3,4,yellow)    # 0.4,4,3,4,yellow
    arcade.run()


if __name__ == "__main__":
    main()
