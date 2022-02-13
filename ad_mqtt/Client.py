# pylint: disable=attribute-defined-outside-init
import errno
import logging
import socket
import insteon_mqtt.network as IN
import alarmdecoder.event as ADE

LOG = logging.getLogger(__name__)


class Client (IN.Link):
    # Alarmdecoder signals to implement the device api.  Also need write().
    on_open = ADE.event.Event("Connected event.  f(link)")
    on_close = ADE.event.Event("Close event.  f(link)")
    on_read = ADE.event.Event("Read cb.  f(link, bytes)")
    on_write = ADE.event.Event("Written db.  f(link, data)")

    def __init__(self, host='', port=10000, reconnect_dt=30):
        IN.Link.__init__(self)
        self.addr = (host, port)
        self.reconnect_dt = reconnect_dt
        self._init_vars()

    #-----------------------------------------------------------------------
    def write(self, data):
        if not len(data):
            return

        if not isinstance(data, bytes):
            data = data.encode("utf-8")

        LOG.debug("Adding %s bytes to write buffer of %s bytes: '%s'",
                  len(data), len(self._write_buf), data)
        self._write_buf += data

        # Only need to emit if there was no data in the buffer already.
        self.signal_needs_write.emit(self, True)

    #-----------------------------------------------------------------------
    def retry_connect_dt(self):
        """Return a positive integer (seconds) if the link should reconnect.

        If this returns None, the link will not be reconnected if it closes.
        Otherwise this is the retry interval in seconds to try and reconnect
        the link by calling connect().
        """
        return self.reconnect_dt

    #-----------------------------------------------------------------------
    def connect(self):
        """Connect the link to the device.

        This should connect to the socket, serial port, file, etc.

        Returns:
          bool:  Returns True if the connection was successful or False it
          it failed.
        """
        LOG.info("Connecting to %s:%s", *self.addr)
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.addr)
        except:
            LOG.exception("Failed to connect")
            if self.socket:
                self.socket.close()

            self.socket = None
            return False

        LOG.info("Connected")
        self.signal_connected.emit(self, True)
        self.on_open()
        return True

    #-----------------------------------------------------------------------
    def fileno(self):
        """Return the file descriptor to watch for this link.

        Returns:
          int:  Returns the descriptor (obj.fileno() usually) to monitor.
        """
        return self.socket.fileno()

    #-----------------------------------------------------------------------
    def read_from_link(self):
        """Read data from the link.

        This will be called by the manager when there is data available on
        the file descriptor for reading.

        Returns:
           int:  Return -1 if the link had an error.  Or any other integer
           to indicate success.
        """
        LOG.debug("Reading from alarmdecoder")
        try:
            buf = self.socket.recv(4096)
        except socket.error as e:
            if e.errno in [errno.EWOULDBLOCK, errno.ETIMEDOUT]:
                return 0

            LOG.exception("Error during read")
            if e.errno in [errno.ECONNRESET, errno.EHOSTUNREACH]:
                return -1
            raise

        # If no data was read, the connection was closed.
        if len(buf) == 0:
            return -1

        LOG.debug("Adding %s bytes to read buffer of %d bytes",
                  len(buf), len(self._read_buf))
        self._read_buf += buf
        self.parse_read_buf()
        return 0

    #-----------------------------------------------------------------------
    def parse_read_buf(self):
        """TODO
        """
        while True:
            line, _sep, after = self._read_buf.partition(b"\n")

            # If we didn't find a new line, or the parsed data is empty, wait
            # for more data
            if not _sep or not line:
                break

            line = line.rstrip(b"\r\n")

            LOG.debug("Processing line '%s'", line)
            self.on_read(data=line)
            self._read_buf = after

    #-----------------------------------------------------------------------
    def write_to_link(self, t):
        """Write data from the link.

        This will be called by the manager when the file descriptor can be
        written to.  It will only be called after the link as emitted the
        signal_needs_write(True).  Once all the data has been written, the
        link should call self.signal_needs_write.emit(False).

        Args:
           t (float):  The current time (time.time).
        """
        num = 0
        LOG.debug("Writing to device")
        try:
            if self._write_buf:
                num = self.socket.send(self._write_buf)
        except socket.error as e:
            # If we can't actually write, then return and try again later.
            if e.errno in [errno.EWOULDBLOCK, errno.ETIMEDOUT]:
                return

            # Connection is closed.
            elif e.errno == errno.ECONNRESET:
                self.close()
                return

            raise

        LOG.debug("Wrote %d bytes", num)
        if num:
            self.on_write(data=self._write_buf[:num])
            self._write_buf = self._write_buf[num:]

        if not len(self._write_buf):
            self.signal_needs_write.emit(self, False)

    #-----------------------------------------------------------------------
    def close(self):
        """Close the link.

        The link must call self.signal_closing.emit() after closing.
        """
        if self.isClosing or self.socket is None:
            return

        LOG.info("Closing device")
        self.isClosing = True
        self.signal_closing.emit(self)
        self.on_close()

        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass

        self.socket.close()
        self._init_vars()

    #-----------------------------------------------------------------------
    def _init_vars(self):
        "TODO:"
        self.socket = None
        self._fileno = None
        self._read_buf = bytes()
        self._write_buf = bytes()
        self.isClosing = False

    #-----------------------------------------------------------------------
