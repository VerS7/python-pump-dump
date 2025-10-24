#!/bin/bash

PID_FILE="main.pid"

if [ -f "$PID_FILE" ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
    echo "Процесс работает с PID: $(cat $PID_FILE)"
    echo "Использует ресурсов:"
    ps -p $(cat $PID_FILE) -o %mem,%cpu 
else
    echo "Процесс не запущен"
fi