# UART Info

## TODO

- [x] remove len field
- [x] remove write and close in while loop
- [x] add AAAB preamble
- [x] write function should accept cmd and data to send and add the preamble
- [x] add remaining commands
- [ ] use same protocol to read data
- [x] move to separate package, e.g. uart, shared is only for shared classes used by differents parts of the SW
- [x] parameterize functions to pass data. e.g. lift up / lift down
- [ ] read and write should run in separate task
- [ ] add id field -> waiting on protocol definition
- [ ] implement checksum -> waiting on definition
- [ ] check for ACK, NACK, checksum error and resend in that case (with same message id)
- [ ] await ACK, NACK or timeout before sending other command
- [ ] support receiving GET_STATE response (SEND_STATE)

## Local Setup

Create virtual serial port -> creates two devices e.g. /dev/pts/3, /dev/pts/4:

```bash
socat -d -d pty,rawer,echo=0 pty,rawer,echo=0
```

Read / write to serial port from console to test the software:

```bash
# minicom -D <port> -H -b 115200
# E.g. read on one and write on second:
 minicom -D /dev/pts/3 -H -b 115200
 minicom -D /dev/pts/4 -H -b 115200
```

SEND_STATE example response:

```bash
# random data, will change but general structure is the same as the write commands#
# b'AAAB\x07\xca\xff\xee\xaa\xdc\x00\x08\x00\x00\x00\x00\x001\x00  9\x0c'
```
