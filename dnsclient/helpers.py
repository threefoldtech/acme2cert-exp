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
