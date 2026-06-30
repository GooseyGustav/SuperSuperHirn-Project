from adapter.driven_adapter.for_getting_codebreaker_move.cpu.cpu_codebreaker import CpuCodebreaker
from adapter.driven_adapter.for_getting_codebreaker_move.gui.gui_codebreaker import GuiCodebreaker
from adapter.driven_adapter.for_getting_codemaker_move.cpu.cpu_codemaker import CpuCodemaker
from adapter.driven_adapter.for_getting_codemaker_move.gui.gui_codemaker import GuiCodemaker
from adapter.driven_adapter.for_getting_codemaker_move.network.network_codemaker import NetworkCodemaker
from app.ports.driven.for_assembling_players import ForAssemblingPlayers
from app.ports.driven.for_getting_moves.for_getting_codebreaker_move import ForGettingCodebreakerMove
from app.ports.driven.for_getting_moves.for_getting_codemaker_move import ForGettingCodemakerMove
from network.network_manager import NetworkManager

# Port Info:
# class ForAssemblingPlayers(ABC):
# """The port for assembling players. Requests one instantiated adapter per role
# (one Codemaker, one Codebreaker).
# Note:
#     - Implemented by `Matchmaker` (src/startup).
#     - Implemented for testing App by `FakeMatchmaker` (src/startup).
#     - Passed to App by `SupersuperhirnRunner` (src/startup).
#     - Methods called by: `GameManager` (src/app/game_management).
# """


CODEMAKER = "CODEMAKER"
CODEBREAKER = "CODEBREAKER"
OBSERVER = "OBSERVER"


class Matchmaker(ForAssemblingPlayers):

    def __init__(self, gui_callback=None):
        # self._player_adapter: dict = {} # unused (direct call)
        self._gui_callback = gui_callback  # in diagram/class ref.: "onGuiGameStart"
        self._network_manager = None
        # self.headless = headless # True for CLI driver

    def assemble_players(self, config: dict) -> tuple[ForGettingCodemakerMove, ForGettingCodebreakerMove]:

        # Port Contract:
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

        network_enabled = config["network_enabled"]
        user_role = config["user_role"]  # str per Port contract (from app enum `Role`)
        number_of_positions = config["number_of_positions"]
        number_of_colors = config["number_of_colors"]
        network_address = config.get("network_address")
        gamer_id = config.get("gamer_id")

        # TODO: make sure that guard is in GameManager._validate_config
        # TODO: make sure to catch that raise in GameManager
        # Network can only be codemaker
        if network_enabled and user_role != CODEBREAKER:
            raise ValueError("Network game only possible with user as codebreaker")

        match user_role:
            case "CODEBREAKER":
                cpu_or_net_codemaker = (
                    self._network_codemaker(network_address, gamer_id, number_of_positions, number_of_colors)
                    if network_enabled
                    else CpuCodemaker()
                )
                gui_codebreaker = GuiCodebreaker()
                self._notify_gui_callback({"codemaker": None, "codebreaker": gui_codebreaker})
                return cpu_or_net_codemaker, gui_codebreaker
            case "CODEMAKER":
                gui_codemaker = GuiCodemaker()
                cpu_codebreaker = CpuCodebreaker()
                self._notify_gui_callback({"codemaker": gui_codemaker, "codebreaker": None})
                return gui_codemaker, cpu_codebreaker
            case "OBSERVER":
                cpu_codemaker = CpuCodemaker()
                cpu_codebreaker = CpuCodebreaker()
                # self._notify_gui_callback({"codemaker": None,
                #                            "codebreaker": None})
                return cpu_codemaker, cpu_codebreaker
            case _:
                raise ValueError(f"Unsupported user_role: {user_role}")  # TODO: catch that error

    def _network_codemaker(
        self, network_address: str, gamer_id: str, number_of_positions: int, number_of_colors: int
    ) -> NetworkCodemaker:
        self._network_manager = NetworkManager(network_address)  # default timeout = 5
        network_codemaker = NetworkCodemaker(self._network_manager, gamer_id, number_of_positions, number_of_colors)
        network_codemaker.start_network_session()
        return network_codemaker

    def _notify_gui_callback(self, player_adapter: dict):
        if self._gui_callback is not None:
            self._gui_callback(player_adapter)


# Waren im Diagram und in der Klassendoku, aber doch nicht nötig:

# def _create_codebreaker(self, player_type: str):
#     pass
#
# def _create_netplayer(self, player_type: str):
#     self.network_manager = NetworkManager(server_url=None, timeout=None)
