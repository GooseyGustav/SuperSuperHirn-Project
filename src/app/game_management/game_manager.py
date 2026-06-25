# From Class Reference:
#
# **NOTE: even if Adapters have their own validators: port return must get validated (wether is legal).
# GameEngine calls ports => checks legality of each move in run()**
#
# ### `GameManager` _(implements `ForGameAdministration` + `ForConfiguringGame`)_
#
# - **Responsibility:** the driving-port implementation; orchestrates lifecycle + configuration;
# owns persistence (config + game); delegates live-game/thread work to `GameEngine`.
# - **Attributes:** `configManager: ConfigManager`, `gameEngine: GameEngine`, `persistConfigPort:
# ForPersistingConfig`, `assemblingPlayersPort: ForAssemblingPlayers`, `persistGamePort: ForPersistingGame`
# - **Methods (admin):** `startGame()` _(Calls `assemblinglayersPort.assemblePlayers`)_,
# `startGameDeleteInterrupted()`, `resumeInterrupted()`, `interruptGame()`, `abortGame()`, `restartGame()`,
# `exitProgramm()`.
# - **Methods (config):** `saveConfig(dict)`, `loadConfig(): dict`, `resetConfig()`. **(private):**
# `createConfigPersistObject(): dict`, `persistConfig(config)`, `persistGame(game: Game)`
# _(builds the dict and calls `persistGamePort.saveGame(dict)`)_.
# - **Constructor (injection):** `(persistConfigPort, assemblingPlayersPort, persistGamePort)`.
# - **Creates:** `GameEngine` (per game), `ConfigManager`.
# - **Instantiated by:** `SupersuperhirnApp`.

# # from diagram:

# attr/params:
# configManager: ConfigManager
# gameEngine: GameEngine
# persistConfigPort: ForPersistingConfig
# persistGamePort: ForPersistingGame
# assemblingPlayersPort: ForAssemblingPlayers
#
# methods
# + startGame() // note on side
# + startGameDeleteInterrupted()
# + resumeInterrupted() // prüfen ob spiel gespeichert; lädt gameData aus dict von loadGame(),
# erstellt GameConfig (aber delegiert prüfen der Validität des secretCodes aus geladenen gameData an GameEngine)
# + interruptGame() // ruft gameengine.createGamePersistObject() und aus dem returned
# objekt erstellt dict fuer persistgameport
# + abortGame()
# + restartGame()
# + exitApplication()
# + saveConfig(Dict)  //  zu port
# + loadConfig(): Dict
# + resetConfig()


# From Diagram (OM):

# WICHTIG ZU GAME MANAGER  (ABLAUF)
#
# startGame() :
# Rolle des startens und eines kompletten runGame(), durchführt das spiel bis stop/interrupt und persistiert:
# - erhält player vom port forassembling players (runtime: bedeutet vom matchmaker)
# - ruft loadConfig(): Dict
# - ConfigManager erstellt Config Datei
# - ruft gameengine.run()
#         - run() läuft
#         - spiel interrupted oder beendet
#         - run() gibt Game-Objekt zurück
# - ruft gameengine.createGamePersistObject(): Object
# - gibt dieses Object als dict zum Port


from app.game_management.game_config_management.config_manager import ConfigManager
from app.game_management.game_config_management.role import Role
from app.game_management.live_game.game_engine import GameEngine
from app.game_model.game_mode import Gamemode
from app.ports.driven.for_assembling_players import ForAssemblingPlayers
from app.ports.driven.for_persisting.for_persisting_config import ForPersistingConfig
from app.ports.driven.for_persisting.for_persisting_game import ForPersistingGame
from app.ports.driving.for_configuring_game import ForConfiguringGame
from app.ports.driving.for_game_administration import ForGameAdministration


class GameManager(ForGameAdministration, ForConfiguringGame):
    """The GameManager's implementation of the `ForGameAdministration` and
    `ForConfiguringGame` Ports.
    """

    def __init__(
        self,
        persist_config: ForPersistingConfig,
        assembling_players: ForAssemblingPlayers,
        persist_game: ForPersistingGame,
    ):
        self._persist_config = persist_config
        self._assembling_players = assembling_players
        self._persist_game = persist_game

        # per game, declared absent at first:
        self._config_manager: ConfigManager | None = None
        self._game_engine: GameEngine | None = None

    # ForGameAdministration methods

    def start_game(self) -> None:
        """
        Starts the game by initializing the necessary parts and running the game engine.

        Step by step: this method loads the configuration, sets up the configuration manager,
        creates the game configuration object, and initializes the game engine.

        Returns: None
        """
        config_dict = self.load_config()
        config_manager = ConfigManager(config_dict)
        game_config = config_manager.create_config_obj()
        self._config_manager = config_manager

        players_config = {
            **config_dict,
            "number_of_positions": game_config.number_of_positions,
            "number_of_colors": game_config.number_of_colors,
        }

        codemaker, codebreaker = self._assembling_players.assemble_players(players_config)

        self._game_engine = GameEngine(game_config)

        # TODO: "run engine → persist (Step 4 tail); persist-policy still open: finished games vs interrupted-only."

    def start_game_delete_interrupted(self) -> None: ...

    def resume_interrupted(self) -> None: ...

    def interrupt_game(self) -> None: ...

    def abort_game(self) -> None: ...

    def restart_game(self) -> None: ...

    def exit_application(self) -> None: ...

    # ForConfiguringGame methods

    def save_config(self, config: dict) -> None:
        """Validates the provided configuration and if valid, saves it to a file."""
        self._validate_config(config)
        self._persist_config.save_config_dict(config)

    def load_config(self) -> dict:
        """Loads the configuration from a file."""
        return self._persist_config.load_config_dict()

    def reset_config(self) -> None:
        """Resets the configuration to the default values."""
        self._persist_config.reset_to_default()

    @staticmethod
    def _validate_config(config: dict) -> None:
        """Validates the provided configuration dictionary.
        Will pass silently if the configuration is valid, raises ValueError otherwise.
        """

        # enum fields are validated by the enum itself with simple attempts
        Gamemode(config["gamemode"])  # ValueError if not a valid Gamemode
        Role(config["user_role"])  # ValueError if not a valid Role

        # bool check
        if not isinstance(config["network_enabled"], bool):
            raise ValueError("network_enabled must be a boolean")

        # non-negative int check for time
        for key in ("countdown_millis", "delay_millis"):
            value = config[key]
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{key} must be a non-negative integer")
