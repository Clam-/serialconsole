import sys
import threading
import time
import serial


class SerialConsole:
    def __init__(self, port, baudrate=9600, bytesize=8, parity="N",
                 stopbits=1, flow_xonxoff=False, flow_rtscts=False,
                 force_echo=False, timestamps=False):
        parity_map = {
            "N": serial.PARITY_NONE,
            "E": serial.PARITY_EVEN,
            "O": serial.PARITY_ODD,
            "M": serial.PARITY_MARK,
            "S": serial.PARITY_SPACE,
        }
        bytesize_map = {
            5: serial.FIVEBITS,
            6: serial.SIXBITS,
            7: serial.SEVENBITS,
            8: serial.EIGHTBITS,
        }
        stopbits_map = {
            1: serial.STOPBITS_ONE,
            1.5: serial.STOPBITS_ONE_POINT_FIVE,
            2: serial.STOPBITS_TWO,
        }

        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize_map[bytesize],
            parity=parity_map[parity.upper()],
            stopbits=stopbits_map[stopbits],
            xonxoff=flow_xonxoff,
            rtscts=flow_rtscts,
            timeout=0.1,
        )
        self.force_echo = force_echo
        self.timestamps = timestamps
        self._remote_echoes = None
        self._stop = threading.Event()
        self._line_start = True

    def _detect_echo(self):
        probe = b"AT"
        self.ser.reset_input_buffer()
        self.ser.write(probe)
        time.sleep(0.3)
        response = self.ser.read(self.ser.in_waiting or 1)
        if probe in response:
            self._remote_echoes = True
        else:
            self._remote_echoes = False

    def _should_local_echo(self):
        if self.force_echo:
            return True
        if self._remote_echoes is None:
            return True
        return not self._remote_echoes

    def _print_timestamp(self):
        if self.timestamps and self._line_start:
            stamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
            sys.stdout.write(stamp)
            sys.stdout.flush()
            self._line_start = False

    def _reader(self):
        while not self._stop.is_set():
            try:
                data = self.ser.read(self.ser.in_waiting or 1)
            except serial.SerialException:
                sys.stderr.write("\nSerial port disconnected.\n")
                self._stop.set()
                break
            if not data:
                continue
            text = data.decode("utf-8", errors="replace")
            for ch in text:
                self._print_timestamp()
                sys.stdout.write(ch)
                if ch == "\n":
                    self._line_start = True
            sys.stdout.flush()

    def run(self):
        info = (
            f"Connected to {self.ser.port} at {self.ser.baudrate} baud "
            f"[{self.ser.bytesize}{self.ser.parity}{self.ser.stopbits}]"
        )
        sys.stderr.write(info + "\n")
        sys.stderr.write("Press Ctrl+] to exit.\n")

        self._detect_echo()
        if self._remote_echoes:
            sys.stderr.write("Remote echo detected.\n")
        else:
            sys.stderr.write("No remote echo detected.\n")
        if self.force_echo:
            sys.stderr.write("Local echo forced on.\n")

        self.ser.write(b"ATL 1\r\n")
        time.sleep(0.3)
        self.ser.read(self.ser.in_waiting or 1)

        reader_thread = threading.Thread(target=self._reader, daemon=True)
        reader_thread.start()

        try:
            self._input_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self._stop.set()
            reader_thread.join(timeout=1)
            self.ser.close()
            sys.stderr.write("\nDisconnected.\n")

    def _input_loop(self):
        if sys.platform != "win32":
            self._input_loop_unix()
        else:
            self._input_loop_windows()

    def _input_loop_unix(self):
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while not self._stop.is_set():
                ch = sys.stdin.read(1)
                if not ch:
                    break
                if ch == "\x1d":  # Ctrl+]
                    break
                self.ser.write(ch.encode("utf-8"))
                if self._should_local_echo():
                    sys.stdout.write(ch)
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _input_loop_windows(self):
        import msvcrt

        while not self._stop.is_set():
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch == "\x1d":  # Ctrl+]
                    break
                self.ser.write(ch.encode("utf-8"))
                if self._should_local_echo():
                    sys.stdout.write(ch)
                    sys.stdout.flush()
            else:
                time.sleep(0.01)
