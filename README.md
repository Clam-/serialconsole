# serialconsole

A simple interactive serial port console for Python.

## Install

```
pip install .
```

## Usage

```
serialconsole /dev/ttyUSB0              # defaults: 9600 8N1
serialconsole /dev/ttyUSB0 -b 115200    # set baud rate
serialconsole COM3 -b 9600 --parity E   # even parity
serialconsole /dev/ttyS0 -e             # force local echo
serialconsole /dev/ttyUSB0 -t           # timestamp received lines
```

Or run as a module:

```
python -m serialconsole /dev/ttyUSB0 -b 115200
```

### Options

| Flag | Description |
|---|---|
| `-b`, `--baud` | Baud rate (default: 9600) |
| `--bytesize` | Data bits: 5, 6, 7, 8 (default: 8) |
| `--parity` | N, E, O, M, S (default: N) |
| `--stopbits` | 1, 1.5, 2 (default: 1) |
| `--xonxoff` | Enable XON/XOFF flow control |
| `--rtscts` | Enable RTS/CTS flow control |
| `-e`, `--echo` | Force local echo on |
| `-t`, `--timestamps` | Prefix received lines with timestamps |

Press **Ctrl+]** to exit.

## License

MIT
