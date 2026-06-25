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


import sys

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
    """The GameManager is responsible for orchestrating the lifecycle of the game.
    It receives user input (it implements of the `ForGameAdministration` and
    `ForConfiguringGame` Ports) and controls the game flow.
    It saves and loads the configuration to and from the `ForPersistingConfig` port,
    asks for the players to be assembled through the `ForAssemblingPLayers` Port,
    and delegates the actual game logic to the `GameEngine`.
    It also handles the persistence of the current game state through the
    `ForPersistingGame` port and can load an interrupted game from that port.

     The GameManager is instantiated by the `SupersuperhirnApp` which passes it the ports
     to persist the configuration and game data, and the port to assemble the players.
     It creates its own `ConfigManager` and `GameEngine` to delegate tasks to them.

     Shape of the configuration dict that the user adapter passes to the GameManager:
        {
             "gamemode":             str,   # CLASSIC | TIME_TRIAL | BLIND_TRIAL
             "user_role":            str,   # CODEMAKER | CODEBREAKER | OBSERVER
             "network_enabled":      bool,
             "countdown_millis":     int,   # TIME_TRIAL countdown time, milliseconds
             "delay_millis":         int,   # OBSERVER mode: ms between auto-moves so progress is visible
         }
    """

    def __init__(
        self,
        persist_config_port: ForPersistingConfig,
        assembling_players_port: ForAssemblingPlayers,
        persist_game_port: ForPersistingGame,
    ):
        self._persist_config_port = persist_config_port
        self._assembling_players_port = assembling_players_port
        self._persist_game_port = persist_game_port

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

        self._configure_and_run()
        self._persist_current_game()

    def resume_interrupted(self) -> None:
        """Resumes the interrupted game (loads the saved game and continues the game)."""

        game_data = self._persist_game_port.load_game()
        self._configure_and_run(game_data)
        self._persist_current_game()

    def _configure_and_run(self, game_data: dict | None = None) -> None:
        """Shared flow for start game/resume interrupted to set up and run a
        game round.

        When game data is given with resume_interrupted(), the saved game mode
        overwrites the loaded configuration and the GameEngine is created via
        Engine.resume() before Engine.run(). Engine.run() continues the
        existing game instead of the game creating a new one.
        """
        config_dict = self.load_config()  # load from save config json
        if game_data is not None:
            config_dict = {**config_dict, "gamemode": game_data["gamemode"]}  # overwrite gamemode

        config_manager = ConfigManager(config_dict)
        game_config = config_manager.create_config_obj()  # type Config
        self._config_manager = config_manager

        self._game_engine = GameEngine(game_config)
        if game_data is not None:
            self._game_engine.resume(game_data)

        players_config_for_port = {
            **config_dict,
            "number_of_positions": game_config.number_of_positions,
            "number_of_colors": game_config.number_of_colors,
        }
        codemaker, codebreaker = self._assembling_players_port.assemble_players(players_config_for_port)
        self._game_engine.run(codemaker, codebreaker)

    def start_game_delete_interrupted(self) -> None:
        """Starts the game and deletes the interrupted game (clears the board and
        starts a new game).
        """
        self._persist_game_port.delete_game()
        self.start_game()

    def interrupt_game(self) -> None:
        """Interrupts the game (saves the game for a later time and stops it)."""
        self._game_engine.interrupt_game()
        self._persist_current_game()

    def _persist_current_game(self) -> None:
        """Build the dict to persist the current game and save it."""
        game_data = self._game_engine.create_game_persist_object()
        self._persist_game_port.save_game(game_data)

    def abort_game(self) -> None:
        """Aborts the game (clears the board and stops the game)."""
        if self._game_engine is not None:
            self._game_engine.interrupt_game()  # brauch anderen Name (namenskonflikt)
        self._game_engine = None
        self._config_manager = None

    def restart_game(self) -> None:
        """Restarts the game (clears the board and starts a new game)."""
        self.abort_game()
        self.start_game()

    def exit_application(self) -> None:
        """Exits the application (closes the entire program), saving the
        current game beforehand."""
        if self._game_engine is not None:
            self.interrupt_game()
        sys.exit()

    # ForConfiguringGame methods

    def save_config(self, config: dict) -> None:
        """Validates the provided configuration and if valid, saves it to a file."""
        self._validate_config(config)
        self._persist_config_port.save_config_dict(config)

    def load_config(self) -> dict:
        """Loads the configuration from a file, loading the default config if no file
        is found. The method validates the loaded configuration before returning it.
        Returns:
            A dict containing the loaded configuration.
        """
        config = self._persist_config_port.load_config_dict()
        self._validate_config(config)
        return config

    def reset_config(self) -> None:
        """Resets the configuration to the default values by delegating to the
        Adapter in charge of persisting the Config. The default values will be
        validated at the start of the next game.
        """
        self._persist_config_port.reset_to_default()  # adapter takes care of this

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
