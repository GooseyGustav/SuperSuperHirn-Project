from abc import ABC, abstractmethod

from app.ports.driven.for_getting_moves.for_getting_codebreaker_move import ForGettingCodebreakerMove
from app.ports.driven.for_getting_moves.for_getting_codemaker_move import ForGettingCodemakerMove


class ForAssemblingPlayers(ABC):
    """The port for assembling players. Requests one instantiated adapter per role
    (one Codemaker, one Codebreaker).
    Note:
        - Implemented by `Matchmaker` (src/startup).
        - Implemented for testing App by `FakeMatchmaker` (src/startup).
        - Passed to App by `SupersuperhirnRunner` (src/startup).
        - Methods called by: `GameManager` (src/app/game_management).
    """

    @abstractmethod
    def assemble_players(self, config: dict) -> tuple[ForGettingCodemakerMove, ForGettingCodebreakerMove]:
        """Assembles the players for the current game configuration by turning
        the current `config` selection into the round's two player adapters.

        Args:
            config: the current game config as a dict. Shape:
                {
                    "gamemode":            str,
                    "user_role":           str,
                    "network_enabled":     bool,
                    "countdown_millis":    int,
                    "delay_millis":        int,
                    "number_of_positions": int,   # fixed constant, app-injected (5) (board size/code length)
                    "number_of_colors":    int,   # fixed constant, app-injected (8)
                    "network_address":     str,  #  url or "<ip>:<port>" only for network game; None if local
                    "gamer_id":            str,  # only for network game; None if local
                }

        Returns:
            this round's two player adapters.

        Raises:
            ValueError: invalid user role choice or players assembly configuration.
            ConnectionError: network connection failure (network "handshake" for network game failed).
        """
