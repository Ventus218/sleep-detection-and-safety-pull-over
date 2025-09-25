import time
from typing import cast
from carla import Client, Vehicle

from remove_vehicles_and_sensors import remove_vehicles_and_sensors
from vehicle_state_machine import VehicleStateMachine

FRAMERATE = 60
DT = 1 / FRAMERATE

client = Client("192.168.1.24", 2000)
client.set_timeout(120)  # pyright: ignore[reportUnknownMemberType]
world = client.get_world()
settings = world.get_settings()
settings.synchronous_mode = True
settings.fixed_delta_seconds = DT
_ = world.apply_settings(settings)

try:

    spectator = world.get_spectator()
    blueprint = world.get_blueprint_library()
    vehicle_bp = blueprint.filter("vehicle.*")[0]
    spwan_point = world.get_map().get_spawn_points()[0]
    vehicle = cast(Vehicle, world.spawn_actor(vehicle_bp, spwan_point))
    spectator.set_transform(vehicle.get_transform())  # pyright: ignore[reportUnknownMemberType]

    state_machine = VehicleStateMachine(vehicle)
    while True:
        _ = world.tick()
        tick_start = time.time()
        state_machine.step(DT)
        compute_time = time.time() - tick_start
        if compute_time < DT:
            time.sleep(DT - compute_time)
finally:
    remove_vehicles_and_sensors(world)
    settings = world.get_settings()
    settings.synchronous_mode = False
    settings.fixed_delta_seconds = 0
    _ = world.apply_settings(settings)
