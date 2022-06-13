from sys import argv
from . game import Chess


def main():
    try:
        # TODO: use argparse
        sleep_time = 0
        if len(argv) > 2:
            print("Usage: pychess [sleep_time]")
            return 1
        elif len(argv) == 2:
            try:
                sleep_time = float(argv[1])
            except ValueError:
                print("Usage: pychess [sleep_time]")
                return 1
        game = Chess()
        game.start(sleep_time)
    except (EOFError, KeyboardInterrupt):
        print("\n Quitting...")


if __name__ == "__main__":
    main()
