from carla import Client, World


def remove_vehicles_and_sensors(world: World):
    for a in world.get_actors().filter("vehicle.*"):
        _ = a.destroy()
    for a in world.get_actors().filter("sensor.*"):
        _ = a.destroy()


if __name__ == "__main__":
    client = Client("localhost", 2000)
    _ = client.get_world().tick()
    remove_vehicles_and_sensors(client.get_world())
