from app.ports.driven.for_getting_moves.for_getting_codemaker_move import ForGettingCodemakerMove
from app.ports.driven.for_getting_moves.for_getting_codebreaker_move import ForGettingCodebreakerMove
from app.ports.driven.for_assembling_players import ForAssemblingPlayers

from network.network_manager import NetworkManager


class Matchmaker(ForAssemblingPlayers):
    def __init__(self, gui_callback: callable):
        self.player_adapter: dict = {}
        self.gui_callback = gui_callback
        self.network_manager = None

    def assemble_players(self, config: dict) -> tuple[ForGettingCodemakerMove, ForGettingCodebreakerMove]:
        # Read disctionary and get player adapter
        # player_string = None #  List of respective player string from config

        # self.player_adapter.add(self._create_codemaker(player_string[0]))
        # self.player_adapter.add(self._create_codebreaker(player_string[1]))

        # if player contains any keyword "human":
        #   go over each entry in player_adapter. If Human, send dict to
        #   gui_callback with key=role and value=Human{Role}Adapter
        #   _notify_gui_callback()
        pass

    def _create_codemaker(self, player_type: str):
        pass

    def _create_codebreaker(self, player_type: str):
        pass

    def _create_netplayer(self, player_type: str):
        self.network_manager = NetworkManager(server_url=None, timeout=None)

    def _notify_gui_callback(self):
        self.gui_callback(self.player_adapter)
