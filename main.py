from ursina import time as Time
from ursina import Ursina, Sprite, Audio, EditorCamera
from ursina import destroy as Destroy

from Scripts.World import Scene
from Scripts.Common import Shared
from Scripts.Interface import Ui
from Scripts.Characters import Player


from random import randint as Randint


app = Ursina()

atmosphere = Audio("Assets/Sound/atmosphere.mp3", loop=True)
soundtrack = Audio("Assets/Sound/soundtrack.mp3", loop=True)
soundtrack.volume = 0
atmosphere.volume = 0

# ambient_sound = [
#     Audio(f"Assets/Sound/Zombie/00.mp3", False),
#     Audio(f"Assets/Sound/Zombie/01.mp3", False),
#     Audio(f"Assets/Sound/Zombie/02.mp3", False)
# ]

shared = Shared()
scene = Scene(sprite=Sprite)
shared.set_scene(scene)
shared.set_ui(Ui(sprite=Sprite))
player = Player(
    Sprite(
        name="player",
        collider="box",
        scale=(5, 2),
        position=(0, -1.5),
        always_on_top=True,
    )
)
shared.entities.append(player)

game_loop = True
editor_camera = EditorCamera(enabled=False, ignore_paused=True)


###############################################
#       ENGINE AUTO INVOKED METHODS
###############################################


def update():

    # global ambient_sound

    if game_loop:       # HANDLE GAME LOGIC (FPS)

        for obj in shared.entities:
            obj.elapsed_frames += Time.dt
            obj.update()

        scene.update(player.entity.get_position().x)
        scene.apply_gravity(scene, shared.entities)

        # EVERY 20 UNITS TRAVELED GENERATE RANDOM ZOMBIE SOUND
        # if player.entity.world_position_getter().x % 20 <= 0.1:
        #     ambient_sound[Randint(0, len(ambient_sound)-1)].play()

        # DESTROY FLAGGED ENTITIES IF AVAILABLE
        if shared.flagged_delete:

            for collider in shared.flagged_delete:

                if isinstance(collider, Sprite):
                    Destroy(collider)           # RESOURCES
                else:
                    Destroy(collider.entity)    # ENEMY / PLAYER

            shared.flagged_delete.clear()


def input(key):

    global game_loop

    # _____ ENABLE/DISABLED GAME CONTROLLER
    if key == "p":

        player.state = "idle"

        if game_loop:   # PAUSE GAME
            game_loop = False
            shared.ui.pause_menu.render()

        else:           # UNPAUSE GAME
            game_loop = True
            shared.ui.pause_menu.destroy()

    elif key == "tab":
        editor_camera.enabled = not editor_camera.enabled

    # _____ CHANGE CONTROLLER
    if game_loop:       # GAME CONTROLLER ENABLED

        # HANDLE PLAYER CONTROLLER
        player.controller(key)

    else:               # GAME CONTROLLER DISABLED

        # HANDLE MENU CONTROLLERS
        if shared.ui.pause_menu.is_enabled:
            game_loop = shared.ui.pause_menu.controller(key)


app.run()
