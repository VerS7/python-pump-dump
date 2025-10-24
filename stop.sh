#!/bin/bash

PID_FILE="main.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Процесс остановлен (PID: $PID)"
    else
        echo "Процесс с PID $PID не найден"
    fi
    rm -f $PID_FILE
else
    echo "PID файл не найден"
fi