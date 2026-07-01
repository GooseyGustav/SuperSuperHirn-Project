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


import ipaddress
import logging
import sys
from urllib.parse import urlparse

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

    # TODO: which players (adapters) should be assembled must be loaded from the persisted game data
    #  and sent to the ForAssemblingPlayers port

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

        # for network game
        self._network_enabled: bool = False
        self._network_address: str | None = None
        self._gamer_id: str | None = None

    # ForGameAdministration methods

    def start_game(self) -> None:
        """
        Starts the game by initializing the necessary parts and running the game engine.

        Step by step: this method loads the configuration, sets up the configuration manager,
        creates the game configuration object, and initializes the game engine.

        Returns: None
        """
        # make sure local Game doesn't launch network
        self._network_enabled = False
        self._network_address = None
        self._gamer_id = None

        thread = threading.Thread(
            target=self._configure_and_run,
            daemon=True
        )
        thread.start()

    def start_network_game(self, network_address: str, gamer_id: str) -> None:
        """Starts the game with a remote player. The App connects to the remote player's
        network address and provides the User's Gamer ID. The implementer is responsible for
        validating the network address and gamer ID.

        Args:
            network_address: IP:port or URL ("http://" or "https://" optional.)
            gamer_id: the user's gamer ID

        Raises:
            ValueError: data or protocol failure :
                - invalid network address: empty, no host, bad/missing port (IP always needs port)
                - bad server response, invalid gameid, mismatch in game configuration (nr of positions, colors)
            ConnectionError: network connection failure:
                - can't reach remote player
                - connection lost during game (--> aborts game round)

        Note:
            Raised Errors -> driving adapter can fix and retry (GUI: ask input again)
            Illegal move from remote player during game -> logged, game round aborted silently
            (no error raise).
        """
        network_address = self._normalize_address(network_address)
        self._validate_normalized_network_address(network_address)  # raises ValueError if invalid
        self._network_enabled = True
        self._network_address = network_address
        self._gamer_id = gamer_id
        self._configure_and_run()
        # does not persist on purpose

    def resume_interrupted(self) -> None:
        """Resumes the interrupted game (loads the saved game and continues the game)."""

        self._network_enabled = False

        # TODO: handle corrupt-persist: load_game() + GameEngine.resume() (called inside _configure_and_run)
        #  can raise ValueError AND KeyError on a corrupt save. Not caught here yet.
        #  This is the eventual catch spot (kept separate from the run() illegal-move catch).
        game_data = self._persist_game_port.load_game()
        self._configure_and_run(game_data)

    def _configure_and_run(self, game_data: dict | None = None) -> None:
        """Shared flow for start game/resume interrupted to set up and run a
        game round.

        When game data is given with resume_interrupted(), the saved game's config (game_data["matchup"])
        overwrites the loaded configuration so the Matchmaker can rewire the same adapters,
        and the GameEngine is created via Engine.resume() before Engine.run().
        Engine.run() continues the existing, saved game instead of creating a new game.

        Raises:


        """
        # get config for all elements
        config_dict = self.load_config()  # load from save config JSON

        # overwrite players assembly to resume an interrupted in assembly it was started in
        if game_data is not None:  # Resumed interrupted game
            # game_data["matchup"] will overwrite any config selection entries that differ from
            # the saved game's config for this round (doesn't re-save config to ForPersistingConfig Port).
            config_dict = {**config_dict, **game_data.get("matchup", {})}  # overwrite game config

        # make sure the "real" live bool ist active (not old saved config)
        config_dict["network_enabled"] = self._network_enabled

        # recheck
        self._validate_config(config_dict)

        config_manager = ConfigManager(config_dict)
        game_config = config_manager.create_config_obj()  # type Config
        self._config_manager = config_manager

        self._game_engine = GameEngine(game_config)

        if game_data is not None:
            self._game_engine.resume(game_data)

        players_config_for_players_assembling_port = {
            **config_dict,
            "number_of_positions": game_config.number_of_positions,
            "number_of_colors": game_config.number_of_colors,
            "network_address": self._network_address,
            "gamer_id": self._gamer_id,
        }

        try:
            codemaker, codebreaker = self._assembling_players_port.assemble_players(
                players_config_for_players_assembling_port
            )
        except (ValueError, TypeError, ConnectionError) as e:
            logging.warning("Error assembling players: %s", e)
            self._game_engine = None
            self._config_manager = None
            raise

        try:
            self._game_engine.run(codemaker, codebreaker)
        except ConnectionError:  # tells driver (GUI): problem with network
            logging.warning("Network failure during game; aborting game.", exc_info=True)
            self._game_engine = None
            self._config_manager = None
            raise
        except (ValueError, TypeError):  # illegal move -> quiet abort (not passes to GUI)
            # doesn't include resume/load of a corrupt json
            logging.warning("Illegal move has reached the app; aborting round without saving.", exc_info=True)
            self._game_engine = None
            self._config_manager = None
            return

        self._persist_current_game()

    def start_game_delete_interrupted(self) -> None:
        """Starts the game and deletes the interrupted game (clears the board and
        starts a new game).
        """
        self._persist_game_port.delete_game()
        self.start_game()

    def interrupt_game(self) -> None:
        """Interrupts the game (saves the game for a later time and stops it)."""
        if self._game_engine is None:  # no active game to interrupt (like if abort after illegal move passed)
            return
        self._game_engine.interrupt_game()
        self._persist_current_game()

    def _persist_current_game(self) -> None:
        """Build the dict to persist the current local game and save it.
        Does not save network games.
        """
        if self._network_enabled:
            return
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
            dict: the loaded configuration.
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
        # enum fields are validated by the enum itself with simple instantiation attempts
        Gamemode(config["gamemode"])  # ValueError if not a valid Gamemode
        user_role = Role(config["user_role"])  # ValueError if not a valid Role
        network_enabled = config["network_enabled"]

        # bool check
        if not isinstance(config["network_enabled"], bool):
            raise ValueError("network_enabled must be a boolean")

        # check network only with user_role = codebreaker
        if network_enabled and user_role is not Role.CODEBREAKER:
            raise ValueError("network_enabled is only valid with user_role set to codebreaker")

        # non-negative int check for time
        for key in ("countdown_millis", "delay_millis"):
            value = config[key]
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{key} must be a non-negative integer")

    @staticmethod
    def _validate_normalized_network_address(normalized_network_address: str):
        """Validates the provided network address.
        Accepts IP:port or URLs with optional http:// or https://.
        IP requires explicit port, URL/hostname doesn't.
        Will pass silently if the address is valid, raises ValueError otherwise.
        """
        parsed_address = urlparse(normalized_network_address)

        if not parsed_address.hostname:
            raise ValueError(f"No valid host found in: {normalized_network_address}")

        # catch port errors
        try:
            port = parsed_address.port
        except ValueError:
            raise ValueError(f"No valid port found in: {normalized_network_address!r}")

        # if ip address, make sure valid (IP: port mandatory, hostname: port optional)
        # (don't need regex thanks to ipaddress lib)
        try:
            ipaddress.ip_address(parsed_address.hostname)
            is_ip_address = True
        except ValueError:
            is_ip_address = False

        if is_ip_address and port is None:
            raise ValueError(f"IP requires explicit port: {normalized_network_address!r}")

    @staticmethod
    def _normalize_address(address_arriving_from_port: str) -> str:
        if not address_arriving_from_port or not address_arriving_from_port.strip():
            raise ValueError("network_address cannot be empty")

        address_arriving_from_port = address_arriving_from_port.strip()

        if not address_arriving_from_port.startswith(("http://", "https://")):
            address_arriving_from_port = f"http://{address_arriving_from_port}"
        return address_arriving_from_port
