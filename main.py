import time
from ursina import Ursina, Sprite, Entity, Keys
from ursina import time as Time

from Scripts.Characters import Character
from Scripts.World import Scene

app = Ursina()
scene = Scene()

#########################
#       STAGE INIT
#########################
stage = scene.stage_1()
sky = Sprite(
    stage.get("bg"),
    scale=(0, 4),
    position=(0, 0.7, 0)
)

ground = Sprite(
    stage.get("fg"),
    scale=(0, 2.1),
    position=(3.3, -1.5, 0),
    always_on_top=True
)

#########################
#       ENTITES INIT
#########################
character = Character(
    Entity(
        model="quad",
        scale=(3.8, 1.8),
        position=(-6, -1.6),
        always_on_top=True,
    ),
    sky,
    ground
)


###############################################
#       ENGINE AUTO INVOKED METHODS
###############################################

def update():
    character.elapsed_frames += Time.dt
    character.last_fire_frame += Time.dt
    character.elapsed_loop_duration += Time.dt

    character.animate()


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
                character.state = "fire"
                character.is_gun_triggered = True
                character.last_fire_frame = 0


app.run()
