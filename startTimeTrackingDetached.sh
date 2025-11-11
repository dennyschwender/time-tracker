#!/bin/zsh

# Run the nohup command with the full paths
/usr/bin/nohup sh -c 'cd /Users/denny/Development/TimeTracking && PYTHONPATH=/Users/denny/Development/TimeTracking/src /Users/denny/Development/.venv/bin/python -u src/main.py' &

# Optional: Exit the script immediately
exit