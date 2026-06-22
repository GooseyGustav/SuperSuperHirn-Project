from app.game_management.game_manager import GameManager
from app.ports.driven.for_assembling_players import ForAssemblingPlayers
from app.ports.driven.for_persisting.for_persisting_config import ForPersistingConfig
from app.ports.driven.for_persisting.for_persisting_game import ForPersistingGame
from app.ports.driving.for_configuring_game import ForConfiguringGame
from app.ports.driving.for_game_administration import ForGameAdministration


class SupersuperhirnApp:
    """The App's façade to connect the App's internals to all the external parts
    (the `SupersuperhirnRunner` and all Adapters).

    Note:
        - Instantiated by `SupersuperhirnRunner` (src/startup).
        - Gets the driven Ports from `SupersuperhirnRunner` (src/startup) via
        constructor injection.
        - Instantiates `GameManager` (src/app) as the Implementer of the Driving Ports
        and hands it the Driven Ports for persisting the game and configuration
        and for assembling the players.

    """

    # Order based on Class Documentation
    def __init__(
        self,
        for_persisting_game: ForPersistingGame,
        for_persisting_config: ForPersistingConfig,
        for_assembling_players: ForAssemblingPlayers,
    ) -> None:
        self._for_persisting_game = for_persisting_game
        self._for_persisting_config = for_persisting_config
        self._for_assembling_players = for_assembling_players

        # Order based on Class Documentation
        self._game_manager = GameManager(
            self._for_persisting_config, self._for_assembling_players, self._for_persisting_game
        )

    def for_game_administration(self) -> ForGameAdministration:
        """Returns the `GameManager` for the App (`GameManager` is the Implementer
        of the `ForGameAdministration` Port).
        """
        return self._game_manager

    def for_game_configuration(self) -> ForConfiguringGame:
        """Returns the `GameManager` for the App (`GameManager` is the Implementer
        of the `ForConfiguringGame` Port).
        """
        return self._game_manager
