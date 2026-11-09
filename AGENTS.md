# AGENTS.md

> 面向所有 AI 编码代理的项目硬约束。需求与判据以 `docs/` 为准；实现与文档冲突时先改文档。

## 项目定位

部署在高端康养社区（CCRC）长者卧室平板上的 3D 数字人陪伴系统：WebRTC 全双工语音，System One（本地 Laya 快决策）+ System 2（DeepSeek / Qwen 开放域）双路由，承担情感陪伴、用药提醒、健康采集、戏曲/影视娱乐、信息搜集。

## 技术栈

| 层 | 选型 |
| --- | --- |
| 后端 | Python 3.10+、FastAPI（HTTP/SSE/WebRTC 信令）、uvicorn、JWT、LangGraph、SQLAlchemy + Alembic、Pydantic v2 + Pydantic Settings |
| 存储 | PostgreSQL + pgvector、Redis |
| 实时语音 | WebRTC（aiortc）、流式 ASR/TTS、3D-Speaker CAM++ 声纹 |
| 前端 | Vite、three.js + three-vrm（改造 vrm-playground） |
| 模型 | 本地 Laya（CPU）、DeepSeek / Qwen（S2）、第三方流式 ASR/TTS |
| 工程 | Docker Compose、pytest、eval_gate、Langfuse |

## 目录约定

```
app/api/            FastAPI 路由（/health、HTTP / SSE / WebRTC 信令）
app/core/           配置（.env）、结构化日志、trace_id 中间件、安全
app/models/         SQLAlchemy 模型（11 张主表）
app/router/         三级路由：规则层 → Laya → 主控
app/system_one/     Laya 分类器与 questions.py
app/services/       业务服务与 Tool
frontend/pad/       长者平板（Vite + three-vrm）
mcp-servers/        weather / workorder / wechat
alembic/            数据库迁移
tests/              单元 / 接口 / 闸门 / 注入 / 评测
eval/               评测集、eval_gate.py、reports/
docs/               规格与判据（唯一事实源）
```

- 新目录/新模块先改 `docs/06_工程化实施指南.md`，再落地代码。
- 请求链路必须带 `trace_id`；Agent 链路带 `thread_id`。
- 分层目录 `app/api`、`app/core`、`app/models`、`app/services` 已落地，新增模块不得绕过分层。
- 工作流选型以 `docs/工作流选型说明.md` 为准：主链路是受约束的多 Agent，确定性强的子流程用 Workflow。

## 运行基线

- 入口：`app.main:app`；健康检查 `GET /health` 返回 HTTP 200 与合法 JSON。
- 配置：`app/core/config.py` 使用 Pydantic Settings 读取项目根目录 `.env`；缺失时使用本地默认值，密钥只走环境变量/`.env`。
- 日志：`app/core/logging.py` 输出 JSON 行，每行含 `trace_id`；`app/core/middleware.py` 读写 `X-Trace-ID`，缺省自动生成。
- 分层：`app/api`（路由）、`app/core`（配置/日志/中间件）、`app/models`（ORM）、`app/services`（业务与 Tool）。

## 常用命令

以下命令随 Day 1 脚手架落地生效：

```bash
pip install -e ".[dev]"             # 安装依赖
uvicorn app.main:app --host 0.0.0.0 --port 8000  # 后端 :8000（日志全量 JSON + trace_id）
curl -i http://127.0.0.1:8000/health  # 健康检查，响应头含 X-Trace-ID
pytest -q                           # 单测 / 接口 / 闸门 / 注入用例
alembic revision --autogenerate -m "msg"  # 新建迁移（须人工审查）
alembic upgrade head                      # 应用迁移
python eval/eval_gate.py            # 评测门禁（pre-push 同入口）
docker compose up -d                # pg / redis / backend / frontend / Laya / MCP
npm --prefix frontend/pad run dev   # 平板前端
```

## 禁区

| 禁止 | 约束 |
| --- | --- |
| 连接生产数据库 | 只用本机 Docker 或教学 mock；`DATABASE_URL` 默认 localhost |
| 硬编码 key / 口令 / token | LLM、ASR/TTS、JWT、数据库密钥全部走 `.env` + Pydantic Settings；`.env` 不入库 |
| 医疗诊断结论 | B1：只记录/提醒，异常统一"建议问医生"并告警人工 |
| 替代 SOS 或急救 | B2：急症只告警，不做急救引导 |
| 高精度 3D 建模 / 动捕 | B3：只用现成 VRM + viseme，不写图形学 |
| AI 歌曲生成 / 演唱 | B4：娱乐只走已授权戏曲/老电影 |
| 敏感语音文本外发第三方推理 API | B5：System One 必须本地 Laya |
| 使用未授权曲库/影库 | B6：仅教学模拟、已授权或公有领域素材 |
| 接入物业/支付/门禁系统 | B7：外部依赖仅微信/HIS mock |
| 存完整病历或原始录音 | B8：只存结构化摘要；音频中间态 72h TTL |
| 移动端原生 App / 多租户 / diarization | B9 家属侧仅最简 H5；B10 单社区单实例；B11 重叠语音只澄清 |
| 日志无 `trace_id`、落身份证号或具体剂量 | 每行 JSON 带 `trace_id`；敏感字段脱敏后落盘 |
| 提交密钥、录音、模型权重、数据库导出 | 一律禁止 |

## 高风险文件清单

| 路径 | 风险 | 改动要求 |
| --- | --- | --- |
| `app/core/**auth*`、`app/api/**/auth*`、JWT/权限中间件 | 人/设备双 JWT、角色越权 | 必须补越权用例；身份只从 token / `runtime_context` 取，不信请求体 |
| `app/core/config.py`、`.env*` | 密钥/口令泄露、配置漂移 | 只从环境变量/根目录 `.env` 读取；密钥用 `SecretStr`；`.env` 不入库 |
| `alembic/**`、`alembic/versions/**` | 不可逆 schema、敏感字段 | 只走迁移不手改库；可回滚；禁止 `tenant_id` 与 B8 字段 |
| `app/services/tools/**`、`app/router/**` | 越权调用、死循环 | Tool 身份从 `runtime_context.elder_id` 取（闸门 3）；≤8 次/轮；补越权用例 |
| `mcp-servers/**` | 任意命令/URL/文件访问、数据外泄 | 只暴露白名单工具；外部依赖走 mock/内网；调用留审计日志 |
| `Dockerfile*`、`docker-compose*.yml` | 密钥入镜像、端口暴露、root 运行 | 非 root、固定基础镜像 tag、不写密钥、不挂生产数据、DB/Redis 不暴露公网 |

- 三道闸门（会话 / 记忆 / 工具）失败即阻断发布：伪造 thread_id 返回 403；pgvector 查询必须带 `elder_id`；Tool 身份只认 `runtime_context`。
- 核心 Tool 与权限场景单测覆盖 100%，接口 ≥70%；`eval_gate` 未过不得推送。

## 模型路由表

| 层 | 模型/服务 | 部署 | 职责 | 触发与降级 |
| --- | --- | --- | --- | --- |
| 规则层（前置） | 关键词/正则/状态机 | 本地 | 确定性指令、敏感词、设备状态 | 命中直接返回，不调模型 |
| S1 快决策 | Laya `convaiinnovations/laya`（`subfolder=multilingual`） | 本地 CPU | 7 类意图、敏感、是否升级、隐私收敛；P95 ≤200ms（目标） | 置信度 ≥0.85 直接闭环；<0.85 升级 S2；Laya 失败则全走 S2 |
| S2 开放域 | DeepSeek / Qwen | 第三方 API（key 走环境变量） | 复杂对话、Tool 编排、人设 + 记忆 | 超时/限流重试 1 次，失败用预设话术兜底 |
| ASR | 第三方流式 ASR（带置信度） | 第三方 API | 语音转文本 | 不可用 → 文字模式 + 护工工单 |
| TTS | 第三方流式 TTS（viseme 时间轴） | 第三方 API | 语音合成、口型驱动 | 不可用 → 文字模式 + 护工工单 |

- 三级路由实现在 `app/router/`；改路由必须跑 `python eval/eval_gate.py`。
- 敏感判断宁可错杀；命中即一票否决，转护工 HITL，并写 `decision_logs`。
- 高危副作用（敏感意图、漏服升级、健康告警、用药变更）必须人工确认（HITL）。
- S1 判据：意图准确率 ≥90%、敏感召回 ≥95%（50 条标注集，未验证）；P3 延迟实测（2026-11-08，Ryzen 9 7945HX/CPU）：单问 P50 78ms、四判断 P50 223ms，四判断未达 200ms；改问题集/路由需复测。
- 目标：S1 闭环率 ≥60%，单会话 Tool 调用 ≤8 次。

## 文风

文档与注释只写约束、判据、命令，不写大段教程或背景铺垫；提交说明写清"为什么"。
