# UART Info

## TODO

- [x] remove len field
- [x] remove write and close in while loop
- [x] add AAAB preamble
- [x] write function should accept cmd and data to send and add the preamble
- [x] add remaining commands
- [x] use same protocol to read data
- [x] move to separate package, e.g. uart, shared is only for shared classes used by differents parts of the SW
- [x] parameterize functions to pass data. e.g. lift up / lift down
- [x] read and write should run in separate task (blockierend, erst wieder schreiben, wenn acklowleged)
- [x] add id field -> waiting on protocol definition (schauen bei andre in github)
- [ ] implement checksum -> waiting on definition
- [x] check for ACK, NACK, checksum error and resend in that case (with same message id)
- [x] await ACK, NACK or timeout before sending other command (von aussen)
- [x] support receiving GET_STATE response (SEND_STATE) 
- [ ] make decoder funtion better, that when a command is not valid, make none and it wont add into the queue

## Local Setup

Create virtual serial port -> creates two devices e.g. /dev/pts/3, /dev/pts/4:

```bash
socat -d -d pty,rawer,echo=0 pty,rawer,echo=0
```

Read / write to serial port from console to test the software:

```bash
# minicom -D <port> -H -b 115200
# E.g. read on one and write on second:
 minicom -D /dev/ttys047 -H -b 115200
 minicom -D /dev/ttys048 -H -b 115200
```

SEND_STATE example response:

```bash
# random data, will change but general structure is the same as the write commands#
# b'AAAB\x07\xca\xff\xee\xaa\xdc\x00\x08\x00\x00\x00\x00\x001\x00  9\x0c'
```
