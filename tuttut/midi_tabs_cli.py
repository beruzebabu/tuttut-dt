import pretty_midi
from tuttut.logic.tab import Tab
from tuttut.logic.theory import Tuning
import argparse
import traceback
from time import time
import numpy as np
from pathlib import Path
np.seterr(divide="ignore")


def parse_args():
    """Initializes the argument parser for execution.

    Returns:
        argparse.ArgumentParser: The parser object
    """
    parser = argparse.ArgumentParser(description="MIDI to stringed instrument tabs convertor")
    parser.add_argument("source", metavar="src", type=Path, help="File(path) of MIDI file to convert")
    parser.add_argument("-t", "--target", metavar="target", type=Path, help="Target file(path)", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    source: Path = args.source
    target: Path = args.target if args.target is not None else Path(f"./{args.source.with_suffix(".txt")}")

    weights = {'b': 1, 'height': 1, 'length': 1, 'n_changed_strings': 1}

    try:
        start = time()
        f = pretty_midi.PrettyMIDI(source.absolute().as_posix())
        tab = Tab(source.stem, Tuning(), f, weights=weights, output_file=target)
        # tab = Tab(file.stem, Tuning([Note(69), Note(64), Note(60), Note(67)]), f, weights=weights)
        tab.to_ascii()
        print(f"Time taken: {round(time() - start, 2)}s")

    except Exception as e:
        print(traceback.print_exc())
        print("There was an error. You might want to try another MIDI file. The tool tends to struggle with more complicated multi-channel MIDI files.")
