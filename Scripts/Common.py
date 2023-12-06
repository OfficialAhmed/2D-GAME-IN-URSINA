from .World import Screen


class Shared(Screen):
    """
        SHARABLE VARS. INIT ONCE ONLY
    """

    ui = None
    scene = None

    entities = []           # ENTITIES CAN BE CHECKED FOR COLLISION
    flagged_delete = []     # ENTITIES TO BE DELETED

    def __init__(self) -> None:
        super().__init__()

    def set_ui(self, ui):
        Shared.ui = ui

    def set_scene(self, scene):
        Shared.scene = scene
