#!/bin/bash

PID_FILE="main.pid"

if [ -f "$PID_FILE" ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
    echo -e "Процесс работает с PID: $(cat $PID_FILE)\n"
    ps -p $(cat $PID_FILE) -o lstart,etime,%mem,%cpu
else
    echo "Процесс не запущен"
fi