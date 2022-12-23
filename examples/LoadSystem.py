import argparse

import pysamss
from mayavi import mlab

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='path to .psm input file')
    parser.add_argument('-e', '--every_nth', nargs='?', const=1, type=int, help='load every nth save timestep (default=1)')
    parser.add_argument('-p', '--plot', action='store_true', help='plot system')
    parser.add_argument('-s', '--save_animation', action='store_true', help='save animation')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    system = pysamss.System(args.input_file)
    system.load(args.input_file, args.every_nth)
    if args.plot:
        fig = pysamss.MainWidget()
        fig.loadSystem(system, save_animation=args.save_animation)
        fig.showMaximized()
        mlab.show()

if __name__ == "__main__":
    main()
