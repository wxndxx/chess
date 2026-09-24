class InvalidCommandException(Exception):
    def __str__(self) -> str:
        command = self.args[0]
        message = ""
        if len(self.args) > 1:
            message = self.args[1]
        if isinstance(command, list):
            error_command = " ".join(command)
        else:
            error_command = command
        if message:
            return f"{message}: {error_command}"
        return f"Invalid command - {error_command}"
