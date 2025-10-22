
import random
import math
import carla
from typing import List, Tuple
from carla import Client, World, Map, Vehicle, Transform, Location, Rotation
from remove_vehicles_and_sensors import remove_vehicles_and_sensors

class Scenario():
    def __init__(self, map_name: str):
        self.map_name: str = map_name

    def load(self, world: World) -> Vehicle:
        raise NotImplementedError()

# map.get_spawn_points()[349]

def load_scenario(client: Client, scenario: Scenario) -> tuple[World, Vehicle]:
    w = client.load_world_if_different(scenario.map_name)
    world = w if w is not None else client.get_world()
    ego_vehicle = scenario.load(world)

    return (world, ego_vehicle)


