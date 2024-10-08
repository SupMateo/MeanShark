import logging

class Information:
    def __init__(self):
        self.info = {'version': 'v1.0.0', 'release_date': 'September 12th, 2024'}
        logging.basicConfig(level=logging.INFO,
                            format='\033[33m[MEANSHARK | %(asctime)s | %(levelname)s] \033[0m %(message)s')

info = Information()
def welcome():
    print("")
    print("█▀▄▀█ ▄███▄     ██    ▄      ▄▄▄▄▄    ▄  █ ██   █▄▄▄▄ █  █▀")
    print("█ █ █ █▀   ▀   █ █     █    █     ▀▄ █   █ █ █  █  ▄▀ █▄█")
    print("█ ▀ █ ██▄▄    █▄▄█ ██   █ ▄  ▀▀▀▀▄   ██▀▀█ █▄▄█ █▀▀▌  █▀▄")
    print("█   █ █▄   ▄▀ █  █ █ █  █  ▀▄▄▄▄▀    █   █ █  █ █  █  █  █")
    print(" █     ▀███▀  █    █  █ █  ▄▄           █     █   █     █")
    print("  ▀            █   █   ██  █ ▀▄        ▀     █   ▀     ▀")
    print("                ▀          █   ▀▄           ▀")
    print("▄▄▄▄▄▄▄▀▀▀▄▄▄▄▄▄▄▄▄▀▀▄▄▄▀▀ █     ▀▄ ▀▀▄▄▄▄▀▀▄▄▄▄▄▄▄▀▀▀▄▄▄▄▄")
    print("                     ▄    ▄         ▄    ▄")
    print("                     ▀      ▀▀  ▀▀▀      ▀ ")
    print("                        ▀   ▄▄▄  ▄    ▀ ")
    print("")
    print("                       Training Tool                       ")
    print("")
    print("    Developped by SupMateo on GitHub")
    print("    https://github.com/SupMateo/MeanShark")
    print("    Version {version}, {release_date}".format(version=info.info['version'],release_date=info.info['release_date']))
    print("▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄")
    print("")

