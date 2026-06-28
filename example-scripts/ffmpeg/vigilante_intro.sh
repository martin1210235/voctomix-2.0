#!/bin/bash

# DEPRECATED - DO NOT RUN
#
# This script was replaced by logic integrated in voctogui/lib/toolbar/mix.py.
# The GUI launches launch_intro.sh directly when the operator presses CUT with
# the intro source selected, with a delay to allow ffmpeg to connect before
# voctocore attempts to display the source.
#
# Running this script in the background CONFLICTS with the GUI and causes:
#   - intro connecting on startup before the operator presses CUT.
#   - intro reconnecting when the video ends (unintended loop behaviour).
#
# To stop a running instance:
#   pkill -f vigilante_intro.sh

echo "vigilante_intro.sh is DEPRECATED and does nothing. See the comment in this script."
exit 0
