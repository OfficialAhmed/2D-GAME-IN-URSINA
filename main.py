from ursina import Entity, Audio
from ursina import time as Time
from ursina import Ursina, Entity, Keys, Sprite, Audio

from Scripts.World import Scene
from Scripts.Characters import Character
from Scripts.Interface import Ui

from random import choice as Randomize

app = Ursina()

atmosphere = Audio("Assets/Sound/atmosphere.mp3", loop=True)
atmosphere.volume = 0.9

ui = Ui(Entity=Entity)
scene = Scene(Sprite=Sprite)
character = Character(
    Entity(
        model="quad",
        scale=(3.8, 1.8),
        position=(-6, -2.3),
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

        character.elapsed_frames += Time.dt
        character.last_fire_frame += Time.dt
        character.elapsed_loop_duration += Time.dt

        character.update()

        if character.position_on_origin():
            scene.update()

        # EVERY 20 UNITS TRAVELED GENERATE RANDOM ZOMBIE SOUND
        if scene.ground.x % 20 <= 0.1:
            Randomize(ambient_sound).play()

    else:               # HANDLE MENUS UI
        pass


def input(key):
    global game_loop

    # _____ ENABLE/DISABLED GAME CONTROLLER
    if key == "p":

        character.state = "idle"
        
        if game_loop:   # PAUSE GAME
            game_loop = False
            ui.pause_menu.render()

        else:           # UNPAUSE GAME
            game_loop = True
            ui.pause_menu.destroy()

    # _____ CHANGE CONTROLLER
    if game_loop:       # GAME CONTROLLER ENABLED

        # HANDLE PLAYER CONTROLLER
        character.controller(key)

    else:               # GAME CONTROLLER DISABLED

        # HANDLE MENU CONTROLLERS
        if ui.pause_menu.is_enabled:
            game_loop = ui.pause_menu.controller(key)


app.run()
