# Opus 5.5 全流程短视频制作：GitHub 项目研究与实施建议

> 核验日期：2026-10-19（北京时间）。  
> 目标：Opus 5.5 自主完成选题、检索、脚本、分镜、画面、配音、配乐、字幕、渲染和自检；用户只审核最终成片。  
> 本文为研究文档，未在本次任务中安装这些项目、调用付费媒体服务、实际制作视频或向平台发布。  
> 证据分层：GitHub API 元数据、项目 README／技能说明／部分源码已核对；功能与性能若仅来自作者文档，均不代表本次实测；推荐方案和参数是研究判断。

## 1. 结论先看

这个目标可以作为系统设计目标，但当前热门仓库没有被本次研究证明能“安装即自动找热点、无需任何中间决策、稳定做出优质中文视频”。

应让 Opus 5.5 担任总导演和执行代理，通过工具完成声音、画面与编码。它并不原生输出配音音频、音乐波形或 MP4。用户不需要亲自操作这些工具，但首次仍要把执行环境、可用账号、音色、渠道范围和费用边界配置好。

按本次目标，建议分三条路线：

| 路线 | 优先采用 | 推荐理由 | 与目标之间还差什么 |
|---|---|---|---|
| 中文／英文知识短视频的综合生产 | **digitalsamba/claude-code-video-toolkit** | 明确覆盖脚本、配音、音乐、视觉和渲染，已经封装 Qwen3-TTS、ACE-Step 等工具 | 增加自主选题；将交互式制作流程改为事先授权范围内自动决策；验证中文与无人值守运行 |
| 这波 Opus 纯代码风格动画 | **lemomo-ai/lemo-opuscar** | 51 种风格；技术指南包含 TTS、代码作曲、混音、字幕及渲染 | 增加选题与事实核验；固定音色和默认策略；让分镜检查由代理自己完成 |
| 真实影像、生成视频、纪录片等多类型内容 | **calesthio/OpenMontage** | 检索、素材、语音、音乐、合成和审查工具覆盖面大，支持真实动态素材 | 默认有较多强制人工批准节点；需要实际适配流程与检查点，集成和维护成本较高 |

若优先要“像 X 上那些用 Opus 写代码的动画”，先选 **lemo-opuscar**。若优先要“把不同题目都做成有声音的短视频”，先验证 **claude-code-video-toolkit**。不要把所有项目叠在一起，多个主流程可能互相要求不同目录、依赖和确认步骤。

来源：[toolkit README](https://github.com/digitalsamba/claude-code-video-toolkit)、[toolkit CLAUDE.md](https://github.com/digitalsamba/claude-code-video-toolkit/blob/main/CLAUDE.md)、[lemo 技术指南](https://github.com/lemomo-ai/lemo-opuscar/blob/main/TECHNIQUE.md)、[OpenMontage Agent Guide](https://github.com/calesthio/OpenMontage/blob/main/AGENT_GUIDE.md)。

## 2. 怎样理解“GitHub 上爆火”

本次用“累计 Star 数、最近推送时间、公开样片和源码可检查性”筛选，不把项目的营销词当作播放或收益证据。

- 累计 Star 反映关注规模，不等于近期增长速度，也不证明成片质量。
- 最近推送只反映仓库活动，不保证关键功能维护良好。
- “100M views”“一键爆款”之类描述不能当作可复现的结果。
- 当前没有核验到足以评估这些工具在抖音／TikTok 上成功率的完整账号样本、投入成本和播放收益数据。
- 下表是相关候选项目快照，并非 GitHub 全站穷尽清单，也不是热度增长榜。
- API 返回的推送日期原为 UTC，下表保留其日期口径。

| 原仓库 | Star 快照 | 最近推送日期（UTC） |
|---|---:|---|
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | 69,528 | 2026-10-16 |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 66,720 | 2026-10-18 |
| [hypit-ai/hypit](https://github.com/hypit-ai/hypit) | 23,523 | 2026-10-15 |
| [browser-use/video-use](https://github.com/browser-use/video-use) | 29,279 | 2026-10-08 |
| [QwenLM/Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | 13,851 | 2026-03-17 |
| [ACE-Step/ACE-Step-1.5](https://github.com/ACE-Step/ACE-Step-1.5) | 13,770 | 2026-10-11 |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 12,390 | 2026-10-17 |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | 5,328 | 2026-10-16 |
| [alchaincyf/huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) | 4,358 | 2026-10-16 |
| [NarratorAI-Studio/narrator-ai-cli-skill](https://github.com/NarratorAI-Studio/narrator-ai-cli-skill) | 3,052 | 2026-07-05 |
| [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 3,039 | 2026-10-18 |
| [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) | 2,275 | 2026-10-12 |
| [JohnHeibel/PDoomVideo](https://github.com/JohnHeibel/PDoomVideo) | 2,201 | 2026-09-25 |
| [Vincentwei1021/video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft) | 1,636 | 2026-10-12 |
| [JohnHeibel/ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) | 1,267 | 2026-09-24 |
| [Vincentwei1021/mg-styles-15](https://github.com/Vincentwei1021/mg-styles-15) | 1,164 | 2026-10-05 |
| [tuzhechen2005/opus-video-skills](https://github.com/tuzhechen2005/opus-video-skills) | 231 | 2026-09-27 |
| [Kianzzz/xilo-opus-video](https://github.com/Kianzzz/xilo-opus-video) | 183 | 2026-09-28 |
| [chuspeeism/dashi-animationstyle](https://github.com/chuspeeism/dashi-animationstyle) | 92 | 2026-10-13 |
| [WaterDJiang/Wattter_openSkills](https://github.com/WaterDJiang/Wattter_openSkills) | 55 | 2026-10-08 |

元数据来源：各仓库 GitHub REST API，例如 [OpenMontage 元数据](https://api.github.com/repos/calesthio/OpenMontage)、[HyperFrames 元数据](https://api.github.com/repos/heygen-com/hyperframes)、[lemo 元数据](https://api.github.com/repos/lemomo-ai/lemo-opuscar)。上述统计仅代表本次读取时点。

## 3. 最贴合“只看成片”的新增项目

### 3.1 claude-code-video-toolkit：综合制作的首批验证对象

仓库：<https://github.com/digitalsamba/claude-code-video-toolkit>

项目明确提供从概念到成片的工作区，支持配音、音乐、图像／视频素材、Remotion、部分 Python/moviepy 模板和质量检查。已有 9:16 概念解说样例。

对本需求最有用的能力：

- 配音工具可选择 ElevenLabs、Qwen3-TTS 等后端。
- 音乐生成工具对接 ACE-Step 1.5。
- 可以用代码画面，也可以加入生成式图像和视频素材。
- 项目状态能够跨会话保留，适合失败恢复和后续改片。

需要补齐：自主选题排序、中文专有名词与字幕验证、预算控制，以及把默认交互式场景规划改为授权范围内自主选择。README 中的单次成本和云平台赠送额度是作者描述，不能作为当前报价或完整成本承诺。

工具仓库为 MIT；模型权重、采样、云服务、人物和音乐仍分别核对使用条件。首次配置云 GPU、存储和声音不等于日后每条都要人工操作。

### 3.2 lemo-opuscar：最贴近本轮纯代码动画

仓库：<https://github.com/lemomo-ai/lemo-opuscar>

当前 README 为 51 种风格，不是旧清单中的 43 种。除画风外，还提供导演和制作方法。

其 TECHNIQUE.md 已描述画面、语音、音乐、音效和字幕共用时间线：

- 英文默认可用本地 Kokoro；中文默认路线包含在线 edge-tts。
- 用语音识别回查配音文字，并生成时间信息。
- Opus 根据镜头节奏编写配乐代码，使用合成与采样生成声音。
- 逐帧渲染画面，再混音和编码。

因此它比“仅有画风提示词”更接近完整生产工具。需要增加的是选题、来源核验、长期账号风格和自主执行配置。中文长期生产不应只依赖一条在线语音通道，应预先测试备用 TTS；源码开放也不等于在线语音服务承诺稳定可用。

许可：代码和文档 MIT；演示影片及静帧为 CC BY 4.0；第三方素材沿用自己的许可。自己制作的影片与直接搬用演示片是两种情况。

来源：[README](https://github.com/lemomo-ai/lemo-opuscar)、[TECHNIQUE.md](https://github.com/lemomo-ai/lemo-opuscar/blob/main/TECHNIQUE.md)。

### 3.3 OpenMontage：能力全面，默认交互也较多

仓库：<https://github.com/calesthio/OpenMontage>

支持研究、剧本、素材生成与检索、配音、音乐、字幕、合成和自检。可以剪真实动态影像，也可以使用生成模型或代码渲染。

适合以后扩展到纪录片、科技故事、实拍素材混剪和生成视频。

但当前 AGENT_GUIDE.md 明确包含人类批准与检查点，甚至在渲染引擎选择等阶段要求等待。它不是本次要求下可以直接宣称“零中间确认”的产品。

落地时必须逐项核实哪些检查点支持配置、哪些只是代理指令、哪些是程序强制门禁。在你的明确自主制作授权范围内设计自动决策适配；需要改代码的门禁就进行实现与测试，不伪造“用户已批准”记录。

仓库为 AGPL-3.0。自用制作与将工具改成对外网络服务的许可义务不同；商业部署还须核对底层模型与第三方服务条款。

来源：[README](https://github.com/calesthio/OpenMontage)、[AGENT_GUIDE.md](https://github.com/calesthio/OpenMontage/blob/main/AGENT_GUIDE.md)。

### 3.4 HyperFrames：热门的 HTML 视频底座

仓库：<https://github.com/heygen-com/hyperframes>

将 HTML、CSS、媒体和可定位时间的动画渲染成视频。当前技能体系覆盖创作路由、动画、音频混音、媒体查找与生成等能力，可供 Claude Code／Codex 等代理调用。

它适合搭建稳定、可编辑、可复用的动画生产工程，特别是动态字体、图表、界面与 2.5D 运镜。其媒体技能也能路由 TTS／音乐等工具，但最终能力取决于已配置的后端。

它仍不是自动经营短视频账号的完整系统。选题、事实来源、预算和最终审核队列需要自己组合；默认 brief 确认行为也需适配。源码许可为 Apache-2.0。

来源：[README](https://github.com/heygen-com/hyperframes)。

### 3.5 Hypit：参考短视频改编与多版本

仓库：<https://github.com/hypit-ai/hypit>

重点是把参考视频解析成可复用的制作流程，用词语时间锚安排字幕、画面和效果，再更换主题、语言或素材。也支持纯代码画面。

对于研究 TikTok 风格结构、多语言改编、模板化批量版本，值得验证；不能据其宣传口号推断播放量。

许可不是无附加条件的 Apache-2.0：当前 LICENSE 对多租户服务、商业再分发等设置限制，同时允许在自身基础设施上用于本组织工作，包括商业工作和客户工作；输出内容另有说明。要区分自用做视频和提供视频制作 SaaS。

来源：[README](https://github.com/hypit-ai/hypit)、[LICENSE](https://github.com/hypit-ai/hypit/blob/main/LICENSE)。

### 3.6 video-use：适合已有真人素材

仓库：<https://github.com/browser-use/video-use>

以转写文本和按需视觉检查驱动剪辑，可去口头语、剪停顿、加字幕、调色和叠加动画。默认文档采用 ElevenLabs Scribe 转写。

当输入只有“请自动选题并创作”时，它还缺少上游内容和素材生产；更适合作为真人录音／实拍支线的后期工具，不优先作为本项目总控。MIT 许可。

### 3.7 Narrator AI CLI Skill：影视解说服务入口

仓库：<https://github.com/NarratorAI-Studio/narrator-ai-cli-skill>

文档描述选影片、模板、BGM、声音、生成解说和合成视频的链路，但 skill 需要底层 narrator-ai-cli 及服务 app_key；README 要求联系提供方取得密钥，且列有行动前确认规则。

这说明“公开了技能代码”不等于全部生产能力都能免费自托管。它主要面向影视解说，与原创 AI／知识科普的匹配度较低，影视素材和服务授权也要额外确认，不列为首选。

## 4. 原始 8 项，按新目标重新排序

| 项目 | 在全流程中的角色 | 能否原样满足只看成片 | 本次建议 |
|---|---|---|---|
| [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 风格动画＋TTS＋代码作曲＋合成 | 接近，但缺自主选题和执行配置 | **纯代码路线优先验证** |
| [xilo-opus-video](https://github.com/Kianzzz/xilo-opus-video) | 通用方案规划、逐镜头制作与渲染 | 默认三方案、预览与用户选择；默认并不配音 | 可做轻量总流程，须接 TTS 并适配为自主选方案 |
| [huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) | 艺术画面、解说语法、分析与验收 | 有些成片示例需要外部人物或音频 | 作为艺术动画专用路线，不强求承担所有内容运营 |
| [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 真实产品页面拍摄与宣传片 | 主要围绕具体产品，不能代替通用自主选题 | App／网站／智能体宣传时调用 |
| [wtt-code-animation-studio](https://github.com/WaterDJiang/Wattter_openSkills/tree/main/wattter_skills/wtt-code-animation-studio) | 中文剧本、分镜、代码、声音、成片 | 默认要选风格；根仓库有非商业限制 | 可研究方法；拟变现前先解决许可 |
| [dashi-animationstyle](https://github.com/chuspeeism/dashi-animationstyle) | 现成中文口播配画面和字幕 | 需要口播输入，默认有两次确认，配乐音效回剪映 | 不作全自动主流程 |
| [mg-styles-15](https://github.com/Vincentwei1021/mg-styles-15) | 15 支样片、提示词、源码、代码声音 | 主要是风格参考库 | 借鉴动作、声音和渲染方法，不当作总控 |
| archival-doc | 据原帖描述是授权历史素材纪录片流程 | 未找到可确认的公开仓库 | 保留为待核验，不写成已支持或可安装 |

补充更新：huashu 当前 README 写到 36 种艺术风格、9 种解说语法，同时存在更多研究配方卡；这些数量不是同一个统计口径。video-shotcraft 当前 README 写 124 张卡／150 个镜头，不能混用旧描述或仓库 About 中的另一组计数。

## 5. 配音和配乐由谁完成

“Opus 负责所有制作任务”可以实现为由 Opus 操作工具、选择参数、检查结果；不要求用户自己录音或写音乐。

| 环节 | Opus 的工作 | 需要实际执行的工具 | 推荐策略 |
|---|---|---|---|
| 选题 | 搜索、验证、排序、选择一个题目 | 搜索工具、RSS、已有新闻源／本地材料 | 留下选题理由与来源，内部筛选后直接制作 |
| 配音 | 改写适合口语的台词，控制情绪和停顿 | Qwen3-TTS 或已配置的 TTS 服务 | 首次确定默认声音，后续自动沿用 |
| 原创配乐 | 定音乐结构、节奏和配器，或编写生成提示词 | ACE-Step 1.5 或代码合成／采样器 | 知识短片优先无歌词，避免盖住人声 |
| 音效 | 给动作和转场安排声音 | 合法音效库、代码合成或音效生成工具 | 控制数量，服务叙事 |
| 字幕 | 规范文字、纠错、决定断句与强调 | ASR／强制对齐＋字幕渲染工具 | 以最终实际音频校时 |
| 最终合成 | 统一时间线、混音、编码 | FFmpeg、Remotion 或 HyperFrames | 输出真实可播放成片 |

### 5.1 Qwen3-TTS

仓库：<https://github.com/QwenLM/Qwen3-TTS>

官方项目支持语音生成、声音设计和声音克隆，包含中文、英文等语言。适合建立长期默认旁白后端。代码元数据标识 Apache-2.0，具体选用的权重版本和服务条款仍应单独记录。

可以由 Opus 自动生成每镜配音并做回查。中文自然度、数字、英文缩写和专有名词需要在自己的运行环境实测。没有必要把“使用本人声音”作为前提，可先采用合适的预置／设计音色。

来源：[官方 README](https://github.com/QwenLM/Qwen3-TTS)。

### 5.2 ACE-Step 1.5

仓库：<https://github.com/ACE-Step/ACE-Step-1.5>

用于音乐生成。Opus 可以制定情绪、速度、配器和时长要求，再调用模型生成背景音乐。

不同型号、量化和设备对显存需求差异较大，不能把 README 的低显存描述套到所有模型；例如 XL 的要求明显更高。选具体权重后再做速度和内存验证。

仓库代码为 MIT；若改用 ACEMusic 等托管服务，输出与商业使用还要依据对应服务条款，不能只引用代码许可证。生成音乐也不等于自动获得任何第三方旋律、录音或艺人声音的权利。

来源：[官方 README](https://github.com/ACE-Step/ACE-Step-1.5)、[输出授权相关讨论](https://github.com/ace-step/ACE-Step-1.5/discussions/1256)。

### 5.3 代码作曲也是可选主路线

lemo、mg-styles-15、xilo 等展示了代码生成音乐或音效的方法。对短促卡点、图形动画、像素风很实用，不一定非要部署音乐模型。

但“代码合成”可能仍使用乐器采样。应保存采样库来源和许可；代码、采样、音色及最终音频分别记录。先验证音质，不预设代码音乐一定优于生成模型。

## 6. 真正无人值守，缺的通常是总控层

推荐的运行顺序：

1. 收集候选题目，并检查已有内容避免重复。
2. 内部比较候选题，选定一个可验证、可画出来的题目。
3. 写剧本、事实来源表和视觉动作表。
4. 自主选择画风、声音、音乐和制作工具。
5. 生成配音，回查读音与文字，锁定时间线。
6. 制作画面、配乐、音效和字幕。
7. 渲染整片，检查音画、事实和可读性。
8. 自动修复明确问题，达到预设重试上限后交付结果。
9. 将最终视频和简短说明送入人工审核队列。

中间的分镜、静帧和预览依然保留，只是由代理自己检查，不要求用户逐项操作。用户看到的应是最终视频及必要的异常说明，而非一堆等待选择的方案。

### 自主选题的建议规则

以下是设计建议，不是某个仓库已经完成的功能：

| 评价项 | 建议权重 | 判断内容 |
|---|---:|---|
| 观众价值 | 30% | 看完能解决什么疑问，能否一句话说清 |
| 来源可靠性 | 25% | 关键事实有无官方、论文或原始材料支持 |
| 可视化程度 | 20% | 能否用变化、比较、流程或动作表达 |
| 新意与时效 | 15% | 是否有新的事实、角度或表达方式 |
| 制作可行性 | 10% | 现有素材、算力和预算能否完成 |

没有可核实的热点时可以选择常青题材，不为“每天必须有新闻”编造事件。时效信息须查当天来源；不能把模型记忆当成实时新闻。

可以把现有 AI 新闻数据源作为候选输入，但它需要提供可读取的文件或地址。本次只新增研究文档，不修改新闻数据或既有更新任务。

## 7. 怎样取消中间确认而不让系统停住

这不是“在提示词里加一句不要问我”就一定能完成的。

| 阻塞来源 | 处理方式 | 验收办法 |
|---|---|---|
| 技能默认询问画风、分镜 | 在项目级任务规则中记录用户已委托自主选择，并规定可用范围 | 从空项目到成片运行一次，观察是否等待输入 |
| 脚本有交互选择器 | 采用项目实际支持的非交互参数或配置；没有则开发适配 | 无终端输入时仍能正常退出 |
| 程序强制人工批准 | 研究源码中的检查点机制，按支持方式配置或实现自主审批模式 | 保留真实自动决策记录，不伪造人工点击 |
| 第三方服务缺密钥／额度 | 首次配置可用后端和已允许的备用后端 | 模拟主服务失败，验证自动回退或明确失败 |
| 风格、素材或音色不足 | 使用已配置的默认策略 | 用户不选题、不选音乐，也能完整交付 |
| 任意失败反复重试 | 按步骤设置重试和预算上限 | 到上限后停止该任务并报告原因 |

当前用户授权是研究并提交文档，不包含立即安装、消耗媒体额度或批量生成视频。未来制作任务中可明确授权代理在设定范围内自主决策；技术上仍需遵守实际宿主与服务的能力边界。

## 8. 推荐的最小实施方案

### 方案 A：优先跑通“带声音的知识短视频”

- 总导演：Claude Code 中的 Opus 5.5。
- 主工程：claude-code-video-toolkit。
- 声音：先配置一个已验证的中文 TTS；Qwen3-TTS 是候选。
- 配乐：先验证代码音乐／已许可音乐，再视质量需要接 ACE-Step。
- 画面：先复用一个竖屏解说模板，不同时引入多套合成引擎。
- 内容输入：给定频道定位后，代理自主从可用来源选题。
- 输出：MP4、封面、字幕、来源与运行摘要；默认待审核。

主要开发工作是总控、非交互适配、事实核验、预算与失败恢复，并非重新造一套动画框架。

### 方案 B：优先复现“Opus 写代码做艺术动画”

- 总导演：Opus 5.5。
- 主工程：lemo-opuscar。
- 画面：从 51 种风格中自主选一种适合主题的风格。
- 配音：先用项目现有 TTS 路线验证，再决定是否替换。
- 配乐：沿用项目的时间线驱动代码作曲和混音。
- 上游补充：自动选题与来源检查。
- 输出：有声竖屏动画，用户只看整片。

该路线更贴近原始需求中的样片审美。不要把不同动画库的渲染器直接混接，先让一个项目完整跑通。

### 方案 C：以后扩展真实影像和生成视频

采用 OpenMontage 作为主工程，并单独完成批准节点适配、提供方配置与成本测试。它适合扩大内容类型，但不建议第一天就接入全部模型和管线。

以上都是待验证的集成方案，本文没有把跨项目安装兼容性、无人值守成功率或生产质量标记为已通过。

## 9. 建议的首次频道配置

这些信息首次设置后可长期复用，避免每条视频询问用户。

| 设置项 | 建议起点 |
|---|---|
| 内容方向 | AI 技术和工具解释，或另行确定一个垂直领域 |
| 观众 | 对 AI 感兴趣、能理解日常语言的人 |
| 首批长度 | 30–60 秒，每条只讲一个问题 |
| 画幅 | 原生 9:16，1080×1920，30fps |
| 默认声音 | 一个已验证音色；中英文版本分别设置 |
| 默认音乐 | 无歌词，优先不干扰旁白；可自动决定无配乐 |
| 内容来源 | 原始官方材料优先，保存链接及访问时间 |
| 制作预算 | 显式填写单条、每日总额和重试上限，不能把建议值当实际授权 |
| 失败策略 | 只使用已配置备用路线；到上限提交失败摘要 |
| 发布状态 | 待人工审核；“制作完成”不代表自动发布 |
| 反馈 | 用户看最终片，按时间点提修改；只重做受影响镜头 |

这些是起步建议，并非抖音或 TikTok 的强制技术规格。

## 10. 用户只审核成片时，系统必须自检什么

### 技术检查

- 文件可完整解码，分辨率、帧率、时长正确。
- 有预期音轨，人声没有被音乐淹没。
- 字幕根据最终配音生成，没有出界、乱码和平台界面遮挡。
- 片头片尾、镜头中段及转场没有意外黑帧或残留占位图。
- 修改某段后，最终合成中确实使用了新版本素材。
- 保存重跑命令、依赖版本和阶段状态，失败能恢复。

### 内容与观感检查

- 选题、标题、口播与画面讲的是同一件事。
- 数字、年份、实体名称和结论能对应来源。
- 实际配音没有漏词、重复或明显错读。
- 同屏信息来得及读懂，动作帮助理解。
- 主体在镜头内发生有意义的变化，避免只有文字卡片切换。
- 不把“渲染成功”当作“有趣”“准确”或“会爆”。

建议连续生成三条不同主题的测试片，用户全程不参与选题、分镜和声音选择。三条都能交付只说明基础流程可用，不能据此保证长期稳定或平台收益。

## 11. 原始案例中容易误解的两点

### 11.1 PDoomVideo 是自动导演的好案例，但不是全套原创声音证明

[JohnHeibel/PDoomVideo](https://github.com/JohnHeibel/PDoomVideo) 开放了 Opus 写出的分镜、动画和渲染源码；README 说明没有指定每个场景的创意。

但它使用一首已有歌曲作为输入。不能据此说“Opus 自主完成了选题、原创歌曲、声音和全部版权处理”。适合学习镜头连贯、角色表演和自动审片。

其后续 [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) 为 MIT 动画起步工程，可研究角色动作与渲染。代码许可不自动覆盖第三方角色、歌曲或形象权利。PDoomVideo 的授权需单独确认，本次元数据没有识别到许可证。

### 11.2 video-talkcraft 很合适，但许可与输入方式要看清

[video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft) 强在口播时间戳、语义分镜和动效同步。默认接收成品配音，也提供可选语音服务入口。

它当前采用 PolyForm Noncommercial 1.0.0，README 和 LICENSE 都说明工具商业使用需要作者事先授权。“用它生成的视频归创作者”不能理解成工具可无条件用于商业生产。

来源：[LICENSE](https://github.com/Vincentwei1021/video-talkcraft/blob/main/LICENSE)。

## 12. 成本与部署的实际边界

完整成本至少包括 Opus、TTS、音乐、图像／视频、渲染算力及存储。开源代码不等于调用免费；云平台促销额度不应作为长期生产的预算基础。

对纯代码路线，主要负担通常是模型执行、浏览器渲染和反复改片。对生成视频路线，素材生成和失败重试可能明显增加支出。具体比例需实际记录后判断。

普通服务器能否承担渲染取决于场景：二维图形与复杂 WebGL、水彩笔刷、3D 并不相同。ClaudeAnimationBase 作者特别提示水彩填充在无独显环境可能慢到每帧数秒。因此不能直接承诺现有阿里云服务器胜任全部风格。

推荐先用短样片测量峰值内存、渲染速度、Token 和媒体成本，再决定本地渲染、服务器 CPU 渲染或 GPU 后端。TTS 与音乐服务可独立部署，但需要明确接口适配；本文未验证硬件配置。

## 13. 商业使用与发布边界

| 对象 | 本次核对到的情况 | 对本项目的含义 |
|---|---|---|
| toolkit、xilo、huashu、mg-styles、ClaudeAnimationBase | MIT，部分项目有素材例外 | 保留许可，逐项检查人物、声音、字体、采样等 |
| lemo | 代码／文档 MIT，演示片 CC BY 4.0 | 直接使用演示片需按许可署名；自制内容另看素材 |
| video-shotcraft、HyperFrames | Apache-2.0 | 底层媒体、服务与依赖继续单独核对 |
| OpenMontage | AGPL-3.0 | 对外托管修改版系统时特别核对对应源码义务 |
| Hypit | 带附加条件的自定义许可 | 自用做片与多租户／商业再分发有不同限制 |
| wtt 根仓库 | CC BY-NC-SA 4.0 | 不作为默认可变现生产工具 |
| video-talkcraft | PolyForm Noncommercial | 商业生产前需要作者授权 |
| Remotion | 自身另有免费／公司许可规则 | 不能因为外层 skill 免费就忽略框架许可 |
| 云端 TTS／音乐／视频服务 | 各自服务条款 | 密钥可用不代表全部输出用途已获允许 |

许可是当前来源的技术性归纳，不替代对具体部署、权重、资产和服务条款的逐项确认。

制作与发布应分开。当前目标是“用户审核最终视频”，所以成片交付后保持待审核；本次没有授权自动发抖音或 TikTok。以后确需自动发布，再配置审核通过信号、账号与平台接口。发布时执行适用的 AI 内容标识要求。

## 14. 建议交付目录与状态

以下是可采用的工程结构，不是本文已创建的视频项目：

~~~text
video-project/
  brief.md
  topics.json
  sources.md
  script.md
  storyboard.md
  project.json
  assets/
  audio/
  captions/
  source/
  qa/
  out/
    final.mp4
    cover.png
    subtitles.srt
    review.md
~~~

- topics.json：候选题、排序与实际选题。
- sources.md：关键事实、出处和访问时间。
- project.json：当前阶段、依赖、预算使用和失败原因。
- review.md：实际视频规格、检查结果、来源与必要异常。
- final.mp4：唯一待用户审核的最终版本，旧版保留版本记录。

建议状态流：待制作 → 制作中 → 自检中 → 待人工审核 → 已通过／需修改。只有实际发布成功后才进入“已发布”，不能由渲染状态推断。

## 15. 后续优先级

1. 在 lemo 与 toolkit 中选择一个主工程，先跑一条带配音、音乐和字幕的原生竖屏片。
2. 增加自主选题与事实来源记录，不要求用户提供口播稿。
3. 消除已授权范围内的中间交互，实际验证不会等待输入。
4. 加入预算、重试上限、恢复执行和最终审核队列。
5. 连续跑不同题材并记录失败点，随后才决定批量生产和自动发布。

判断成功的依据是：用户没有参与中间制作，收到可播放、有声音、内容可核实的成片；系统留下可重跑记录，且没有悄悄超出已配置资源边界。

## 16. 主要一手来源与继续检索入口

### 综合生产与渲染

- [claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit)
- [toolkit CLAUDE.md](https://github.com/digitalsamba/claude-code-video-toolkit/blob/main/CLAUDE.md)
- [OpenMontage](https://github.com/calesthio/OpenMontage)
- [OpenMontage Agent Guide](https://github.com/calesthio/OpenMontage/blob/main/AGENT_GUIDE.md)
- [HyperFrames](https://github.com/heygen-com/hyperframes)
- [Hypit](https://github.com/hypit-ai/hypit)
- [Hypit LICENSE](https://github.com/hypit-ai/hypit/blob/main/LICENSE)
- [Remotion Skills](https://github.com/remotion-dev/skills)
- [Remotion 许可说明](https://www.remotion.dev/docs/license/pricing)
- [video-use](https://github.com/browser-use/video-use)
- [Narrator AI CLI Skill](https://github.com/NarratorAI-Studio/narrator-ai-cli-skill)

### 代码动画与风格

- [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar)
- [lemo TECHNIQUE.md](https://github.com/lemomo-ai/lemo-opuscar/blob/main/TECHNIQUE.md)
- [xilo-opus-video](https://github.com/Kianzzz/xilo-opus-video)
- [xilo 渲染代码](https://github.com/Kianzzz/xilo-opus-video/blob/main/skills/xilo-opus-video/scripts/render.py)
- [huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion)
- [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)
- [video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft)
- [mg-styles-15](https://github.com/Vincentwei1021/mg-styles-15)
- [dashi-animationstyle](https://github.com/chuspeeism/dashi-animationstyle)
- [wtt 根 README 与许可说明](https://github.com/WaterDJiang/Wattter_openSkills)
- [wtt-code-animation-studio](https://github.com/WaterDJiang/Wattter_openSkills/tree/main/wattter_skills/wtt-code-animation-studio)
- [opus-video-skills](https://github.com/tuzhechen2005/opus-video-skills)
- [PDoomVideo](https://github.com/JohnHeibel/PDoomVideo)
- [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase)

### 声音与平台

- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS)
- [ACE-Step 1.5](https://github.com/ACE-Step/ACE-Step-1.5)
- [Anthropic：Opus 5.5 官方发布](https://www.anthropic.com/claude-opus-5-5)
- [TikTok：AI-generated content](https://support.tiktok.com/en/using-tiktok/creating-videos/ai-generated-content)
- [抖音安全与信任中心：AI 治理公告](https://trust.douyin.com/article/15868)

### 项目发现索引

- [awesome-opus-video-skills](https://github.com/ismoshushi/awesome-opus-video-skills)
- [awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills)

索引只用于发现候选；许可、数量和接口以原仓库为准。本次未复现索引作者的横向测试，也不沿用其安全评级作为独立安全结论。

