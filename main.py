from ursina import time as Time
from ursina import Ursina, Sprite, Audio

from Scripts.World import Scene
from Scripts.Characters import Player, Enemy
from Scripts.Interface import Ui

from random import choice as Randomize

app = Ursina()

atmosphere = Audio("Assets/Sound/atmosphere.mp3", loop=True)
atmosphere.volume = 0.9

ui = Ui(Sprite=Sprite)
scene = Scene(Sprite=Sprite)

player = Player(
    Sprite(
        collider="square",
        scale=(5, 2),
        position=(-6, -2.2),
        always_on_top=True,
    ),
    ui
)

enemy = Enemy(
    Sprite(
        collider="square",
        scale=(2.7, 1.9),
        position=(1, -2.25),
        always_on_top=True,
    ),
    ui
)

ambient_sound = (
    Audio(f"Assets/Sound/Zombie/00.mp3", False),
    Audio(f"Assets/Sound/Zombie/01.mp3", False),
    Audio(f"Assets/Sound/Zombie/02.mp3", False)
)

game_loop = True

###############################################
#       ENGINE AUTO INVOKED METHODS
###############################################


def update():
    global ambient_sound

    if game_loop:       # HANDLE GAME LOGIC

        player.elapsed_frames += Time.dt
        enemy.elapsed_frames += Time.dt

        # UPDATE CHARACTER
        player.last_fire_frame += Time.dt
        player.elapsed_loop_duration += Time.dt
        player.update()

        if player.position_on_origin():
            scene.update()

        # EVERY 20 UNITS TRAVELED GENERATE RANDOM ZOMBIE SOUND
        if scene.ground.x % 20 <= 0.1:
            Randomize(ambient_sound).play()

        # UPDATE ENEMIES
        enemy.update_ai()

    else:               # HANDLE MENUS UI
        pass


def input(key):
    global game_loop

    # _____ ENABLE/DISABLED GAME CONTROLLER
    if key == "p":

        player.state = "idle"

        if game_loop:   # PAUSE GAME
            game_loop = False
            ui.pause_menu.render()

        else:           # UNPAUSE GAME
            game_loop = True
            ui.pause_menu.destroy()

    # _____ CHANGE CONTROLLER
    if game_loop:       # GAME CONTROLLER ENABLED

        # HANDLE PLAYER CONTROLLER
        player.controller(key)

    else:               # GAME CONTROLLER DISABLED

        # HANDLE MENU CONTROLLERS
        if ui.pause_menu.is_enabled:
            game_loop = ui.pause_menu.controller(key)


app.run()
