from gen_figures_linux import linux_main
from gen_figures_nonlinux import nonlinux_main
from argparse import ArgumentParser
import os

def main(args):
    config = args.config if os.path.exists(args.config) else None
    if config:
        nonlinux_main(config)
        linux_main(config)
    

if __name__ == "__main__":
    parser = ArgumentParser("Torte Dashboard Preprocessing")
    parser.add_argument("--config", "-c", type=str, required=True)
    args = parser.parse_args()
    main(args)