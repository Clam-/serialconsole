import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from serialconsole.console import SerialConsole


def main():
    parser = argparse.ArgumentParser(
        prog="serialconsole",
        description="Interactive serial port console",
    )
    parser.add_argument("port", help="Serial port (e.g. /dev/ttyUSB0, COM3)")
    parser.add_argument("-b", "--baud", type=int, default=9600,
                        help="Baud rate (default: 9600)")
    parser.add_argument("--bytesize", type=int, choices=[5, 6, 7, 8],
                        default=8, help="Data bits (default: 8)")
    parser.add_argument("--parity", choices=["N", "E", "O", "M", "S"],
                        default="N",
                        help="Parity: N(one), E(ven), O(dd), M(ark), S(pace) "
                             "(default: N)")
    parser.add_argument("--stopbits", type=float, choices=[1, 1.5, 2],
                        default=1, help="Stop bits (default: 1)")
    parser.add_argument("--xonxoff", action="store_true",
                        help="Enable software flow control (XON/XOFF)")
    parser.add_argument("--rtscts", action="store_true",
                        help="Enable hardware flow control (RTS/CTS)")
    parser.add_argument("-e", "--echo", action="store_true",
                        help="Force local echo on (overrides auto-detection)")
    parser.add_argument("-t", "--timestamps", action="store_true",
                        help="Prefix each received line with a timestamp")

    args = parser.parse_args()

    try:
        console = SerialConsole(
            port=args.port,
            baudrate=args.baud,
            bytesize=args.bytesize,
            parity=args.parity,
            stopbits=args.stopbits,
            flow_xonxoff=args.xonxoff,
            flow_rtscts=args.rtscts,
            force_echo=args.echo,
            timestamps=args.timestamps,
        )
    except Exception as e:
        sys.stderr.write(f"Error opening port: {e}\n")
        sys.exit(1)

    console.run()


if __name__ == "__main__":
    main()
