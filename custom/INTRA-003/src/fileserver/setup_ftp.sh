#!/bin/bash
# Start SSH daemon in background
/usr/sbin/sshd

# Start vsftpd in foreground
vsftpd /etc/vsftpd/vsftpd.conf
