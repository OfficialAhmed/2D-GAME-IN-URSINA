from ursina import Sprite, Audio, Keys, Text
from ursina import time as Time

from ursina import camera as Camera
from random import randint as Randint
from ursina import destroy as Destroy
from ursina import load_texture as LoadTexture

from .Resources import Chest
from .Common import Shared
from .World import Fps


class Character(Fps, Shared):

    def __init__(self) -> None:
        super().__init__()

        # OVERWRITTEN BY THE INSTANCE
        self.weapon:            Weapon = None
        self.entity:            Sprite = None
        self.frame:             dict = {}
        self.TEXTURE:           dict = {}
        self.TOTAL_TEXTURES:    dict = {}

        self.aiming_timer = 0               # TO HOLD DURATION OF THE AIMING FRAME
        self.is_gun_triggered = False       # TO DISABLE MULTIPLE SHOOTING

        self.SPEED = 1.7
        self.health = 100
        self.state = "idle"
        self.direction = "Right"

        self.fire_cooldown = 0.3
        self.hit_animation_frame = 0

        # DELAY BETWEEN EACH TEXTURE FRAME
        # SOME AFFECT THE STATE SPEED, OTHER AFFECT THE ANIMATION SPEED ONLY
        self.texture_delay = {
            "idle":         0.08,       # IDLE ANIMATION SPEED
            "run":          0.08,       # RUNNING ANIMATION SPEED
            "walk":         0.13,       # WALKING ANIMATION SPEED
            "fire":         0.03,       # FIRING SPEED
            "reload":       0.17,       # RELOADING SPEED
        }

    def update_animation_no_repeat(self, after_animation: str):
        """
            UPDATES THE TEXTURE IN ONE LOOP ONLY
        """

        if after_animation:     # ALLOW ANIMATION

            if self.elapsed_frames >= self.texture_delay.get(self.state):

                self.elapsed_frames = 0
                current_frame = self.frame.get(self.state)
                total_frames = self.TOTAL_TEXTURES.get(self.state) - 1

                if current_frame <= total_frames:        # MORE FRAMES LEFT TO ANIMATE

                    self.entity.texture = self.TEXTURE.get(
                        self.direction
                    ).get(self.state).get(current_frame)

                    self.frame[self.state] += 1

                else:                                   # REACHED LAST ANIMATION FRAME

                    # RESET CURRNET STATE FRAME COUNTER
                    self.frame[self.state] = 0
                    self.state = after_animation

    def update_animation_repeat(self):
        """
            UPDATES THE TEXTURE IN REPEAT MODE
        """

        # IF PASSED THE ANIMATION DURATION
        if self.elapsed_frames >= self.texture_delay.get(self.state):

            self.elapsed_frames = 0
            total_frames = self.TOTAL_TEXTURES.get(self.state)
            current_frame = self.frame.get(self.state)

            # CHANGE TEXTURE
            self.entity.texture = self.TEXTURE.get(
                self.direction
            ).get(self.state).get(current_frame)

            # LOOP ANIMATION FRAMES
            self.frame[self.state] = (current_frame + 1) % total_frames


class Weapon(Shared):

    # _____   CONSTANTS   ____________
    VELOCITY = 15           # BULLET STARTING SPEED

    def __init__(
        self,
        entity,
        capacity,
        total_ammo,
        total_ammo_mag,
        weapon_y_pos,
        max_range,
        power
    ) -> None:

        super().__init__()

        self.entity = entity

        self.bullets = []
        self.direction = "Right"

        self.power = power
        self.capacity = capacity
        self.max_range = max_range
        self.total_ammo = total_ammo
        self.weapon_y_pos = weapon_y_pos
        self.total_ammo_mag = total_ammo_mag

        self.shoot_sound = Audio("Assets/Sound/Gun/Shotgun/shoot.mp3", False)
        self.empty_sound = Audio("Assets/Sound/Gun/Shotgun/empty.mp3", False)
        self.reload_sound = Audio("Assets/Sound/Gun/Shotgun/reload.mp3", False)
        self.loaded_sound = Audio("Assets/Sound/Gun/Shotgun/loaded.mp3", False)

    def reload(self):

        # RELOAD IF SUFFICIENT AMMO AVAILABLE
        if self.total_ammo >= self.capacity:

            # RELOAD GUN
            self.total_ammo -= self.capacity
            self.total_ammo_mag = self.capacity

            # UPDATE AMMO ON SCREEN (UI)
            self.ui.update_ammo(self.total_ammo)
            self.ui.update_mag_capacity(self.total_ammo_mag)

    def spawn_bullet(self):

        # TRACK THE BULLET DATA TO ANIMATE INDIVIDUALLY
        self.bullets.append(
            {
                "direction":    self.direction,
                "speed":        self.VELOCITY,
                "bullet":       Sprite(
                    collider="box",
                    scale=0.1,
                    position=(
                        self.entity.x,
                        self.weapon_y_pos
                    ),
                    always_on_top=True,
                )
            }
        )

        self.total_ammo_mag -= 1
        self.ui.update_mag_capacity(self.total_ammo_mag)

    def is_bullet_collided(self, opponent: Character, bullet: Sprite, bullet_index: int) -> bool:

        # IF COLLISION DETECTED AND NOT COLLIDING WITH ITSELF
        if opponent.state != "dead":
            if opponent.entity.name != self.entity.name and bullet.intersects(opponent.entity):
                if bullet.x >= opponent.entity.position.x - 0.4:        # 0.4 DIFFERENCE FROM TEXTURE TO THE FRAME

                    # REMOVE BULLET
                    Destroy(bullet)
                    self.bullets.pop(bullet_index)

                    return True

        return False

    def animate_bullet(self):

        bullets: list[dict] = self.bullets.copy()

        for bullet_index, bullet_data in enumerate(bullets):

            speed = bullet_data["speed"]
            bullet = bullet_data["bullet"]

            # ANIMATE MOVEMENT
            if bullet_data["direction"] == "Left":
                speed *= -1

            bullet.x += speed * Time.dt

            # BULLET DISTANCE FROM CHARACTER REACHED MAX
            if abs(bullet.x - self.entity.x) >= self.max_range:
                Destroy(bullet)
                self.bullets.pop(bullet_index)

            # COLLISION DETECTION
            for entity_index, entity in enumerate(self.entities.copy()):

                if self.is_bullet_collided(entity, bullet_data["bullet"], bullet_index):

                    entity.hit(entity, entity_index)
                    break


class Player(Character):

    MAX_RANGE = 7           # BULLET DISTANCE
    SHOTGUN_POWER = 25
    WEAPON_Y_POS = -2.1
    SHOTGUN_CAPACITY = 4    # MAGAZINE CAPACITY
    VISIBLE_AREA = 13       # THE CAMERA FOV IN PIXELS
    TOTAL_AMMO = 20         # STARTING AMMO

    def __init__(self, entity: Sprite) -> None:
        super().__init__()

        self.TOTAL_TEXTURES = {
            "idle":     6,
            "run":      8,
            "fire":     12,
            "reload":   12,
            "aim":      1
        }

        self.TEXTURE = {
            "Right": {
                "aim":        {0: LoadTexture(f"Assets/Animation/Char/Attack/Fire/Right/0.png")},
                "run":        {i: LoadTexture(f"Assets/Animation/Char/Run/Right/{i}.png") for i in range(self.TOTAL_TEXTURES.get("run"))},
                "idle":       {i: LoadTexture(f"Assets/Animation/Char/Idle/Right/{i}.png") for i in range(self.TOTAL_TEXTURES.get("idle"))},
                "fire":       {i: LoadTexture(f"Assets/Animation/Char/Attack/Fire/Right/{i}.png") for i in range(self.TOTAL_TEXTURES.get("fire"))},
                "reload":     {i: LoadTexture(f"Assets/Animation/Char/Attack/Reload/Right/{i}.png") for i in range(self.TOTAL_TEXTURES.get("reload"))}
            },
            "Left": {
                "aim":        {0: LoadTexture(f"Assets/Animation/Char/Attack/Fire/Left/0.png")},
                "run":        {i: LoadTexture(f"Assets/Animation/Char/Run/Left/{i}.png") for i in range(self.TOTAL_TEXTURES.get("run"))},
                "idle":       {i: LoadTexture(f"Assets/Animation/Char/Idle/Left/{i}.png") for i in range(self.TOTAL_TEXTURES.get("idle"))},
                "fire":       {i: LoadTexture(f"Assets/Animation/Char/Attack/Fire/Left/{i}.png") for i in range(self.TOTAL_TEXTURES.get("fire"))},
                "reload":     {i: LoadTexture(f"Assets/Animation/Char/Attack/Reload/Left/{i}.png") for i in range(self.TOTAL_TEXTURES.get("reload"))}
            }
        }

        self.texture_delay["aim"] = 0.2

        # FRAMES COUNTER
        self.frame = {
            "idle":     0,
            "run":      0,
            "fire":     0,
            "reload":   0,
            "aim":      0
        }

        self.entity = entity

        self.ui.render_money(50)
        self.ui.render_armor(100)
        self.ui.render_health(self.health)
        self.ui.render_ammo(self.TOTAL_AMMO)
        self.ui.render_mag_capacity(self.SHOTGUN_CAPACITY)

        self.weapon = Weapon(
            entity=entity,
            max_range=self.MAX_RANGE,
            power=self.SHOTGUN_POWER,
            total_ammo=self.TOTAL_AMMO,
            capacity=self.SHOTGUN_CAPACITY,
            weapon_y_pos=self.WEAPON_Y_POS,
            total_ammo_mag=self.SHOTGUN_CAPACITY
        )

        self.chest = Chest()
        self.enemy: Enemy = Enemy      # WITHOUT INVOKING THE CLASS

        # DETERMINE WHETHER ANIMATION LOOP ENDED
        self.is_animating = lambda: (
            self.frame.get(self.state) != 0
        )
        self.timer = 0

    def controller(self, key):

        match key:

            case Keys.up_arrow:
                # TODO: ANIMATE JUMPING STATE
                self.entity.y += 1.2

            case Keys.right_arrow:
                self.state = "run"
                self.direction = "Right"

            case Keys.left_arrow:
                self.state = "run"
                self.direction = "Left"

            case Keys.right_arrow_up | Keys.left_arrow_up:
                self.state = "idle"

            case "space":

                # RESTRICT FIRING WHILE RELOADING
                if self.state != "reload":
                    self.state = "fire"
                    self.is_gun_triggered = True

            case "o":

                self.state = "idle"
                self.chest.open_at(self.entity.position.x)

    def pick_ammo(self, ammo):
        self.weapon.total_ammo += ammo
        self.ui.update_ammo(self.weapon.total_ammo)

    def popup(self, text) -> Text:
        """
            RENDER A TEXT ON TOP OF THE PLAYER. RETURN TEXT TO DESTROY LATER.
        """

        return self.ui.render_popup(
            text, 0, -0.15, 1
        )

    def generate_spwan_position(self, distance: int):
        """
            CALCULATES RANDOM X-AXIS PIXEL OFF-SCREEN
        """

        pixel_off_screen = self.entity.world_position_getter().x + self.VISIBLE_AREA
        return pixel_off_screen + Randint(1, distance)

    def update(self):
        """
            CHECKS THE STATE OF THE CHARACTER AND UPDATE THE ANIMATION
        """

        self.weapon.direction = self.direction
        self.weapon.animate_bullet()
        self.enemy.spawn(self, self.generate_spwan_position(50))
        self.enemy.despawn(self)
        self.chest.spawn(self.generate_spwan_position(20))
        self.chest.update()

        match self.state:

            case "idle":
                self.update_animation_repeat()

            case "run":
                self.update_animation_repeat()

                speed = self.SPEED * Time.dt
                if self.direction == "Left":
                    speed *= -1     # NEGATIVE VALUE

                self.entity.x += speed
                Camera.position += (speed, 0, 0)
                self.ui.update_ui_pos(speed)

            case "reload":
                self.update_animation_no_repeat(after_animation="aim")

                # RELOAD AMMO ONCE RELOADING-ANIMATION ENDED
                if self.weapon.total_ammo_mag != self.weapon.capacity:
                    if not self.is_animating():
                        self.weapon.loaded_sound.play()
                        self.weapon.reload()

            case "aim":

                self.entity.texture = self.TEXTURE.get(
                    self.direction).get("aim").get(0)

                # PAUSE ANIMATION FOR SOME TIME THEN BACK TO IDLE
                if self.aiming_timer >= 70 * Time.dt:
                    self.state = "idle"
                self.aiming_timer += Time.dt

            case "fire":

                self.aiming_timer = 0

                # FIRE A BULLET IF MAGAZINE NOT EMPTY
                if self.weapon.total_ammo_mag > 0:

                    # IF NO ANIMATION PLAYED, SPAWN ONE BULLET
                    if self.is_gun_triggered and not self.is_animating():
                        self.update_animation_no_repeat(after_animation="aim")
                        self.weapon.spawn_bullet()
                        self.weapon.shoot_sound.play()
                        self.is_gun_triggered = False

                # MAG IS EMPTY, RELOAD
                elif self.weapon.total_ammo >= self.weapon.capacity:
                    self.state = "reload"
                    self.weapon.reload_sound.play()

                # NO MORE AMMO, KEEP AIMING
                else:
                    self.state = "aim"
                    self.weapon.empty_sound.play()

                self.update_animation_no_repeat(after_animation="aim")


class Enemy(Character):

    def __init__(self, entity: Sprite, player) -> None:
        super().__init__()

        self.FOV = 3.5         # FIELD OF VIEW
        self.SPEED = 0.7       # MOVEMENT SPEED

        self.entity = entity
        self.player = player

        self.alert_sound = Audio(f"Assets/Sound/Soldier/alert.mp3", False)

        # ENEMY SPECIFIC TEXTURES DELAY
        self.texture_delay["hit"] = 0.07
        self.texture_delay["die"] = 0.22
        # NO ANIMATION, DOESNT AFFECT ANYTHING
        self.texture_delay["dead"] = 0
        self.texture_delay["shoot"] = 0.5
        self.texture_delay["fight"] = 0.5

        # FRAMES COUNTER
        self.frame = {
            "hit":  0,
            "idle": 0,
            "walk": 0,
            "die":  0
        }

        self.TOTAL_TEXTURES = {
            "idle":     7,
            "walk":     7,
            "hit":      3,
            "die":      4,
            "fight":    3,
            "shoot":    4,
            "aim":      1,
            "dead":     1
        }

        self.TEXTURE = {
            "Right": {
                "dead":       {0: LoadTexture(f"Assets/Animation/Soldier/Die/Right/3.png")},
                "aim":        {0: LoadTexture(f"Assets/Animation/Soldier/Attack/Fire/Right/0.png")},
                "hit":        {i: LoadTexture(f"Assets/Animation/Soldier/Hit/Right/{i}.png") for i in range(self.TOTAL_TEXTURES.get("hit"))},
                "die":        {i: LoadTexture(f"Assets/Animation/Soldier/Die/Right/{i}.png") for i in range(self.TOTAL_TEXTURES.get("die"))},
                "idle":       {i: LoadTexture(f"Assets/Animation/Soldier/Idle/Right/{i}.png") for i in range(self.TOTAL_TEXTURES.get("idle"))},
                "walk":       {i: LoadTexture(f"Assets/Animation/Soldier/Walk/Right/{i}.png") for i in range(self.TOTAL_TEXTURES.get("walk"))}
            },

            "Left": {
                "dead":       {0: LoadTexture(f"Assets/Animation/Soldier/Die/Left/3.png")},
                "aim":        {0: LoadTexture(f"Assets/Animation/Soldier/Attack/Fire/Left/0.png")},
                "hit":        {i: LoadTexture(f"Assets/Animation/Soldier/Hit/Left/{i}.png") for i in range(self.TOTAL_TEXTURES.get("hit"))},
                "die":        {i: LoadTexture(f"Assets/Animation/Soldier/Die/Left/{i}.png") for i in range(self.TOTAL_TEXTURES.get("die"))},
                "idle":       {i: LoadTexture(f"Assets/Animation/Soldier/Idle/Left/{i}.png") for i in range(self.TOTAL_TEXTURES.get("idle"))},
                "walk":       {i: LoadTexture(f"Assets/Animation/Soldier/Walk/Left/{i}.png") for i in range(self.TOTAL_TEXTURES.get("walk"))}
            }
        }

        self.weapon = Weapon(
            power=20,
            capacity=5,
            max_range=5,
            total_ammo=10,
            entity=entity,
            total_ammo_mag=2,
            weapon_y_pos=(1, -1),
        )

        # AI SPECIFIC DATA
        self.frames_per_state = 4       # FRAMES LIMIT TO CHANGE STATE
        self.ai_elapsed_frames = 0      # HOLDS FPS FOR THE AI MOVEMENT
        self.player_detected = False

    def update_ai(self):

        match self.state:
            case "hit" | "die" | "dead":
                return

        self.ai_elapsed_frames += Time.dt

        # CALCULATE THE DISTANCE BETWEEN THE PLAYER AND THE ENEMY
        if abs(self.player.entity.position.x - self.entity.x) <= self.FOV:

            # LOOK AT THE PLAYER
            self.state = "idle"
            self.direction = "Left" if self.entity.position.x > self.player.entity.position.x else "Right"
            self.player_detected = True

        else:
            self.player_detected = False

        # SOLDIER PATROLLING
        if self.ai_elapsed_frames >= self.frames_per_state:

            if not self.player_detected:

                # WHEN IDLING CHANGE NEXT PATROLLING DIRECTION
                if self.state == "idle":
                    self.direction = "Left" if self.direction == "Right" else "Right"
                    self.state = "walk"

                # STOP WALKING
                elif self.state == "walk":
                    self.state = "idle"

            self.ai_elapsed_frames = 0

        elif self.state == "walk":

            speed = self.SPEED * Time.dt
            if self.direction == "Left":
                speed *= -1

            self.entity.x += speed

    def hit(self, entity, entity_index, despawn=False):

        if despawn:
            self.flagged_delete.append(entity)
            self.entities.pop(entity_index)

        if self.health <= 0:
            self.state = "die"

        else:
            self.state = "hit"
            self.health -= self.player.SHOTGUN_POWER

    def spawn(self, pos):

        # MAKE SURE ALWAYS 3 ENEMIES IN THE WORLD
        if len(self.entities) <= 3:
            self.entities.append(
                Enemy(
                    Sprite(
                        name="soldier",
                        collider="box",
                        scale=(2.7, 1.9),
                        position=(pos, -2),
                        always_on_top=True,
                    ),
                    self
                )
            )

    def despawn(self):

        # DESPAWN ENEMIES LEFT THE SCREEN
        for index, enemy in enumerate(self.entities.copy()):
            if enemy.entity.name != "player":
                if enemy.entity.world_position_getter().x <= self.entity.world_position_getter().x - 5:
                    enemy.hit(enemy, index, despawn=True)

    def update(self):
        """
            CHECKS THE STATE OF THE ENEMY AND UPDATE THE ANIMATION
        """

        match self.state:

            case "idle" | "walk":   self.update_animation_repeat()
            case "hit":             self.update_animation_no_repeat(after_animation="idle")
            case "die":             self.update_animation_no_repeat(after_animation="dead")
            case "dead":            self.update_animation_no_repeat(after_animation=None)

        self.update_ai()
