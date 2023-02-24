class Colours:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @classmethod
    def Bold(self, text: str) -> str:
        return self.BOLD + text + self.END

    @classmethod
    def Red(self, text: str) -> str:
        return self.RED + text + self.END

    @classmethod
    def Bold_Red(self, text: str) -> str:
        return self.Bold(self.RED + text + self.END)

    @classmethod
    def Green(self, text: str) -> str:
        return self.GREEN + text + self.END

    @classmethod
    def Bold_Green(self, text: str) -> str:
        return self.Bold(self.GREEN + text + self.END)
