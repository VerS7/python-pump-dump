#!/bin/bash

PYTHON_EXEC="python"
PIP_EXEC="python -m pip"
SCRIPT_NAME="main.py"
VENV_DIR=".venv"
REQUIREMENTS="requirements.txt"
PID_FILE="main.pid"

if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения..."
    $PYTHON_EXEC -m venv $VENV_DIR
fi

if [ -f "$PID_FILE" ]; then
    PREV_PID=$(cat $PID_FILE)
    kill $PREV_PID
fi

source $VENV_DIR/bin/activate

$PIP_EXEC install --upgrade pip

if [ -f "$REQUIREMENTS" ]; then
    pip install -r $REQUIREMENTS
fi

echo "Запуск..."

python $SCRIPT_NAME &

PYTHON_PID=$!

echo $PYTHON_PID > $PID_FILE

echo "Процесс запущен!"

wait $PID
EXIT_CODE=$?
