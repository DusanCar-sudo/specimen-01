#!/bin/bash
# Builds archimedes-story.mp4: all render clips + stills (Ken Burns), soundtrack = Aura.mp3
set -e
cd "$(dirname "$0")"
SRC=renders/archimedesroboticsiq
WORK=story-work
OUT=$SRC/archimedes-story.mp4
FPS=30
mkdir -p "$WORK"; rm -f "$WORK"/*.mp4 "$WORK/list.txt"

# motion clips, normalized 1920x1080@30
motions=(
  "Glowing_orb_floats_in_darkness_20261022191825.mp4"
  "Orb_drifting_in_darkness_20261022191825.mp4"
  "Camera_circling_glowing_orb_20261022191825.mp4"
  "Glass_gate_rising_between_orb_20261022191825.mp4"
  "Glowing_lines_on_glass_screen_20261022191825.mp4"
  "Orb_hovers_before_screen_20261022191825.mp4"
)
i=0
for m in "${motions[@]}"; do
  ffmpeg -y -v error -i "$SRC/$m" -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=$FPS,format=yuv420p" \
    -an -c:v libx264 -preset veryfast -crf 20 "$WORK/m$i.mp4"
  i=$((i+1))
done

# hero film (24s, silent) normalized
ffmpeg -y -v error -i "$SRC/archimedes-hero.mp4" -vf "scale=1920:1080,fps=$FPS,format=yuv420p" \
  -an -c:v libx264 -preset veryfast -crf 20 "$WORK/hero.mp4"

# used-so-far: 6*10 + 24 = 84s ; stills fill 179-84 = 95s at 3.65s each
stills=(
  Glowing_orb_floats_in_darkness_20261022191825.jpg
  Orb_drifts_in_darkness_20261022191825.jpg
  Glowing_orb_in_dark_background_20261022191825.jpg
  Glowing_orb_before_retro_screen_20261022191825.jpg
  Amber_orb_hovering_before_screen_20261022191825.jpg
  Amber_orb_and_glass_gate_20261022191825.jpg
  Glowing_orb_and_mechanical_gate_20261022191825.jpg
  Glass_gate_rising_in_factory_20261022191825.jpg
  Glass_gate_stops_light_ribbon_20261022191825.jpg
  Glowing_light_enters_glass_gate_20261022191825.jpg
  Light_flows_into_glass_gate_20261022191825.jpg
  Light_flows_through_glass_gate_20261022191825.jpg
  Ribbon_of_light_rises_upward_20261022191825.jpg
  White_light_rising_upward_20261022191825.jpg
  Light_beam_descending_from_tower_20261022191825.jpg
  Camera_panning_upward_toward_tower_20261022191825.jpg
  Light_illuminates_desk_with_laptop_20261022191825.jpg
  Closed_laptop_and_coffee_mug_20261022191825.jpg
  Quiet_retro_desk_with_computer_20261022191825.jpg
  Retro_screen_filling_with_text_20261022191825.jpg
  Scanning_glass_gate_at_desk_20261022191825.jpg
  Scanning_light_through_glass_gate_20261022191825.jpg
  Vector_scanning_lines_moving_ins…_20261022191825.jpg
  Orb_dims_behind_glass_20261022191825.jpg
  Glowing_orb_settles_into_glow_20261022191825.jpg
  Light_fading_into_total_darkness_20261022191825.jpg
)
D=3.65
DF=110
j=0
for s in "${stills[@]}"; do
  f="$SRC/$s"; [ -f "$f" ] || { echo "skip missing $s"; continue; }
  if [ $((j % 2)) -eq 0 ]; then Z="zoom+0.0008"; else Z="1.12-0.0008*on"; fi
  ffmpeg -y -v error -loop 1 -i "$f" -t $D \
    -vf "scale=2400:-2,zoompan=z='$Z':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$DF:s=1920x1080:fps=$FPS,format=yuv420p" \
    -an -c:v libx264 -preset veryfast -crf 20 "$WORK/s$j.mp4"
  j=$((j+1))
done

ABS="$PWD/$WORK"
: > "$WORK/list.txt"
for k in 0 1 2 3 4 5; do echo "file '$ABS/m$k.mp4'" >> "$WORK/list.txt"; done
echo "file '$ABS/hero.mp4'" >> "$WORK/list.txt"
for f in "$WORK"/s*.mp4; do echo "file '$PWD/$f'" >> "$WORK/list.txt"; done
ffmpeg -y -v error -f concat -safe 0 -i "$WORK/list.txt" -c copy "$WORK/video.mp4"

VDUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$WORK/video.mp4")
FADE=$(python3 -c "print($VDUR-3)")
ffmpeg -y -v error -i "$WORK/video.mp4" -i "$SRC/Aura.mp3" \
  -filter_complex "[0:v]fade=t=in:d=1.5,fade=t=out:st=$FADE:d=3[v];[1:a]atrim=0:$VDUR,afade=t=in:d=2,afade=t=out:st=$FADE:d=3[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 19 -c:a aac -b:a 192k -shortest "$OUT"

echo "DONE: $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s, $(du -h "$OUT" | cut -f1))"
