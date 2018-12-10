import docker
# print(docker.version)
#
# client = docker.from_env()
#
def test_connection():
    print(docker)
    # High level client
    client = docker.from_env()
    # Check running docker images using SDK
    assert len(client.containers.list()) > 0, "No docker containers found"
    for container in client.containers.list():
        print(container.name, container.status)
        print('\t',container.image.tags)
        print('\t',container.labels)
        print("\n")
    # container.logs()