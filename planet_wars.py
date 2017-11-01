from utils import Debuggable

from math import ceil, sqrt
from sys import stdout
import math


def pov(owner, who):
    if who == 1 or owner == 0:
        return owner
    else:
        return 2 if owner == 1 else 1


class Fleet(object):
    def __init__(self, owner, num_ships, source_planet=-1, destination_planet=-1,
                 total_trip_length=-1, turns_remaining=-1):
        self.owner = owner
        self.num_ships = num_ships
        self.src = source_planet
        self.dest = destination_planet
        self.total_trip_length = total_trip_length
        self.turns_remaining = turns_remaining

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.repr_for()

    def repr_for_enemy(self):
        return self.repr_for(2)

    def repr_for(self, who=1):
        return "F %d %d %d %d %d %d\n" % (pov(self.owner, who), self.num_ships,
                                          self.src, self.dest,
                                          self.total_trip_length, self.turns_remaining)


class PlanetWars(Debuggable):
    def __init__(self, game_state=None):
        super(PlanetWars, self).__init__()
        self.planets = []
        self.fleets = []
        self.turn = 0
        self.real_orders = []
        self.game_state = game_state
        self.debug_name = "planetwars"
        self.via_standard_io = True
        if game_state:
            self.parse_game_state()

    def load_data(self, game_state):
        self.game_state = game_state
        self.real_orders = []
        self.parse_game_state()

    @property
    def num_planets(self):
        return len(self.planets)

    def get_planet(self, planet_id):
        return self.planets[planet_id]

    @property
    def num_fleets(self):
        return len(self.fleets)

    def get_fleet(self, fleet_id):
        return self.fleets[fleet_id]

    def _objects_by_owners(self, objects, owners):
        lst = []
        for obj in objects:
            if obj.owner in owners:
                lst.append(obj)
        return lst

    def _planets_by_owners(self, *owners):
        return self._objects_by_owners(self.planets, owners)

    def _fleets_by_owners(self, *owners):
        return self._objects_by_owners(self.fleets, owners)

    def cache_immutable_info(self):
        self.my_planets = self._planets_by_owners(1)
        self.neutral_planets = self._planets_by_owners(0)
        self.enemy_planets = self._planets_by_owners(2)
        self.not_my_planets = self._planets_by_owners(0, 2)
        self.my_fleets = self._fleets_by_owners(self, 1)
        self.enemy_fleets = self._fleets_by_owners(self, 2)

    def __repr__(self):
        return "".join([str(pl) for pl in (self.planets + self.fleets)])

    def repr_for_enemy(self):
        return "".join([obj.repr_for_enemy() for obj in (self.planets + self.fleets)])

    def distance(self, src_id, dest_id):
        src = self.planets[src_id]
        dest = self.planets[dest_id]
        dx = src.x - dest.x
        dy = src.y - dest.y
        return int(ceil(sqrt(dx * dx + dy * dy)))

    def issue_order(self, src_id, dest_id, num_ships):
        order = (src_id, dest_id, num_ships)
        self.real_orders.append(order)
        if self.via_standard_io:
            self.debug("Order: %d %d %d" % order)
            stdout.write("%d %d %d\n" % order)
            stdout.flush()

    def total_ships(self, player_id):
        objs = self._planets_by_owners(player_id) + self._fleets_by_owners(player_id)
        return sum([obj.num_ships for obj in objs])

    def is_alive(self, player_id):
        return self.total_ships(player_id) > 0

    def is_game_over(self, max_turns):
        '''check for end of the game'''
        if not(all[self.is_alive(player) for player in range(1,3)]) or self.turn > max_turns:
            raise EndOfTheGame()

    @property
    def winner(self):
        pl1_ships = self.total_ships(1)
        pl2_ships = self.total_ships(2)
        self.debug("Player1: %d ships, Player2: %d ships" % (pl1_ships, pl2_ships))
        if pl1_ships > pl2_ships:
            return 1
        elif pl2_ships > pl1_ships:
            return 2
        else:
            return 0

    def load_turn_finish(self, map_data):
        turn_msg = "# %d" % self.turn
        self.debug(turn_msg)
        self.debug(turn_msg, 'server_io')
        self.turn += 1
        self.load_data(map_data)
        self.do_turn()
        self.finish_turn()

    