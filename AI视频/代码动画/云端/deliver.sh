#!/bin/bash
# 把成片交给用户：传到 GitHub 的「草稿 Release」（只有仓库主人看得到，不公开，也不进 git 历史）。
# 用法：bash AI视频/代码动画/云端/deliver.sh <片目录> <版本>，例如 deliver.sh AI视频/代码动画/雪花变画 v1
# 传三样：原画质成片、720p 小样（手机上看）、片目录里的封面 jpg。同名的草稿已经存在就往里面加文件（同名文件先删再传）。
set -euo pipefail
DIR=$(cd "$1" && pwd); VER=$2
NAME=$(basename "$DIR")
REPO=$(git -C "$DIR" remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')
MP4="$DIR/${NAME}_${VER}.mp4"
[ -f "$MP4" ] || cp "$DIR/film/out/video.mp4" "$MP4"
PREV="$DIR/film/out/preview_720p.mp4"
ffmpeg -v error -y -i "$MP4" -vf scale=-2:720 -c:v libx264 -preset veryfast -crf 26 -c:a aac -b:a 128k -movflags +faststart "$PREV"

TAG="film-$(date +%Y%m%d)-$VER"
TITLE="《$NAME》$VER"
ID=$(gh api "repos/$REPO/releases?per_page=50" --jq ".[] | select(.draft and .name == \"$TITLE\") | .id" | head -1)
[ -n "$ID" ] || ID=$(gh api -X POST "repos/$REPO/releases" -f tag_name="$TAG" -f name="$TITLE" -F draft=true \
  -f body="代码动画《$NAME》$VER。原画质成片、720p 小样、封面。草稿只有仓库主人看得到。" --jq .id)

# 附件名用英文（GitHub 会把中文文件名改成点）
upload() {   # 本地文件 附件名 类型
  local old; old=$(gh api "repos/$REPO/releases/$ID/assets" --jq ".[] | select(.name == \"$2\") | .id")
  [ -z "$old" ] || gh api -X DELETE "repos/$REPO/releases/assets/$old" >/dev/null
  gh api -X POST "https://uploads.github.com/repos/$REPO/releases/$ID/assets?name=$2" -H "Content-Type: $3" --input "$1" --jq .name
}
upload "$MP4" "video-$VER.mp4" video/mp4
upload "$PREV" "preview-720p-$VER.mp4" video/mp4
for c in "$DIR"/封面_*横*.jpg; do [ -f "$c" ] && upload "$c" "cover-landscape-$VER.jpg" image/jpeg; done
for c in "$DIR"/封面_*竖*.jpg; do [ -f "$c" ] && upload "$c" "cover-portrait-$VER.jpg" image/jpeg; done
echo "草稿 Release：https://github.com/$REPO/releases （登录 GitHub 后在 Releases 页能看到草稿，点附件下载）"
