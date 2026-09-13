#!/usr/bin/env bash
set -euo pipefail

# concat.sh — Concatenate multiple video clips with optional crossfade
#
# Usage: ./concat.sh <video1> <video2> [video3...] [options]
#
# Options:
#   --xfade <sec>        Crossfade transition duration in seconds (e.g. 0.5)
#   --transition <type>  fade, wipeleft, wiperight, dissolve (default: fade)
#   --output <path>      Output video path (default: concatenated.mp4)
#
# Examples:
#   ./concat.sh part1.mp4 part2.mp4 --output merged.mp4
#   ./concat.sh shot1.mp4 shot2.mp4 shot3.mp4 --xfade 0.4 --output full.mp4

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
export PATH="${WORKSPACE_ROOT}/bin:${SCRIPT_DIR}/../bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

print_usage() {
    sed -n '3,16p' "$0" | sed 's/^# \?//'
}

if [[ $# -lt 2 ]]; then
    print_usage
    exit 1
fi

VIDEOS=()
XFADE_DUR=""
TRANSITION="fade"
OUTPUT="concatenated.mp4"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --xfade)
            XFADE_DUR="$2"
            shift 2
            ;;
        --transition)
            TRANSITION="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            if [[ -f "$1" ]]; then
                VIDEOS+=("$1")
            else
                echo "Warning: File not found: $1"
            fi
            shift
            ;;
    esac
done

if [[ ${#VIDEOS[@]} -lt 2 ]]; then
    echo "Error: Please specify at least 2 valid video files to concatenate."
    exit 1
fi

echo "Concatenating ${#VIDEOS[@]} videos..."

# If no crossfade, fast concat via concat demuxer or concat filter
if [[ -z "$XFADE_DUR" ]]; then
    CONCAT_LIST="$(mktemp /tmp/concat_list_XXXXXX.txt)"
    trap 'rm -f "$CONCAT_LIST"' EXIT
    for v in "${VIDEOS[@]}"; do
        abs_v="$(cd "$(dirname "$v")" && pwd)/$(basename "$v")"
        echo "file '$abs_v'" >> "$CONCAT_LIST"
    done
    ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" -c copy "$OUTPUT" 2>/dev/null || \
    ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" -c:v libx264 -c:a aac "$OUTPUT"
else
    # Crossfade concatenation using assemble / filter_complex
    PYTHON_EXEC="/Users/shuozheng/Documents/meinv/.venv/bin/python3"
    "$PYTHON_EXEC" -c "
import sys, subprocess, re

videos = sys.argv[4:]
xfade_dur = float(sys.argv[1])
transition = sys.argv[2]
out_path = sys.argv[3]

# get durations
durs = []
for v in videos:
    res = subprocess.run(['ffmpeg', '-i', v], stderr=subprocess.PIPE, text=True)
    m = re.search(r'Duration:\s*(\d+):(\d+):([\d\.]+)', res.stderr)
    if m:
        h, mn, s = float(m.group(1)), float(m.group(2)), float(m.group(3))
        durs.append(h*3600 + mn*60 + s)
    else:
        durs.append(5.0)

inputs = []
for v in videos:
    inputs.extend(['-i', v])

# build filter_complex
v_filters = []
a_filters = []
n = len(videos)

last_v = '0:v'
last_a = '0:a'
offset = durs[0] - xfade_dur

for i in range(1, n):
    next_v = f'v_mid_{i}'
    next_a = f'a_mid_{i}'
    v_filters.append(f'[{last_v}][{i}:v]xfade=transition={transition}:duration={xfade_dur}:offset={offset:.2f}[{next_v}]')
    a_filters.append(f'[{last_a}][{i}:a]acrossfade=d={xfade_dur}[{next_a}]')
    last_v = next_v
    last_a = next_a
    if i < n - 1:
        offset += durs[i] - xfade_dur

fc = ';'.join(v_filters + a_filters)
cmd = ['ffmpeg', '-y'] + inputs + ['-filter_complex', fc, '-map', f'[{last_v}]', '-map', f'[{last_a}]', '-c:v', 'libx264', '-c:a', 'aac', out_path]
subprocess.run(cmd, check=True)
" "$XFADE_DUR" "$TRANSITION" "$OUTPUT" "${VIDEOS[@]}"
fi

echo "Concatenation complete: $OUTPUT"
