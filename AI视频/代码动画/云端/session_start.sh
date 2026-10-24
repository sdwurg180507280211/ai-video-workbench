#!/bin/bash
# 云端会话启动时由仓库的 .claude/settings.json（SessionStart hook）调用；在本机（没有 CLAUDE_CODE_REMOTE=true）直接退出。
# 让云端和 Mac 用同一套路径：~/ideaProjects/my-skills、~/ideaProjects/mg-styles-15，
# 每支片目录下的 lib、.venv、node_modules。打印的检查结果会进 Claude 的上下文。
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
SKILLS_REPO=sdwurg180507280211/my-skills
mkdir -p ~/ideaProjects

# 环境没配安装脚本（或缓存过期没装上）时，在这里补装一遍：慢几分钟，但能跑
if [ ! -e /opt/chrome ] || [ ! -x /opt/venv-video/bin/python ]; then
  echo "[session] 没找到 Chrome 或 Python 库，现在运行 setup.sh 补装（建议把它贴进环境的 Setup script，就不用每次装）"
  bash "$ROOT/AI视频/代码动画/云端/setup.sh" 2>&1 | grep '^\[setup\]' || echo "[session] setup.sh 有失败的步骤"
fi

# 视频技能每次会话拉最新的：先 git，不行就按清单从 raw.githubusercontent.com 下载
fetch_skill_raw() {
  local base="https://raw.githubusercontent.com/$SKILLS_REPO/main/skills/opus-code-video" f
  for f in SKILL.md references/narration.md references/publish.md references/render-and-qc.md \
           scripts/cutout.py scripts/doubao_tts.py scripts/mix_voice.py scripts/new_project.sh scripts/qc.py scripts/retime.py \
           styles/sticker-explainer/README.md; do
    mkdir -p "/opt/my-skills/skills/opus-code-video/$(dirname "$f")"
    curl -fsSL -A xiaotuanzi-routine/1 "$base/$f" -o "/opt/my-skills/skills/opus-code-video/$f" || echo "[session] 下载失败 $f"
  done
  local rs=/opt/my-skills/skills/seedance-short-drama/scripts/review_script.py   # 剧本审稿（DeepSeek）
  mkdir -p "$(dirname "$rs")" && curl -fsSL -A xiaotuanzi-routine/1 "https://raw.githubusercontent.com/$SKILLS_REPO/main/skills/seedance-short-drama/scripts/review_script.py" -o "$rs" || echo "[session] 下载失败 review_script.py"
}
if [ -d /opt/my-skills/.git ]; then git -C /opt/my-skills pull -q --ff-only 2>/dev/null || true
else rm -rf /opt/my-skills; git clone -q --depth 1 "https://github.com/$SKILLS_REPO" /opt/my-skills 2>/dev/null || fetch_skill_raw; fi
[ -e ~/ideaProjects/my-skills ] || ln -s /opt/my-skills ~/ideaProjects/my-skills

# mgaudio：环境安装脚本没装上的话这里补
[ -d /opt/mg-styles-15/lib/audio ] || { git clone -q --depth 1 --filter=blob:none --sparse https://github.com/Vincentwei1021/mg-styles-15 /opt/mg-styles-15 \
  && git -C /opt/mg-styles-15 sparse-checkout set lib/audio; }
[ -e ~/ideaProjects/mg-styles-15 ] || ln -s /opt/mg-styles-15 ~/ideaProjects/mg-styles-15

# 每支片：lib → mgaudio，.venv → /opt/venv-video，node_modules 按 package.json 装
for pkg in "$ROOT"/AI视频/代码动画/*/package.json; do
  d=$(dirname "$pkg")
  [ -e "$d/lib" ] || [ -L "$d/lib" ] || ln -s ~/ideaProjects/mg-styles-15/lib "$d/lib"   # -L：目标还没装好的软链接也算已有
  [ -e "$d/.venv" ] || [ -L "$d/.venv" ] || ln -s /opt/venv-video "$d/.venv"
  [ -d "$d/node_modules" ] || (cd "$d" && npm install --no-package-lock --no-audit --no-fund --loglevel=error >/dev/null 2>&1) || echo "[session] npm install 失败：$d"
done

ok() { [ "$1" ] && echo "有" || echo "缺"; }
echo "[session] 视频制作环境：ffmpeg $(ok "$(command -v ffmpeg)")，Chrome $(ok "$(ls /opt/chrome 2>/dev/null)")，" \
     "Python 库 $(ok "$(ls /opt/venv-video/bin/python 2>/dev/null)")，mgaudio $(ok "$(ls -d /opt/mg-styles-15/lib/audio 2>/dev/null)")，" \
     "视频技能 $(ok "$(ls ~/ideaProjects/my-skills/skills/opus-code-video/SKILL.md 2>/dev/null)")；" \
     "IMAGE_API_KEY $(ok "${IMAGE_API_KEY:-}")，DOUBAO_SPEECH_API_KEY $(ok "${DOUBAO_SPEECH_API_KEY:-}")，DEEPSEEK_API_KEY $(ok "${DEEPSEEK_API_KEY:-}")。做片前先读 AI视频/代码动画/云端/README.md"
exit 0
