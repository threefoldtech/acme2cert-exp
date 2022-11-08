import redis

DEFAULT_REDIS_HOST = "localhost"
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_PASSWORD = None
DEFAULT_REDIS_DB = 0


class Factory:
    def __init__(self):
        self.instances = {}

    def create(self, *args):
        raise NotImplementedError

    def get(self, *args):
        if args in self.instances:
            return self.instances[args]

        instance = self.create(*args)
        self.instances[args] = instance
        return instance


def get_redis_pool(options):
    host = options.get("host", DEFAULT_REDIS_HOST)
    port = int(options.get("port", DEFAULT_REDIS_PORT))
    password = options.get("password", DEFAULT_REDIS_PASSWORD)
    db = int(options.get("db", DEFAULT_REDIS_DB))
    return redis.ConnectionPool(host=host, port=port, password=password, db=db)


def get_redis_connection(pool):
    return redis.Redis(connection_pool=pool)
