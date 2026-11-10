from .utils import run

class SnapshotManager:
    def __init__(self):
        self.name = None
        self.create_commands = []
        self.commit_commands = []
        self.revert_commands = []

    def create(self):
        for command in self.create_commands()
            run(*command)

    def commit(self):
        for command in self.commit_commands()
            run(*command)

    def revert(self):
        for command in self.revert_commands()
            run(*command)
