#!/bin/bash
# 「视频制作」云端环境的安装脚本：整段贴进 claude.ai/code → 环境 →「Setup script」。
# 以 root 在 Ubuntu 24.04 上跑；跑完 Anthropic 会把磁盘快照缓存约 7 天，之后的新会话直接用，不用再装。
# 要在约 5 分钟内跑完才会缓存，所以几样东西并行装。
# 装：ffmpeg 和 Chrome 依赖库、Chrome for Testing（/opt/chrome）、配乐用的 Python 库（/opt/venv-video）、
#     mg-styles-15 的 mgaudio 和音色采样（/opt/mg-styles-15）。
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
pids=()

( apt-get update -qq && apt-get install -y -qq --no-install-recommends ffmpeg \
    libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxrandr2 libxfixes3 libgbm1 libpango-1.0-0 libcairo2 libasound2t64 libdrm2 libxshmfence1 >/dev/null \
  && echo "[setup] apt ok" ) & pids+=($!)

( cd /tmp && npx -y @puppeteer/browsers install chrome@stable --path /opt/chrome-cft >/dev/null \
  && ln -sfn "$(ls -d /opt/chrome-cft/chrome/linux-*/chrome-linux64 | tail -1)/chrome" /opt/chrome \
  && echo "[setup] chrome ok" ) & pids+=($!)

# 版本和 mg-styles-15 的 requirements.txt 一致（验证过）；装不上时退回不锁版本
( python3 -m venv /opt/venv-video \
  && { /opt/venv-video/bin/pip install -q numpy==2.4.6 scipy==1.16.3 soundfile==0.14.0 numba==0.66.0 pedalboard==0.9.25 \
         pyloudnorm==0.2.0 matplotlib==3.9.1 librosa==0.11.0 pillow==12.3.0 \
       || /opt/venv-video/bin/pip install -q numpy scipy soundfile numba pedalboard pyloudnorm matplotlib librosa pillow; } \
  && echo "[setup] python ok" ) & pids+=($!)

( git clone -q --depth 1 --filter=blob:none --sparse https://github.com/Vincentwei1021/mg-styles-15 /opt/mg-styles-15 \
  && git -C /opt/mg-styles-15 sparse-checkout set lib/audio && echo "[setup] mgaudio ok" ) & pids+=($!)

fail=0
for p in "${pids[@]}"; do wait "$p" || fail=1; done
exit $fail
