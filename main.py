from ursina import time as Time
from ursina import Ursina, Entity, Keys, Sprite, Audio

from Scripts.World import Scene
from Scripts.Characters import Character

app = Ursina()

soundtrack = Audio("Assets/Sound/stage1.ogg", loop=True).play()

scene = Scene(Sprite=Sprite)
character = Character(
    Entity(
        model="quad",
        scale=(3.8, 1.8),
        position=(-6, -2.5),
        always_on_top=True,
    )
)

###############################################
#       ENGINE AUTO INVOKED METHODS
###############################################


def update():

    character.elapsed_frames += Time.dt
    character.last_fire_frame += Time.dt
    character.elapsed_loop_duration += Time.dt

    character.update()

    if character.position_on_origin():
        scene.update()


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
