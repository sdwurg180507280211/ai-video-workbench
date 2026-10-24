# 在 Claude 云端会话里做代码动画

代码动画的整条流程（配音、节拍、画面、配乐、渲染、质检、交付）都能在 claude.ai/code 的云端会话里跑，不用 Mac 开着。
本地 Mac 上照旧能做，两边用的是同一个仓库、同一套路径。

## 一次性设置（用户在 claude.ai/code 里做）

1. GitHub：Claude GitHub App 要有 `ai-video-workbench` 的权限（https://github.com/settings/installations → Claude → Configure）。
2. 新建环境「视频制作」：
   - **Network access**：Full。
   - **Environment variables**（值自己粘贴，不要写进文件或聊天）：
     ```
     IMAGE_API_KEY=…            # 生图网关，和公众号环境同一个
     IMAGE_API_BASE=https://yunyihui.mystic.net.cn/image-api/v1
     DOUBAO_SPEECH_API_KEY=…    # 豆包语音，Mac 上 ~/.config/volc-speech/api-key
     DEEPSEEK_API_KEY=…         # 剧本审稿，Mac 上 ~/.config/deepseek/api-key
     BASH_DEFAULT_TIMEOUT_MS=600000
     BASH_MAX_TIMEOUT_MS=3600000
     ```
   - **Setup script**：整段贴 [setup.sh](setup.sh)。
3. 开会话时仓库选 `ai-video-workbench`，环境选「视频制作」。

## 每次会话自动做的事

仓库的 `.claude/settings.json` 在会话启动时运行 [session_start.sh](session_start.sh)（本机不运行）：

- 拉最新的视频技能到 `~/ideaProjects/my-skills`。
- 把 mgaudio 链接到 `~/ideaProjects/mg-styles-15`。
- 给每支片目录建 `lib`、`.venv`，再装 `node_modules`。
- 最后打印一行检查结果：哪样缺了就先修，不要直接开工。

所以片子 `交接.md` 里「怎么跑」的命令在云端照样能用。Mac 专用的那行 `export PATH=…` 在云端无害，可以照抄。

## 云端和本机不一样的地方

- **工作目录**是仓库里的 `AI视频/代码动画/<片名>/`，不是 Mac 的 `~/Downloads/AI视频/…`。改完要提交并推送，Mac 上 `git pull` 才看得到。
- **渲染**：云端没有显卡，Chrome 用软件渲染，可能比 Mac 慢。整片渲染放后台跑，日志写进文件再轮询，别挂在前台命令上：
  ```bash
  nohup node harness/render.mjs film --mb 8 --workers 4 > film/out/render.log 2>&1 &
  ```
  进度看 `tail -1 film/out/render.log`。渲染期间每隔几分钟看一次，会话就不算闲置。
- **生图网关**：用 `IMAGE_API_BASE`，curl 要加 `-A xiaotuanzi-routine/1`。网关只接受 `size=auto`、`quality=auto`。
- **成片不进 git**（`.gitignore` 忽略了 mp4、wav、`film/out/`）。交付用 [deliver.sh](deliver.sh)：
  ```bash
  bash AI视频/代码动画/云端/deliver.sh AI视频/代码动画/雪花变画 v1
  ```
  它会把原画质成片、720p 小样和封面传到 GitHub 的草稿 Release，只有仓库主人看得到。用户在仓库的 Releases 页下载。
- **要提交的**：画面代码、节拍、配乐脚本、配音 mp3（`voice/lines/` 已在 `.gitignore` 里放行）、新贴纸、封面插画原图、封面 jpg、`交接.md`、`作品.json`。
- **密钥**：只报告「有」或「没有」，不打印，不写进文件，不 `set -x`。

## 每日定时任务

每天全自动做一支片（用户 2026-10-24 授权，不等批稿），提示词和设置见 [每日定时任务.md](每日定时任务.md)，选题见 [../选题清单.md](../选题清单.md)。

## 共用的东西

- `AI视频/代码动画/共用/fonts/`：各片的 `assets/fonts` 是指向这里的软链接（OFL 字体）。
- `AI视频/共用/小团子AI素材/`：小团子贴纸库、`抠图.py`、`素材清单.md`。新动作出好以后收进这里并登记。
