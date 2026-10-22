# AI短剧开源项目

> 原调研与数据快照：2026-10-18。原表收录 **43 个项目**：34 个视频制作相关项目，9 个通用 AI / Agent / 自动化配套项目。本文采用宽口径收录，同时明确区分标准开源许可、开放权重和“仅源码可用 / 自定义许可”。
>
> 目标：找到适合制作 30–60 秒 AI 短剧、漫剧、科普剧情片的工具，并保留后续扩展为自动生产流程的路径。所有能力描述主要来自官方仓库、README 和许可文件，**不代表已经安装、跑通或对成片质量做过实测**。

> **2026-10-21 增补**：新增2个GitHub项目、2条X链接，见第9节。原43项热度表仍为10月18日快照，未在此次整体刷新。

## 1. 先看结论：从哪里开始

短剧制作需要完成“剧本 → 角色/场景资产 → 分镜 → 画面生成 → 对白/口型 → 剪辑/字幕/配乐 → 审片”。单个项目可能只覆盖其中一部分。

- **想用类似 LibTV 的画布组织短剧**：先看 **Toonflow**；如果重视镜头连续性、任务恢复和剪映交付，再看 **ArcReel**。
- **想让 Agent 参与导演和生产流程**：先看 **OpenMontage**，研究多 Agent 协作再看 **ViMax**。
- **想尽快生成科普、故事解说或旁白型短视频**：先看 **Pixelle-Video、MoneyPrinterTurbo**。它们适合验证文案、画面、配音和字幕流水线，多角色表演仍需额外审核。
- **想控制模型、显存、节点和特殊效果**：再进入 **ComfyUI + Wan / 其他视频模型**。这一条路线自由度高，也需要更多配置与排错。
- **想补人物对白和口型**：研究 **GPT-SoVITS / CosyVoice + MuseTalk**；人物表情驱动可看 **LivePortrait**。
- **想做自动化批量生产**：在已经跑通单条视频的基础上，加 n8n / LangGraph 等工具处理排队、审核和归档。

实际建议：先选择一个工作台，接入一种图像模型和一种视频模型，用少量镜头完成一条样片，再决定是否增加本地模型、复杂 Agent 和自动化。

### 1.1 优先研究的 7 个项目

这是按短剧相关性与上手价值筛选的候选清单，**不是 GitHub 全站 Stars 前七名，也不是增长速度榜**。

| 项目 | 为什么优先看 | 适用边界 |
| --- | --- | --- |
| [Toonflow](https://github.com/HBAI-Ltd/Toonflow-app) | 无限画布、剧本、分镜和资产管理，贴近短剧工作台需求 | 生成能力与所接模型有关；不要把画布整理直接等同于完整剪辑交付 |
| [ArcReel](https://github.com/ArcReel/ArcReel) | 生产资产、连续性、成本追踪、任务恢复与剪映草稿 | 需核对 AGPL 与 NOTICE；CapCut 兼容性尚未获官方验证 |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | 从调研、提案到合成的 Agent 导演流程，便于研究分阶段审核 | 需要 Agent、模型及合成环境；原创镜头可能产生模型费用 |
| [ViMax](https://github.com/HKUDS/ViMax) | 创意/脚本转视频的多 Agent 流程，有候选镜头筛选思路 | 多候选、多模型调用会增加成本；应先跑小样 |
| [Pixelle-Video](https://github.com/ATH-MaaS/Pixelle-Video) | 自动生成画面、旁白与配乐，适合快速验证故事解说样片 | 多角色对白、连续表演和精确调度需要人工控制 |
| [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | 高热度自动成片方案，素材、生成片段、配音字幕组合灵活 | 更适合内容流水线；剧情表演质量仍取决于镜头生成和审核 |
| [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | 大量模型与节点生态，可精细控制图像、视频及后处理 | 它是工作流工具；需要自己组织短剧流程，配置成本较高 |

## 2. “爆火”的统计口径

- **热度指标**：GitHub API 的累计 `stargazers_count`，取本次调研快照；下表各分类内按 Stars 从高到低排列。
- **活跃度辅助指标**：API 的 `pushed_at` 日期，仅说明仓库最近有推送，不能证明最新稳定版已经发布、问题响应及时或生产可用。
- **收录方法**：从短剧/漫剧工作台、自动成片、多模型视频应用、视频模型、口型配音，以及通用 Agent/工作流等方向搜集候选，再检查相关项目官方资料。
- **局限**：没有保存连续多日 Stars，因此不声称“近期涨星最快”；也没有穷尽 GitHub 全站。累计 Stars 会受项目年龄、传播和社区影响，不能直接代表画质、性价比或可用率。
- **许可证口径**：API 的 license 字段只是线索。代码、模型权重、预训练组件、声音、字体、音乐和素材可能各有条件，商用应以拟采用版本的实际许可为准。
- 下表中非商业、自定义、品牌限制等项目仍保留，方便比较，但不能据此称它们全部是可自由商用的标准开源项目。

## 3. 分类项目库

表中 Stars、最近推送为同一调研日获取的数据；“依赖”是选择路线时的提示，具体安装命令与支持平台以项目当前文档为准。项目名链接均指向官方仓库，可从 README 查看演示、部署方法及许可入口。

### 3.1 短剧、漫剧与导演工作台（10 个）

| 项目 | Stars | 核心用途 | 运行条件 / 主要依赖 | 许可提示 | 最近推送 |
| --- | ---: | --- | --- | --- | --- |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | 69,403 | Agent 驱动的调研、脚本、分镜、素材和合成 | 需配置 Agent/模型与渲染环境；原创画面另计费 | AGPL-3.0 | 2026-10-16 |
| [HBAI-Ltd/Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | 18,089 | 无限画布式短剧/漫剧工作台，管理剧本、分镜和角色资产 | 本地/客户端；生图生视频依赖所接模型 | MIT | 2026-10-16 |
| [chatfire-AI/huobao-drama](https://github.com/chatfire-AI/huobao-drama) | 16,342 | 火宝短剧：剧本、角色、分镜生成及剧集合成 | 全栈应用/桌面端；模型 API、FFmpeg | CC BY-NC-SA 4.0；非商业限制 | 2026-10-05 |
| [waooAI/waoowaoo](https://github.com/waooAI/waoowaoo) | 14,578 | Assistant + 图像/视频画布；当前预览功能需按 README 判断 | 推荐 Docker；主要配置 OpenRouter 等模型服务 | Elastic License 2.0；源码可用 | 2026-09-21 |
| [HKUDS/ViMax](https://github.com/HKUDS/ViMax) | 12,683 | 多 Agent 将创意、脚本转为视频 | 多种模型服务；候选图与视觉筛选增加成本 | MIT | 2026-09-30 |
| [Forget-C/Jellyfish](https://github.com/Forget-C/Jellyfish) | 6,765 | 人物、服装、场景、道具资产与镜头生成管理 | Docker；图像/视频模型 API；异步任务 | Apache-2.0 | 2026-07-30 |
| [ArcReel/ArcReel](https://github.com/ArcReel/ArcReel) | 5,564 | 短剧生产资产、连续性、成本和剪映草稿导出 | 本地部署及模型服务；需检查 NOTICE | AGPL-3.0 + NOTICE 条款 | 2026-10-18 |
| [yi1108/printfilm](https://github.com/yi1108/printfilm) | 5,177 | 模板化 AI 视频生产与模型路由 | Docker、PostgreSQL、Redis、模型 API | MIT | 2026-10-15 |
| [MemeCalculate/moyin-creator](https://github.com/MemeCalculate/moyin-creator) | 4,727 | 魔因：剧本、角色、场景、导演与多镜头生成 | 图像/视频 API；含 Seedance 工作流 | AGPL-3.0 / 商业双许可 | 2026-08-27 |
| [FireRedTeam/FireRed-OpenStoryline](https://github.com/FireRedTeam/FireRed-OpenStoryline) | 3,529 | 对话式视频剪辑 Agent，支持可复用剪辑 Skills | 素材、ASR 和模型配置；侧重剪辑 | Apache-2.0 | 2026-07-31 |

### 3.2 自动成片与多模型应用（6 个）

| 项目 | Stars | 核心用途 | 运行条件 / 主要依赖 | 许可提示 | 最近推送 |
| --- | ---: | --- | --- | --- | --- |
| [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | 132,609 | 文案、素材/生成视频、配音、字幕、配乐自动成片 | FFmpeg；LLM/素材源/TTS；生成模型另计费 | MIT | 2026-10-17 |
| [Anil-matcha/Open-Generative-AI](https://github.com/Anil-matcha/Open-Generative-AI) | 30,738 | 多模型图像/视频创作工作室 | 云端快速上手需 MuAPI Key；本地引擎另配 | MIT | 2026-10-15 |
| [ATH-MaaS/Pixelle-Video](https://github.com/ATH-MaaS/Pixelle-Video) | 29,136 | 图文/生成片段、旁白和 BGM 的自动视频工作流 | uv、FFmpeg、Streamlit；ComfyUI/RunningHub 或模型 API | Apache-2.0 | 2026-06-14 |
| [hypit-ai/hypit](https://github.com/hypit-ai/hypit) | 23,385 | 用 Agent 和 SVML 编辑视频，可用模板/参考/创作简报 | 编码 Agent、渲染与可选生成模型；费用分别计算 | Hypit 自定义许可 | 2026-10-15 |
| [krillinai/OpenCreator](https://github.com/krillinai/OpenCreator) | 13,666 | 由 KrillinAI 演进的视频创作者工作台 | 按当前版本核对模型/服务和部署要求 | Apache-2.0 | 2026-10-18 |
| [mutonby/openshorts](https://github.com/mutonby/openshorts) | 6,802 | 从已有长视频提取短视频 | 需要源视频；不能替代原创剧情生成 | MIT | 2026-10-17 |

### 3.3 视频模型与推理（7 个）

| 项目 | Stars | 核心用途 | 运行条件 / 主要依赖 | 许可提示 | 最近推送 |
| --- | ---: | --- | --- | --- | --- |
| [hpcaitech/Open-Sora](https://github.com/hpcaitech/Open-Sora) | 29,869 | 视频生成研究与推理/训练框架 | 高显存 NVIDIA/服务器路线；不适合普通 Mac 快速试片 | Apache-2.0（代码）；权重另核 | 2026-04-09 |
| [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) | 18,001 | 文生/图生视频模型系列 | 按 5B/A14B、分辨率和卸载设置区分显存 | Apache-2.0（代码）；权重另核 | 2026-09-21 |
| [Wan-Video/Wan2.1](https://github.com/Wan-Video/Wan2.1) | 17,235 | 成熟的视频生成模型及生态 | 通常配合 NVIDIA GPU、ComfyUI/推理工具 | Apache-2.0（代码）；权重另核 | 2026-03-05 |
| [zai-org/CogVideo](https://github.com/zai-org/CogVideo) | 13,085 | CogVideoX 等视频生成模型与推理示例 | GPU、模型权重及版本对应环境 | Apache-2.0（代码）；权重另核 | 2025-11-04 |
| [Tencent-Hunyuan/HunyuanVideo](https://github.com/Tencent-Hunyuan/HunyuanVideo) | 12,631 | 混元视频生成模型与技术实现 | GPU/显存门槛依具体模型；权重许可需单独读 | 自定义许可；分代码/权重核对 | 2026-10-08 |
| [deepbeepmeep/WanGP](https://github.com/deepbeepmeep/WanGP) | 10,634 | 多模型视频推理工具及显存优化，原 Wan2GP | 主要面向 GPU 推理；低显存不等于低耗时 | 自定义/其他；按组件核对 | 2026-10-17 |
| [Lightricks/LTX-2](https://github.com/Lightricks/LTX-2) | 9,782 | LTX 视频模型与推理，README 含 LTX-2.5 模型入口 | 按所选模型、推理后端和硬件评估 | 自定义/其他；代码/权重分别核对 | 2026-10-13 |

### 3.4 工作流、视频控制与渲染（4 个）

| 项目 | Stars | 核心用途 | 运行条件 / 主要依赖 | 许可提示 | 最近推送 |
| --- | ---: | --- | --- | --- | --- |
| [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | 138,253 | 节点式生成工作流，可串联图像、视频及各类模型 | 本地推理取决于 GPU/模型；也可接远端服务 | GPL-3.0 | 2026-10-18 |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | 64,927 | 用 React 编程生成视频、字幕、动画和模板 | Node.js/浏览器渲染；公司使用需核对授权条件 | Remotion 自定义许可 | 2026-10-18 |
| [modelscope/DiffSynth-Studio](https://github.com/modelscope/DiffSynth-Studio) | 13,258 | 生成模型的推理、训练及工作流工具 | 偏开发者/GPU；依模型加载权重 | Apache-2.0 | 2026-10-16 |
| [ali-vilab/VACE](https://github.com/ali-vilab/VACE) | 3,981 | 视频编辑与内容控制模型框架 | GPU、支持的基座模型和输入条件 | Apache-2.0（代码）；权重另核 | 2025-10-17 |

### 3.5 声音、口型、表情与字幕（7 个）

| 项目 | Stars | 核心用途 | 运行条件 / 主要依赖 | 许可提示 | 最近推送 |
| --- | ---: | --- | --- | --- | --- |
| [RVC-Boss/GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) | 63,099 | 少样本语音克隆与 TTS，中文配音候选 | 参考音频、模型和算力；各依赖许可另核 | MIT（代码） | 2026-10-18 |
| [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp) | 54,464 | 本地语音识别，适合字幕初稿和转写 | CPU/Apple Silicon 等后端；需下载模型 | MIT | 2026-10-12 |
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | 25,934 | 基于 CTranslate2 的高效 Whisper 转写 | CPU/NVIDIA；性能随模型和硬件变化 | MIT | 2026-10-16 |
| [QwenAudio/CosyVoice](https://github.com/QwenAudio/CosyVoice) | 24,027 | 多语言语音生成与声音参考 | 模型下载、推理环境及组件许可 | Apache-2.0（代码）；权重另核 | 2026-05-25 |
| [KlingAIResearch/LivePortrait](https://github.com/KlingAIResearch/LivePortrait) | 19,257 | 单图/视频的人像表情和头部动作驱动 | Apple Silicon 有官方说明；Intel Mac 未经官方测试 | 仓库标记 other；组件单独核对 | 2026-06-01 |
| [Rudrabha/Wav2Lip](https://github.com/Rudrabha/Wav2Lip) | 13,244 | 用音频驱动已有视频口型 | 需视频与语音；旧开源模型限制商用 | 旧开放模型限研究/个人/非商业 | 2025-06-22 |
| [TMElyralab/MuseTalk](https://github.com/TMElyralab/MuseTalk) | 6,740 | 音频驱动的人脸口型同步 | 需人脸视频/图像与音频；组件和测试数据许可另核 | 代码 MIT；官方声明训练模型可商用 | 2025-09-26 |

### 3.6 GitHub 高热度通用 AI 配套（9 个）

这些项目本身通常不生成完整短剧，主要用于创作入口、资料检索、编排或二次开发。将它们单列，避免用通用 AI 项目的高 Stars 混淆视频工具排名。

| 项目 | Stars | 核心用途 | 运行条件 / 主要依赖 | 许可提示 | 最近推送 |
| --- | ---: | --- | --- | --- | --- |
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | 207,886 | 工作流自动化：排队、回调、素材归档等 | 自托管/云；生成 API 单独计费 | Sustainable Use / 企业许可；fair-code | 2026-10-18 |
| [ollama/ollama](https://github.com/ollama/ollama) | 183,706 | 本地运行语言模型，可辅助剧本与素材标注 | 本地内存/模型文件；它本身不负责生成短剧 | MIT 软件；模型许可另核 | 2026-10-18 |
| [langgenius/dify](https://github.com/langgenius/dify) | 158,779 | 可视化 LLM 应用与工作流平台 | 服务部署、LLM API；适合流程与知识库 | 修改版 Apache-2.0，含附加条件 | 2026-10-18 |
| [open-webui/open-webui](https://github.com/open-webui/open-webui) | 156,057 | 自托管 AI 对话与模型入口 | 接本地/远端模型；适合统一创作入口 | 自定义许可，含品牌限制 | 2026-10-16 |
| [langflow-ai/langflow](https://github.com/langflow-ai/langflow) | 155,798 | 可视化 Agent/LLM 流程开发 | Python/服务环境与模型接口 | MIT | 2026-10-18 |
| [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | 148,021 | 构建模型调用、工具和 RAG 的开发框架 | 需要编程；用于二次开发 | MIT | 2026-10-18 |
| [infiniflow/ragflow](https://github.com/infiniflow/ragflow) | 92,415 | 文档理解与 RAG 知识库 | 服务部署、文档处理、检索和模型资源 | Apache-2.0 | 2026-10-17 |
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | 91,189 | 软件开发 Agent，可辅助搭建/改造创作工具 | 运行沙箱和模型；不直接承担视频生成 | MIT（仓库主许可）；组件另核 | 2026-10-17 |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 43,441 | 有状态、多步骤 Agent 工作流开发 | 需要编程；可管理审核、重试和任务状态 | MIT | 2026-10-18 |

## 4. 重点项目：能力、缺口和试用顺序

### 4.1 Toonflow：最贴近画布式短剧工作台的候选

[官方 README](https://github.com/HBAI-Ltd/Toonflow-app#readme)展示剧本创作、智能分镜、角色/场景资产、图像生成、视频生成及无限画布，也提供 Agent、MCP 和插件扩展方向。

它的价值主要是把人物、场景、参考图和镜头关系组织起来，减少散落在多个网页和文件夹中的状态。对需要重复生成同一人物、替换某个镜头的短剧，这比单独一个文生视频输入框更有帮助。

试用时重点验证：角色参考是否能传给实际生成服务、失败任务如何重试、素材能否方便下载和复用。README 中的预览、整理、下载能力，应与完整时间线剪辑、声音混音和最终导出分开核验。

### 4.2 ArcReel：关注连续生产和剪映交付

[官方 README](https://github.com/ArcReel/ArcReel#readme)强调生产资产、角色一致性管理、成本追踪、任务恢复，以及视频合成和**剪映草稿导出**。

这类能力更接近“连续做多集”的需求。选型时应检查失败任务是否复用已有素材、镜头编号是否稳定、重抽后是否容易替换，以及导出的草稿能否在目标剪映版本正常打开。

官方注明 CapCut 兼容性尚未验证，不能把中文剪映支持直接推广到所有海外客户端。许可也要一起阅读 AGPL 和仓库 NOTICE。

### 4.3 OpenMontage：把 Agent 当导演的参考实现

[官方 README](https://github.com/calesthio/OpenMontage#readme)将流程拆为调研、提案、剧本、场景计划、素材、编辑和合成，并提供审核检查点及预算控制。合成路线涉及 Remotion、HyperFrames 或 FFmpeg。

值得参考的是中间产物和审核点：剧本不满意时先改剧本，分镜不合理时先改分镜，避免直接消耗视频生成预算。

可以使用已有/素材库视频进行合成；需要原创人物和剧情镜头时，仍然需要生成模型服务或本地算力。使用 Remotion 等下游工具时也应核对各自许可。

### 4.4 ViMax：研究多 Agent 的剧本到视频流程

[官方 README](https://github.com/HKUDS/ViMax#readme)覆盖创意/脚本到视频的多 Agent 协作。仓库中文说明文件为 `README_ZH.md`，另有 `readme.md`。

默认流程包含生成两张关键帧候选，再由视觉模型选择。这是提高候选质量的一种做法，同时会增加图像、视觉理解等调用开销。评估时要统计整条任务的总费用，不能只算最终那一条视频 API 请求。

适合希望理解或改造生产流水线的开发者；对一次 30 秒样片，先压缩镜头数量和候选数量更容易定位问题。

### 4.5 Pixelle-Video：快速验证旁白型视频

[官方 README](https://github.com/ATH-MaaS/Pixelle-Video#readme)给出 uv、FFmpeg、Streamlit 路线，Web 启动入口为：

```bash
uv run streamlit run web/app.py
```

图像/视频生成可以接 ComfyUI、RunningHub，也可配置直接模型 API；不是每个使用方式都必须在本机完整运行 ComfyUI。项目涉及画面、旁白、BGM 合成，也有数字人/动作迁移相关模块。

更适合先做故事旁白、科普、图像动态化和自动成片验证。如果目标是两个人自然对话、相互看向对方、边操作边说话，应单独测试角色一致性、口型和镜头连续性。

以上命令来自项目说明，本文没有据此声称已完成安装或启动。

### 4.6 MoneyPrinterTurbo：自动内容生产的成熟候选

[官方 README](https://github.com/harry0703/MoneyPrinterTurbo#readme)覆盖文案、素材、配音、字幕、配乐，并提供 CLI/API/Agent 等入口。当前项目也支持生成视频，包括对接火山方舟 Seedance 等路线。

因此不能简单把它归类为“只能拼接素材的视频工具”。更合适的评价是：它侧重自动成片流水线，能否得到自然、连续的剧情表演，依然取决于所接模型、输入资产和审片机制。

如果目标是批量科普、故事解说或资讯短视频，它比自行搭建所有模块更值得先试。若目标是强表演的短剧，要额外检查对白节奏和动作连贯性。

### 4.7 ComfyUI：自由度高，适合第二阶段

[官方 README](https://github.com/Comfy-Org/ComfyUI#readme)与节点生态可连接图像生成、参考控制、视频生成及后处理。工作流文件能保存参数和节点关系，便于重复制作。

但“工作流可复用”不等于“角色、声音和剧情会自动连续”。模型、节点版本、权重、显存和工作流参数仍需维护。建议先在简单流程中确定可用画面，再把真正需要的部分搬进 ComfyUI。

### 4.8 其他短剧工作台的观察点

| 项目 | 值得研究的部分 | 当前需要特别核对 |
| --- | --- | --- |
| [火宝短剧](https://github.com/chatfire-AI/huobao-drama#readme) | 参考图、分镜生成、FFmpeg 剧集合并；有 Mac Intel/ARM 桌面入口 | 当前项目为 TypeScript 全栈路线；CC BY-NC-SA 的非商业限制影响商用选择 |
| [waoowaoo](https://github.com/waooAI/waoowaoo#readme) | Assistant 和图像/视频画布；Docker 部署 | 当前预览 README 明确表示没有音乐/配音控制；不要照搬旧版本“全自动全流程”的宣传；ELv2 为源码可用许可 |
| [Jellyfish](https://github.com/Forget-C/Jellyfish#readme) | 人物、服装、场景、道具资产，镜头候选复用与异步任务 | API 适配、任务恢复及最终交付链路需要实测 |
| [魔因 Moyin](https://github.com/MemeCalculate/moyin-creator#readme) | 剧本 → 角色 → 场景 → 导演，多镜头分组与 Seedance 工作流 | 模型接入条件、AGPL/商业双许可适用方式 |
| [PRINTFILM](https://github.com/yi1108/printfilm#readme) | 模板化生产、模型路由、应用级部署 | 依赖 PostgreSQL、Redis 等服务，不是下载一个模型即可运行 |
| [OpenStoryline](https://github.com/FireRedTeam/FireRed-OpenStoryline#readme) | 对话式剪辑、可复用编辑 Skills、ASR 辅助粗剪 | 重点是编辑已有素材；原创镜头仍要另行生成 |

## 5. 几个容易混淆的地方

### 5.1 开源应用与免费生成是两件事

Open-Generative-AI 的云端快速开始需要 MuAPI Key；本地图像路线涉及 sd.cpp，视频还需要单独配置本地或远端 WanGP。Hypit 的编码 Agent、生成模型和渲染也可能分别产生费用。

自托管可以掌握界面、流程和素材，但如果底层仍接付费模型，每次生成、重试、超分和配音依然可能收费。反过来，本地模型减少 API 支出，也会增加显卡、云 GPU、维护和等待成本。

### 5.2 MuseTalk、Muse 产品和 LivePortrait 不要混用概念

- **MuseTalk** 是音频驱动的口型同步项目，不等同于名称含 Muse 的网页创作产品。官方说明代码为 MIT、训练模型可商用，但外部组件和测试数据另有许可。
- **LivePortrait** 主要处理人像表情、头部动作等驱动，不是完整短剧制作引擎，也不能直接等同于完整对白口型方案。官方说明支持 Apple Silicon，Intel Mac 未经官方测试。
- **Wav2Lip** 的旧开放模型有研究、个人、非商业限制；不能把另一个收费商用服务的授权理解成旧仓库模型自动可商用。
- **Whisper / faster-whisper / whisper.cpp** 负责语音识别与转写，不能直接替代 TTS 配音或视频生成。

参考：[MuseTalk](https://github.com/TMElyralab/MuseTalk#readme)、[LivePortrait](https://github.com/KlingAIResearch/LivePortrait#readme)、[Wav2Lip](https://github.com/Rudrabha/Wav2Lip#readme)。

### 5.3 “本地可运行”需要具体到型号、模型和参数

- **Open-Sora** 是研究/服务器级路线。官方文档中 H100/H800 测试示例，256px 单卡推理峰值显存约 52.5GB，768px 示例约 60.3GB；不能据此推荐普通笔记本直接跑。
- **Wan2.2** 不同模型差异很大：官方 TI2V-5B 示例有 24GB GPU 路线，而 A14B 默认示例涉及 80GB 级配置。卸载、量化、分辨率和具体实现会改变门槛。
- **WanGP** 提供低显存优化，但显存减少可能伴随更长生成时间；不能据此推断 Intel Mac 可快速生成。
- Mac 用作网页/本地工作台客户端、把生成交给云端 API，是一条合理的快速试片路线。工作台能在 Mac 打开，与视频模型能在本机高效运行，要分别验证。

参考：[Open-Sora](https://github.com/hpcaitech/Open-Sora#readme)、[Wan2.2](https://github.com/Wan-Video/Wan2.2#readme)、[WanGP](https://github.com/deepbeepmeep/WanGP#readme)。

### 5.4 高 Stars 项目不一定采用标准开源许可

需要重点关注：

- **n8n**：Sustainable Use License 与企业许可部分，属于 fair-code / 源码可用路线；内部业务使用等有允许范围，不能推导为任意托管转售均可。
- **Dify**：修改版 Apache-2.0，包含多租户使用、品牌等附加条件。
- **Open WebUI**：许可中有品牌相关条件和例外。
- **Remotion**：自定义许可，个人/部分小规模公司使用与更大组织的公司授权条件不同，不能标为 MIT 或统一永久免费。
- **Huobao、waoowaoo、Hypit**：分别存在非商业、ELv2、自定义许可条件。
- **AGPL 项目**：做修改和通过网络向用户提供服务时，要评估相关源码提供义务；不能只凭“仓库公开”决定闭源商用方式。
- **生成模型**：代码许可与权重许可分开阅读，最终还要检查模型卡、第三方依赖和素材授权。

这些判断用于筛选路线，最终应按采用的具体版本阅读许可原文。各仓库根目录及 README 提供许可入口。

## 6. 30 秒短剧的最小验证方案

### 6.1 先把实验范围控制住

建议采用 **1 个场景、2 个角色、4–6 个镜头、少量对白**。例如医疗场景可选择一次普通咨询，通过一个小误会和解释完成情节；医学事实与剧情表现分别审核。

推荐按以下顺序完成一次闭环：

1. **剧本**：明确人物关系、信息点、情绪变化和结束钩子；先固定对白，再估算实际语速。
2. **资产**：保存角色外观、服装、场景和道具参考；角色身份参考与表情参考分别准备。
3. **分镜**：记录镜头编号、时长、景别、台词、动作、视线和上一镜衔接；先完成静态分镜审核。
4. **小样**：先生成一个有对白的镜头和一个动作镜头，验证角色与模型能力，再批量生成。
5. **声音**：固定角色音色和对白，检查停顿、重音及口型；避免画面已定稿后大改整段对白。
6. **剪辑**：替换失败镜头，统一字幕、声音和画面节奏；检查是否能导出可继续编辑的工程/草稿。
7. **审片**：看完整成片，再逐镜检查表情、人物关系、连续性和医学准确性。

表情指导应使用可观察的行为，例如“眉间放松、先听完、轻微点头、短暂犹豫后开口、语气自然”。单写“专业、严肃、坚定”容易把人物推向过强的压迫感。参考图本身也应符合预期情绪。

### 6.2 三条可执行路线

| 路线 | 组合 | 适合的目标 | 最先验证什么 |
| --- | --- | --- | --- |
| 快速自动成片 | Pixelle-Video 或 MoneyPrinterTurbo + 模型 API + 配音 | 旁白故事、科普、轻剧情 | 文案质量、画面可用率、配音字幕与合成 |
| 短剧工作台 | Toonflow 或 ArcReel + 参考图 + 视频模型 + 剪辑 | 多角色、重复拍同一人物、镜头替换 | 参考传递、连续性、任务恢复、工程交付 |
| 深度定制 | ComfyUI + Wan 等模型 + TTS/口型 + FFmpeg/Remotion | 需要自控模型、批量复用、开发产品 | 显存、速度、版本稳定性、许可与维护成本 |

### 6.3 用可用成片衡量成本

建议记录下面这些指标，再决定继续投入哪个项目：

| 指标 | 记录方法 | 为什么有用 |
| --- | --- | --- |
| 有效镜头率 | 可直接使用的生成次数 ÷ 总生成次数 | 反映重抽成本 |
| 可用秒数成本 | 生成/重试/配音/放大/渲染等总费用 ÷ 最终可用秒数 | 比单次模型报价更接近真实成本 |
| 首条成片时间 | 环境配置、资产、生成、修改、剪辑的总耗时 | 衡量上手负担 |
| 角色一致性 | 脸、发型、服装、体型和音色是否前后一致 | 决定能否继续拍下一集 |
| 表演自然度 | 表情、视线、停顿、肢体与人物关系是否合理 | 决定是否像在演戏 |
| 连续性 | 轴线、手中道具、人物位置和动作起止是否衔接 | 防止单镜好看但拼起来不连贯 |
| 可修改性 | 能否只重做一镜、沿用资产、替换声音和导出工程 | 决定后期返工成本 |
| 交付准确性 | 台词、字幕、专有名词和医学事实逐项核对 | 避免画面吸引人但信息错误 |

## 7. 通用热门 AI 项目怎么接入短剧生产

在单条样片跑通后，再按实际瓶颈补充：

- **n8n**：监听任务状态、串接模型 API、生成完成后归档和通知；先核对许可和外部 API 使用条件。
- **Dify / Langflow**：组织剧本生成、角色设定、镜头提示词和人工审核入口。
- **LangGraph / LangChain**：需要编程控制预算、状态、失败重试与审核节点时使用。
- **RAGFlow**：对已有授权资料建立检索知识库，辅助事实核对和背景资料引用；医学内容仍需人工审核。
- **Ollama / Open WebUI**：组织本地或远端语言模型入口，处理文本任务；不会自动替代视频模型。
- **OpenHands**：辅助搭建、修改和维护上述软件，属于开发工具层。

不建议在第一条样片之前同时部署这些平台。先明确生产步骤中真正耗时的部分，再自动化。

## 8. 资料来源、改名与后续维护

### 8.1 来源与验证层级

1. **GitHub 仓库元数据**：Stars、最近推送日期、默认分支、主许可证提示。API 模板：
   `https://api.github.com/repos/{owner}/{repo}`。
2. **官方 README**：用于核对项目定位、工作流、运行依赖、硬件示例和功能边界。上文项目链接均可直接进入官方仓库。
3. **LICENSE / NOTICE / 模型卡**：在许可边界、代码与权重差异明显的项目上重点核对。
4. **仅初筛项**：OpenCreator、openshorts，以及部分通用配套项目的描述主要根据仓库元数据和项目简介整理，未做与重点短剧工作台同等深度的流程核验。
5. **尚未完成的验证**：没有对这 43 个项目逐一安装、生成同题样片或实测成本，也没有据演示视频建立画质排名。

### 8.2 仓库改名与重定向

| 旧地址 / 名称 | 当前采用的仓库 | 维护提示 |
| --- | --- | --- |
| comfyanonymous/ComfyUI | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | 新资料优先使用当前地址 |
| deepbeepmeep/Wan2GP | [deepbeepmeep/WanGP](https://github.com/deepbeepmeep/WanGP) | 不应只按早期 Wan2GP 的功能范围理解当前工具 |
| FunAudioLLM/CosyVoice | [QwenAudio/CosyVoice](https://github.com/QwenAudio/CosyVoice) | 查询模型和说明时注意地址变化 |
| KrillinAI 名称 | [krillinai/OpenCreator](https://github.com/krillinai/OpenCreator) | 当前定位已扩展，应按现版本重新核对功能 |

### 8.3 如何更新这份清单

- 每次更新同时记录统计日期和 Stars；需要判断“近期爆火”时，至少保存两个时间点并比较增长量与增长率。
- 重点复查 Releases、安装说明、模型接入、许可证及 Issues 中的重复故障，而不只刷新 Stars。
- 真正进入试用时，为候选记录具体版本/提交、系统、模型、参数、时长、重试次数、总费用和人工修改时间。
- 后续可优先安排 Toonflow、ArcReel、Pixelle-Video、MoneyPrinterTurbo 同题试片，再根据可用镜头率和修改成本调整推荐顺序。

## 9. 用户收集补充：剧本 Skill 与对话式制作（2026-10-21）

本次阅读了两个仓库的说明、导演方法及评测文档；X原页读取受限，通过公开转呈取得帖子和西堂长文文字。没有观看其中全部视频，也没有安装、跑通这些项目。下表Stars单独取2026-10-21 GitHub API快照，不与旧表混作同日排名。

| 项目 | Stars（10月21日） | 定位 | 最适合借鉴 |
|---|---:|---|---|
| [awesome-short-drama-skills](https://github.com/UnderleveledBuilder/awesome-short-drama-skills) | 558 | 短剧/漫剧Skill目录，按编剧、分镜、提示词、出片等分类，附公开评测；目录本身为CC0-1.0，各收录项目独立核对 | 筛选编剧/审稿方法，对照实际产出判断，不把收录或安装等同于效果保证 |
| [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 4,558 | 用代码制作短片的Claude Code Skill、风格示例、导演与技术指南；代码MIT，样片另有署名约定 | 故事聚焦、开场、节奏、声音与表演检查；不是替换Seedance的真人视频生成模型 |

### 9.1 从合集里借审稿标准，不照搬爽剧公式

合集的[评测规范](https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/main/evals/README.md)关注钩子、人物动机、结构、对白、AI味和可用性。[第一轮点评](https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/main/evals/runs/001-open-brief/review.md)公开了同题、多次生成和匿名对比，也报告不同评审的分歧。它是特定环境下的AI评审，不是人类观众留存或商业效果验证。

对医疗情景短剧，适合采用“主角动机有没有写出来、前后反应有没有因果、台词是否口语、少人少景是否拍得完”。正反派、金手指、连续反转和付费卡点不应硬塞进真实门诊。

### 9.2 从Lemo借导演方法，保持当前画面路线

[DIRECTOR.md](https://github.com/lemomo-ai/lemo-opuscar/blob/main/DIRECTOR.md)主张聚焦目标与转折，尽快进入故事，用结尾呼应开头，并检查节奏和表演。对门诊戏，最有用的是明确情绪变化、关键反应让观众看得见；不照搬动画的多种运镜、音乐节拍或转场要求。

### 9.3 两条X链接是一套案例的介绍与原教程

- [gkxspace：对话式AI短剧制作介绍](https://x.com/gkxspace/status/2112523924433166611?s=20)：转述西堂案例，把剧本、资产、任务恢复、返修和口头剪辑指令串起来。
- [西堂：可灵全流程教程](https://x.com/xitang_ai/status/2112514646196244880?s=20)：原文讲从剧本到资产、分批生成及返修剪辑，并给出实际修改例子。正文文章链接：[X长文](https://x.com/i/article/2112071623092117504)。

两条不计作两套独立方法。教程中更值得迁移的是：每个人的反应有动机、用景别读表情、保存任务编号、把具体错误交给补拍或剪辑。作者对某次模型表现、价格和重试次数的描述属于其案例记录，本页不将其当成当前通用结论。

资产参考也不能机械照抄：教程的遮脸全身参考板服务于其可灵流程；本项目使用本账号Seedream人像原图和已入库授权资产，已有原图不裁剪、遮挡或重编码后重新投喂Seedance。

### 9.4 在本项目第六版试改里采用什么（现已归档）

- 开头前置“赶紧切掉”与“还想生育”的分歧，删去成片里完整候诊和身份核对，正常就诊核对设为此前已完成。
- 医生先听她担心什么，再讲各选项；专业知识服务于人物选择，不写成逐条问答目录。
- 保留三个关键反应，其他停顿收紧；把林悦知道代价后仍自己决定作为高潮，丈夫以一句支持完成转变。
- 保持三个选项及其代价，不把某一治疗拍成救场反转；结尾从重复诊断改成呼应表达顾虑。
- 第六版试改为123秒、16段，已留档。随后用户放开全部创作限制，第七版改名《先听她说》，采用先写完整场景再拆生产段的方法；重心是人物关系，不再要求讲全治疗菜单。现有150.57秒成片仍对应第五版。

本次收集的四条链接均保留在本节；当前剧本及逐次改稿理由在[现行剧本《先听她说》](../短剧/能不能不切/剧本.md)与[改稿记录](../短剧/能不能不切/改稿记录.md)。


### 9.5 截图中的技能方法如何用于第八版（2026-10-21）

本次选择四组方法用于现有门诊片，未安装远端技能、未将其整套流程或商业效果视为已验证，也没有刷新原热度表。借用的是剧作与制作方法，生成继续沿用本机已跑通的Seedance 2.5。

| 参考 | 本次具体采用 | 对应产物 |
| --- | --- | --- |
| [Screenwriting Skills](https://github.com/jtydhr88/screenwriting-skills) | 每句对白都有欲望与策略；删掉林悦分析自己心理的长句，改为“我没说不治。我是问，还能不能要。” | 第八版剧本 |
| [Visual Skills](https://github.com/smixs/visual-skills/blob/main/video/references/dramaturgy.md) | 先按行动与情绪排镜，“我怕/我也怕”同框，纸张与牵手承载变化 | 28镜分镜，按模型能力合成15个批次，共118秒 |
| [shuohao staging](https://github.com/eternityspring/shuohao-skills/blob/main/skills/novel-staging/SKILL.md) | 从实际场景图定家具/站位，生成可拖动俯视报告并校验；再将开场走位交接给分镜 | 空间与连戏表 |
| [Emily2040 Seedance](https://github.com/emily2040/seedance-2.0/blob/main/references/direct-for-the-model.md) | 看谁、为什么说、一个可见动作；每段独立声明人物位置、左右手、道具与参考编号 | V8_01–V8_15逐段提示词 |

“西羊石短剧剧本GPT”的参考价值目前来自西堂公开示例中人物主动性与因果安排，未取得底层配置，也没有对本项目实测；适合借思路，不能声称优于上述方法。LearnPrompt/awesome-seedance可作案例索引；zenstory-ai/drama-skills可借文件衔接思路，不再叠加另一套总控。scenario-labs/skills与pexoai/pexo-skills依赖相应平台，当前不迁移；剪映技能可另用于草稿交付，但不将Mac自动导出当作现成可用能力。

**2026-10-22空间补齐**：已实际运行novel-staging脚本，交付两处俯视图、可拖动HTML、28镜机位核对，并同步原提示词；原图不可见区域标明未确认，旧预览的07左右/木门背景不作空间依据。

第八版文本、分镜与逐段提示词已经准备，DeepSeek复核与处理记录沿原项目留存。新片仍待构图预览、报价确认、试跑与实际听审；本次没有生成新视频，不能据此断言这些方法已提高成片质量。

---

本清单用于发现项目与制定试用路线。项目功能、托管方式、模型授权和价格会变化；采用前请回到拟使用版本的官方文档核对。
