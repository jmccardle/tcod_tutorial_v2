from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

import tcod.event

import game.actions

if TYPE_CHECKING:
    import game.engine

# Part 10 refactoring: ActionOrHandler type
ActionOrHandler = Union[game.actions.Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""


MOVE_KEYS = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    # Vi keys.
    tcod.event.KeySym.H: (-1, 0),
    tcod.event.KeySym.J: (0, 1),
    tcod.event.KeySym.K: (0, -1),
    tcod.event.KeySym.L: (1, 0),
    tcod.event.KeySym.Y: (-1, -1),
    tcod.event.KeySym.U: (1, -1),
    tcod.event.KeySym.B: (-1, 1),
    tcod.event.KeySym.N: (1, 1),
}


# Part 10 refactoring: BaseEventHandler
class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, game.actions.Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.console.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[game.actions.Action]:
        raise SystemExit()


class EventHandler(BaseEventHandler):
    def __init__(self, engine: game.engine.Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed.
            return MainGameEventHandler(self.engine)  # Return to the main handler.
        return self
    
    def handle_action(self, action: Optional[game.actions.Action]) -> bool:
        """Handle actions returned from event methods.
        
        Returns True if the action will advance a turn.
        """
        if action is None:
            return False
        
        action.perform()
        return True

    def on_render(self, console: tcod.console.Console) -> None:
        self.engine.render(console)


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[game.actions.Action] = None

        key = event.sym

        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = game.actions.MovementAction(player, dx, dy)

        elif key == tcod.event.KeySym.ESCAPE:
            action = game.actions.EscapeAction(player)

        # No valid key was pressed
        return action