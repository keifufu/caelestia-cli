import subprocess
from argparse import Namespace

from caelestia.utils.paths import c_cache_dir, caelestia_dir


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if self.args.show:
            # Print the ipc
            self.print_ipc()
        elif self.args.log:
            # Print the log
            self.print_log()
        elif self.args.message:
            # Send a message
            self.message(*self.args.message)
        else:
            # Start the shell
            args = ["qs", "-n", "-c", caelestia_dir, "--log-rules", self.args.log_rules]
            if self.args.daemon:
                args.append("-d")
                subprocess.run(args)
            else:
                shell = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)
                for line in shell.stdout:
                    if self.filter_log(line):
                        print(line, end="")

    def shell(self, *args: list[str]) -> str:
        return subprocess.check_output(["qs", "-c", caelestia_dir, *args], text=True)

    def filter_log(self, line: str) -> bool:
        return (
            "QProcess: Destroyed while process" not in line
            and f"Cannot open: file://{c_cache_dir}/imagecache/" not in line
        )

    def print_ipc(self) -> None:
        print(self.shell("ipc", "show"), end="")

    def print_log(self) -> None:
        log = self.shell("log", "-r", self.args.log_rules)
        # FIXME: remove when logging rules are added/warning is removed
        for line in log.splitlines():
            if self.filter_log(line):
                print(line)

    def message(self, *args: list[str]) -> None:
        print(self.shell("ipc", "call", *args), end="")
