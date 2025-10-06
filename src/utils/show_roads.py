
import os
import time
from typing import cast

from carla import (
    Client,
    Color,
    LaneType,
    Location,
    Waypoint,
    World,
)

host = os.environ.get("HOST", "localhost")
port = os.environ.get("PORT", "2000")
port = int(port)
client = Client(host, port)
client.set_timeout(120)  # pyright: ignore[reportUnknownMemberType]
world = client.get_world()

match client.load_world_if_different("Town12"):  # pyright: ignore[reportUnknownMemberType]
    case None:
        world = client.get_world()
    case w:  # pyright: ignore[reportUnknownVariableType]
        world = cast(World, w)

world_map = world.get_map()

for i in range(3):
    _ = world.wait_for_tick(60)

waypoint_interval = 20
location = Location(x=1473.250000, y=3077.490234, z=365.242188)
world.get_spectator().set_location(location)  # pyright: ignore[reportUnknownMemberType]
waypoint = world_map.get_waypoint(location)
# waypoints = waypoint.next(600)
emergency_waypoint = cast(
    Waypoint, world_map.get_waypoint(location, lane_type=LaneType.Shoulder)
)
emergency_waypoints = emergency_waypoint.next_until_lane_end(waypoint_interval)

while True:
    time.sleep(5)
    waypoints = waypoint.next_until_lane_end(10)
    for w in waypoints:
        world.debug.draw_string(w.transform.location, "W", life_time=5)
    waypoint.next
    for w in emergency_waypoints:
        world.debug.draw_string(
            w.transform.location, "W", color=Color(0, 255, 0), life_time=5
        )
    print("spectator:", world.get_spectator().get_location())


