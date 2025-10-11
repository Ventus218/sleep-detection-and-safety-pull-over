
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


world = client.get_world()
world_map = world.get_map()
if not world_map.name.endswith("Town12"):
    world = client.load_world("Town12")
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
    waypoints = waypoint.next_until_lane_end(10)
    for w in waypoints:
        world.debug.draw_string(w.transform.location, "W", life_time=5)
    for w in emergency_waypoints:
        world.debug.draw_string(
            w.transform.location, "W", color=Color(0, 255, 0), life_time=5
        )
    print("spectator:", world.get_spectator().get_location())


