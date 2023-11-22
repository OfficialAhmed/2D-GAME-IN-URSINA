from ursina import Entity, Audio
from ursina import time as Time
from ursina import Ursina, Entity, Keys, Sprite, Audio

from Scripts.World import Scene
from Scripts.Characters import Character

from random import choice as Randomize

app = Ursina()

atmosphere = Audio("Assets/Sound/atmosphere.mp3", loop=True)
atmosphere.volume = 0.9

scene = Scene(Sprite=Sprite)
character = Character(
    Entity(
        model="quad",
        scale=(3.8, 1.8),
        position=(-6, -2.3),
        always_on_top=True,
    )
)

ambient_sound = (
    Audio(f"Assets/Sound/Zombie/00.mp3", False),
    Audio(f"Assets/Sound/Zombie/01.mp3", False),
    Audio(f"Assets/Sound/Zombie/02.mp3", False)
)
###############################################
#       ENGINE AUTO INVOKED METHODS
###############################################


def update():
    global ambient_sound

    character.elapsed_frames += Time.dt
    character.last_fire_frame += Time.dt
    character.elapsed_loop_duration += Time.dt

    character.update()

    if character.position_on_origin():
        scene.update()

    # EVERY 20 UNITS TRAVELED GENERATE RANDOM ZOMBIE SOUND
    if scene.ground.x % 20 <= 0.1:
        Randomize(ambient_sound).play()


def input(key):

    match key:

        case Keys.right_arrow:
            character.state = "run"
            character.direction = "Right"

        case Keys.right_arrow_up:
            character.state = "idle"

        case Keys.left_arrow:
            character.state = "run"
            character.direction = "Left"

        case Keys.left_arrow_up:
            character.state = "idle"

        case "space":

            # COOLDOWN FIRING
            if (character.last_fire_frame) >= character.fire_cooldown:

                # CANNOT FIRE WHILE RELOADING
                if character.state != "reload":

                    character.state = "fire"
                    character.last_fire_frame = 0
                    character.is_gun_triggered = True


app.run()
