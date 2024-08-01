import logging

info = {'version': 'alpha 0.0.3', 'release_date': 'August 1st, 2024'}
logging.basicConfig(level=logging.INFO,
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
