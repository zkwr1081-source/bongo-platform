#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/BONGO"
python -m bongo.runtime.start

if command -v termux-open-url >/dev/null 2>&1; then
    sleep 1
    termux-open-url "http://127.0.0.1:8093"
fi
