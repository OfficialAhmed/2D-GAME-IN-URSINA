from ursina import time as Time
from ursina import Ursina, Sprite, Audio
from ursina import destroy as Destroy

from Scripts.World import Scene, Collidable
from Scripts.Characters import Player
from Scripts.Interface import Ui

from random import randint as Randint


app = Ursina()

atmosphere = Audio("Assets/Sound/atmosphere.mp3", loop=True, autoplay=False)
soundtrack = Audio("Assets/Sound/soundtrack.mp3", loop=True, autoplay=False)
atmosphere.volume = 0.9
soundtrack.volume = 0.0

ambient_sound = [
    Audio(f"Assets/Sound/Zombie/00.mp3", False),
    Audio(f"Assets/Sound/Zombie/01.mp3", False),
    Audio(f"Assets/Sound/Zombie/02.mp3", False)
]

ui = Ui(sprite=Sprite)
scene = Scene(Sprite=Sprite)
player = Player(
    Sprite(
        name="player",
        collider="box",
        scale=(5, 2),
        position=(0, -2.2),
        always_on_top=True,
    ),
    ui
)


game_loop = True

colliders = Collidable()
colliders.entities.append(player)

###############################################
#       ENGINE AUTO INVOKED METHODS
###############################################


def update():

    global ambient_sound

    if game_loop:       # HANDLE GAME LOGIC (FPS)

        for obj in colliders.entities:
            obj.elapsed_frames += Time.dt
            obj.update()

        # EVERY 20 UNITS TRAVELED GENERATE RANDOM ZOMBIE SOUND
        if player.entity.world_position_getter().x % 20 <= 0.1:
            ambient_sound[Randint(0, len(ambient_sound)-1)].play()

        # DESTROY FLAGGED ENTITIES IF AVAILABLE
        if colliders.flagged_delete:
            for collider in colliders.flagged_delete:
                Destroy(collider.entity)

            colliders.flagged_delete.clear()


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
