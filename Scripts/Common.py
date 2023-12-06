from .World import Screen
from .Interface import Ui


class Shared(Screen):
    """
        SHARABLE VARS. INIT ONCE ONLY
    """

    ui: Ui = None
    entities = []           # ENTITIES CAN BE CHECKED FOR COLLISION
    flagged_delete = []     # ENTITIES TO BE DELETED

    def __init__(self) -> None:
        super().__init__()

    def set_ui(self, ui):
        Shared.ui = ui
