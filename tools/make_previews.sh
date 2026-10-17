#!/bin/bash
# small committed previews (GIF thumbnails): tools/make_previews.sh <animated.mp4> <name>
set -e
mkdir -p previews
ffmpeg -y -loglevel error -i "$1" -vf "fps=10,scale=216:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" "previews/$2.gif"
