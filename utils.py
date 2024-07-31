import logging

info = {'version': 'alpha 0.0.2', 'release_date': 'July 31th, 2024'}
logging.basicConfig(level=logging.DEBUG,
                    format='\033[33m[MEANSHARK | %(asctime)s | %(levelname)s] \033[0m %(message)s')

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
    print("    Developped by SupMateo on GitHub")
    print("    https://github.com/SupMateo/MeanShark")
    print("    Version {version}, {release_date}".format(version=info['version'],release_date=info['release_date']))
    print("▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄")
    print("")
