# Day 01 验收报告

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 康伴数字人（konban） |
| 验收阶段 | Day 1 / Iter 1 地基 |
| 验收日期 | 2026-11-09 |
| 代码分支 | `kangban` |
| 远端仓库 | `https://github.com/userdodo3708/Kangban2026_claude.git` |
| 验收执行 | AI 编码代理（Claude Code） |
| 复核人 | 项目负责人（待签） |
| 最终结论 | **有条件通过（Conditional Pass）** |

> 本报告只判定 Day 1 范围。`docs/07_验收标准.md` 是系统最终验收标准，不适用本次阶段验收；ASR/TTS、WebRTC、S1/S2、身份权限、记忆、Tool/MCP、前端、Docker Compose、端到端时延等均不在本次判定范围。

---

## 一、检测概览

### 1.1 验收依据

| 依据 | 内容 |
| --- | --- |
| `docs/06_工程化实施指南.md` §六 | Git 仓库首次 commit 含 `pyproject.toml`、`.env.example`、`.gitignore`、`README.md`、`AGENTS.md`；FastAPI 可由 uvicorn 启动；`/health`；Pydantic Settings 加载 `.env`；结构化日志带 `trace_id`；目录分层 |
| `docs/06_工程化实施指南.md` §七 Day 1 DoD | FastAPI 骨架 + Git + AGENTS.md + 11 表设计（前 4 张建库） |
| `AGENTS.md` 运行基线 | 入口 `app.main:app`；`GET /health` 返回 200 与合法 JSON；日志每行含 `trace_id`；`X-Trace-ID` 读写；目录分层 |
| `docs/工程结构规范`（§五） | `app/api`、`app/core`、`app/models`、`app/router`、`app/system_one`、`app/services`、`frontend/pad`、`mcp-servers`、`tests`、`eval`、`alembic` |

### 1.2 验收范围

**纳入本次验收：**

- FastAPI 应用可启动，`/health` 状态码、响应头、响应体。
- `trace_id` 的生成、透传、非法值替换、日志关联。
- 结构化 JSON 日志与 uvicorn 访问日志的 `trace_id` 覆盖。
- Pydantic Settings 从项目根目录 `.env` 加载配置，密钥使用 `SecretStr`。
- 目录分层与 Day 1 文件清单。
- 11 张表的 SQLAlchemy 模型、Alembic 迁移链、离线 DDL。
- 依赖声明、解析、冲突检查、已知漏洞审计、依赖范围合规。
- `.env` 提交边界与密钥/敏感文件扫描。
- 单元/接口测试。
- `AGENTS.md`、`README.md`、Git 首次提交等交付基线。

**不纳入本次验收：**

- `docs/07_验收标准.md` 中的全系统指标：端到端 P95 ≤1.5s、S1 准确率/召回率/闭环率、声纹识别、双人重叠语音、三道闸门、HITL 全链路、评测门禁阈值。
- ASR/TTS、WebRTC、3D 形象、Laya 在线推理、DeepSeek/Qwen 调用、LangGraph 多 Agent、MCP Server。
- 长者/护工/医生/家属/管理员前端页面；`frontend/pad` 仅有占位目录。
- Docker Compose 运行、PostgreSQL/pgvector 实际容器编排、Langfuse。
- `eval/eval_gate.py` 的评测逻辑与 pre-push 拦截效果。

### 1.3 验收环境

| 项 | 值 |
| --- | --- |
| 操作系统 | Windows 11 Home China 10.0.26200 |
| 主验收解释器 | Python 3.13.9（临时隔离 venv，未污染项目环境） |
| 对照解释器 | Python 3.12.7（Anaconda，当前 `uvicorn` 命令默认解释器） |
| 包管理 | `pip`，项目以 `pip install -e ".[dev]"` 安装 |
| 网络 | 本机代理 `127.0.0.1:7897`，对 PyPI/OSV 存在间歇性 SSL 握手失败；不影响已完成的批量审计 |
| 数据库 | 本次审计时本机 `localhost:5432` 未运行 PostgreSQL；Docker daemon 未启动 |

### 1.4 检测方法

| 检测 | 方法 |
| --- | --- |
| 接口功能 | 隔离 venv 启动 `python -m uvicorn app.main:app`，用 `curl` 验证状态码、响应头、响应体、404/405 |
| 日志 | 将 uvicorn stdout/stderr 重定向到文件，逐行 `json.loads`，统计 `trace_id`、`request_finished` |
| 配置 | `tests/test_config.py` 使用临时 `.env`，隔离系统环境变量后构造 `Settings` |
| 测试 | `python -m pytest -q`，在隔离 venv、项目 Python 3.13、Anaconda Python 3.12 分别执行 |
| 依赖冲突 | `pip check`；`pip freeze` 锁定完整闭包 |
| 漏洞 | `pip-audit 2.10.1`；因 PyPI JSON 接口被代理阻断，改用 OSV `querybatch` API 对 38 个包批量查询 |
| 迁移 | `alembic heads`；`alembic upgrade head --sql` 离线生成 PostgreSQL DDL；尝试 `alembic current` 连接本机库 |
| 提交边界 | `git status`、`git log`、`git check-ignore -v .env`、密钥正则扫描、敏感扩展名扫描 |

### 1.5 结果汇总

| 验收域 | 结果 | 摘要 |
| --- | --- | --- |
| FastAPI 骨架与 `/health` | **通过** | 200、合法 JSON、`X-Trace-ID` 正常 |
| `trace_id` 中间件 | **通过** | 生成、透传、非法替换均符合预期 |
| 结构化日志 | **通过（有已知边界）** | 23/23 行为 JSON 且含 `trace_id`；`--reload` 父进程日志除外 |
| Pydantic Settings | **通过** | 根 `.env` 加载、`SecretStr`、未知键忽略均有测试 |
| 目录分层 | **通过** | 规定目录均已建立 |
| AGENTS.md | **通过** | 约束、命令、禁区、高风险清单、模型路由齐全 |
| 11 表模型 | **通过** | 4 张核心表 + 7 张占位表，测试通过 |
| 迁移链与 DDL | **通过** | head `0002_remaining_tables`；离线 DDL 生成 11 张业务表 |
| 前 4 张表实际建库 | **待复验** | 本次环境无 PostgreSQL/Docker，无法复现 `alembic upgrade head` |
| 测试 | **通过** | 10 passed；1 条上游弃用警告 |
| 依赖声明与解析 | **通过** | 7 个必需包 + 2 个合理直接依赖；版本均在约束内 |
| 依赖冲突 | **通过（项目闭包）** | 隔离 venv `pip check` 无冲突；Anaconda 有无关的 `paddlex` 冲突 |
| 已知漏洞 | **通过（时点）** | OSV 查询 38 包，0 个已知漏洞 |
| 密钥/敏感文件 | **通过** | `.env` 已忽略；未发现硬编码密钥/私钥/录音/模型权重 |
| README.md | **不通过** | 0 字节，缺背景/架构/启动/配置/局限 |
| Git 首次提交 | **不通过** | 无任何 commit，全部文件未跟踪 |

---

## 二、功能验收结果

### 2.1 FastAPI 启动与健康检查

**命令：**

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
curl -sS -D - http://127.0.0.1:8011/health
```

**实测结果：**

| 检查项 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 服务启动 | 无启动异常，端口可连接 | 隔离 venv 启动成功，健康检查就绪 | 通过 |
| `GET /health` | HTTP 200 | `HTTP/1.1 200 OK` | 通过 |
| 响应体 | 合法 JSON，字段来自 Settings | `{"status":"ok","service":"konban","version":"0.1.0","environment":"local"}` | 通过 |
| 响应头 | 含 `X-Trace-ID` | `x-trace-id: b47f9c737f2f41558a56558136c354d6` | 通过 |
| `POST /health` | 方法不允许 | HTTP 405 | 通过 |
| `GET /not-found` | 未找到 | HTTP 404 | 通过 |

**结论：通过。** `/health` 满足“HTTP 200 + 合法 JSON + 响应头含 trace_id”的运行基线。

### 2.2 `trace_id` 中间件

| 场景 | 输入 | 实际输出 | 结果 |
| --- | --- | --- | --- |
| 无请求头 | 不传 `X-Trace-ID` | 自动生成 32 位 UUID hex，如 `b47f9c737f2f41558a56558136c354d6` | 通过 |
| 合法请求头 | `X-Trace-ID: acceptance-trace-002` | 原样返回 `acceptance-trace-002` | 通过 |
| 非法请求头 | `X-Trace-ID: bad trace id` | 替换为 `3d6df71af38a4144855fcd07a5c8d7da` | 通过 |
| 日志关联 | 带 `acceptance-trace-002` 的请求 | 该值出现在对应日志行 | 通过 |

**实现核对：** `app/core/middleware.py` 只接受长度 1–128、字符集为 `[A-Za-z0-9._-]` 的 trace_id；非法或缺失时使用 `uuid.uuid4().hex`；通过 `ContextVar` 向下游传播，并在 `finally` 中重置。纯 ASGI 实现避免 `BaseHTTPMiddleware` 导致 contextvar 丢失。

**结论：通过。**

### 2.3 结构化日志

**实测统计（隔离 venv，一次完整验收请求序列）：**

| 指标 | 结果 |
| --- | --- |
| 非空日志行数 | 23 |
| 可解析 JSON 行数 | 23 |
| 非 JSON 行数 | 0 |
| 含 `trace_id` 的行数 | 23 |
| `request_finished` 记录数 | 6 |
| 指定 `acceptance-trace-002` 出现 | 是 |

**日志样例（节选）：**

```json
{"timestamp":"2026-11-09T12:34:12.501872+00:00","level":"INFO","logger":"app.http","trace_id":"5a49cf78c2924f4fadb06b8a773fb6df","message":"request_finished method=GET path=/not-found status=404 duration_ms=0.35"}
```

**核对结论：**

- `app/http` 与 `uvicorn.access` 均输出 JSON，且每行带 `trace_id`。
- 日志包含 `timestamp`、`level`、`logger`、`trace_id`、`message`；异常时补充 `exception`/`stack`。
- **已知边界：** `uvicorn --reload` 的 reloader 父进程会输出 3 行不受应用 logging 配置控制的原始日志（“Will watch for changes / Uvicorn running / Started reloader process”）。验收基线使用**非 reload** 命令；该边界已写入 `AGENTS.md` 与 `docs/工作流选型说明.md`，但 README 尚未说明。

**结论：通过（非 reload 基线）；reload 父进程日志为已知边界。**

### 2.4 Pydantic Settings

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| 从项目根目录 `.env` 加载 | 通过 | `PROJECT_ROOT = parents[2]`，`SettingsConfigDict(env_file=...)` |
| 缺失时使用本地默认值 | 通过 | `app_name=konban`、`app_version=0.1.0`、`app_env=local`、`debug=False` 等 |
| 密钥使用 `SecretStr` | 通过 | `deepseek_api_key: SecretStr \| None`；测试断言 `get_secret_value()` |
| 未知环境变量不报错 | 通过 | `extra="ignore"`；测试写入 `UNKNOWN_KEY=ignored` 后仍可加载 |
| 配置测试 | 通过 | `tests/test_config.py` 1 条用例 |

**结论：通过。**

### 2.5 目录分层与 Day 1 骨架

已建立并核对：

```text
app/api/            health.py
app/core/           config.py、logging.py、middleware.py
app/models/         base.py、room.py、device.py、elder.py、persona.py、placeholder.py
app/router/         rules.py（占位，0 字节）
app/system_one/     questions.py（占位，0 字节）
app/services/       __init__.py（占位）
frontend/pad/       .gitkeep（占位）
mcp-servers/        .gitkeep（占位）
alembic/            env.py、script.py.mako、versions/0001、0002
tests/              test_health.py、test_config.py、test_models_schema.py
eval/               eval_gate.py（占位，0 字节）
docs/               规格、工作流选型说明、本报告
```

**结论：通过。** Day 1 只要求目录分层与骨架；`app/router/rules.py`、`app/system_one/questions.py`、`eval/eval_gate.py` 为空占位，符合后续 Day 的实现节奏，但 `AGENTS.md` 的“常用命令随 Day 1 生效”表述需要与实际能力区分（见 4.2）。

### 2.6 数据模型与迁移

#### 2.6.1 模型

| 项 | 结果 |
| --- | --- |
| 表总数 | 11 |
| 核心表 | `rooms`、`devices`、`elders`、`personas` |
| 占位表 | `memory_chunks`、`medication_plans`、`media_library`、`health_records`、`voiceprints`、`work_orders`、`conversations` |
| 核心表列集合 | 与 `docs/02_技术规范.md` 第九章一致，由 `tests/test_models_schema.py` 断言 |
| 占位表约束 | 每张表仅主键，无外键 |
| 索引/外键 | `ix_personas_voice_id`；`ix_rooms_occupant_ids` GIN；`elders.persona_id → personas.persona_id`；`devices.room_id → rooms.room_id` |
| 禁区字段 | 未发现 `tenant_id`、身份证号、诊断、病历、剂量、原始音频字段；仅 `elders` 注释声明“不含病历字段（B8）” |

#### 2.6.2 迁移

| 检查项 | 结果 |
| --- | --- |
| `alembic heads` | `0002_remaining_tables (head)` |
| 迁移文件 | `0001_core_schema.py`、`0002_remaining_tables_placeholder.py` |
| 离线 DDL | `alembic upgrade head --sql` 退出码 0，生成 4181 字节 |
| `CREATE TABLE` 数 | 12（11 张业务表 + `alembic_version`） |
| 约束/索引 | `ck_rooms_bed_count_positive`、`ck_elders_gender_valid`、`ck_elders_status_valid`、`ck_devices_status_valid`、两个外键、GIN 索引均生成 |
| 实时建库 | **未复验**：`alembic current` 连接 `localhost:5432` 被拒绝；`docker version` 无法连接 Docker daemon；本机无 `psql`/`pg_ctl` |

**结论：模型与迁移脚本通过；Day 1 DoD 的“前 4 张表建库”本次无法现场复验，列为待复验项。** 复验命令：

```bash
# 启动本机 PostgreSQL（或 Docker Postgres）后
DATABASE_URL='postgresql+psycopg2://localhost:5432/konban' alembic upgrade head
DATABASE_URL='postgresql+psycopg2://localhost:5432/konban' alembic current
# 预期 current 为 0002_remaining_tables，且 rooms/devices/elders/personas 存在
```

### 2.7 测试结果

| 环境 | 命令 | 结果 |
| --- | --- | --- |
| 隔离 venv（Python 3.13.9） | `python -m pytest -q` | **10 passed**，1 warning，0.62s |
| 项目 Python 3.13 | `python -m pytest -q` | **10 passed** |
| Anaconda Python 3.12.7 | `D:/anacanda3/python.exe -m pytest -q` | **10 passed** |

测试构成：

| 文件 | 用例数 | 覆盖内容 |
| --- | --- | --- |
| `tests/test_health.py` | 5 | `/health` 状态码/响应体、trace 透传、非法 trace 替换、日志 Filter、JSON Formatter |
| `tests/test_config.py` | 1 | 根 `.env` 加载、`SecretStr`、未知键忽略 |
| `tests/test_models_schema.py` | 4 | 11 表列集合、占位列仅主键、索引/外键、ORM 关系 |

**警告：**

```text
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated;
install `httpx2` instead.
```

该警告来自当前 FastAPI/Starlette 上游测试客户端，不影响 10 条用例通过；本次不引入 `httpx2`，待上游版本稳定后统一处理。项目 Python 3.13 环境另有 `anyio.abc.BlockingPortal` 别名弃用警告；Anaconda 环境无警告。两者均为上游依赖告警，不影响用例通过。

**结论：通过。** 未统计覆盖率；`AGENTS.md` 中“核心 Tool 与权限场景 100%、接口 ≥70%”适用于后续包含 Tool/权限的迭代，本阶段没有对应模块。

### 2.8 文档与 Git 交付基线

| 检查项 | 实际 | 结果 |
| --- | --- | --- |
| `AGENTS.md` | 7688 字节，含项目定位、技术栈、目录、运行基线、命令、禁区、高风险清单、模型路由 | 通过 |
| `docs/工作流选型说明.md` | 已创建，含目标用户、核心流程、技术栈、禁区、验收方式、类型判定、Day 1 映射 | 通过 |
| `.env.example` | 432 字节，仅安全占位值与注释键名 | 通过 |
| `.gitignore` | 覆盖 `.env`、`.env.*`、`__pycache__`、`.venv`、`node_modules`、构建产物、日志 | 通过 |
| `README.md` | **0 字节** | **不通过** |
| Git 首次提交 | **无任何 commit**；`git log` 报 “does not have any commits yet”；全部文件未跟踪 | **不通过** |
| 远端 | `origin` 指向 `https://github.com/userdodo3708/Kangban2026_claude.git` | 通过 |

**结论：交付基线未闭环。** `docs/06` §六明确要求首次 commit 含 `pyproject.toml`、`.env.example`、`.gitignore`、`README.md`、`AGENTS.md`；`README.md` 还要求包含“背景/架构/启动/配置/局限”。当前两项均未满足。

---

## 三、依赖合规性检查结果

### 3.1 声明依赖

`pyproject.toml` 声明 `requires-python = ">=3.10"`。

**运行时直接依赖（9 个）：**

| 包 | 约束 | 用途 | 范围判定 |
| --- | --- | --- | --- |
| `fastapi` | `>=0.115,<1.0` | HTTP/SSE/WebRTC 信令框架 | 技术栈明确要求 |
| `uvicorn[standard]` | `>=0.30,<1.0` | ASGI 运行入口 | 技术栈明确要求 |
| `pydantic` | `>=2.8,<3.0` | Pydantic v2 数据模型 | 技术栈明确要求（FastAPI 亦依赖） |
| `pydantic-settings` | `>=2.4,<3.0` | 根 `.env` 配置加载 | 技术栈明确要求 |
| `sqlalchemy` | `>=2.0,<3.0` | ORM | 技术栈明确要求 |
| `alembic` | `>=1.13,<2.0` | 数据库迁移 | 技术栈明确要求 |
| `psycopg2-binary` | `>=2.9,<3.0` | PostgreSQL 驱动 | 存储层 PostgreSQL 必需 |
| `redis` | `>=5.0,<7.0` | 会话/缓存 | 技术栈明确要求 |
| `apscheduler` | `>=3.10,<4.0` | 定时任务 | 技术栈明确要求 |

**开发依赖（2 个）：**

| 包 | 约束 | 用途 |
| --- | --- | --- |
| `pytest` | `>=8.0,<10.0` | 测试 |
| `httpx` | `>=0.27,<1.0` | FastAPI `TestClient` |

**结论：** 7 个任务明确要求的包全部存在；额外直接依赖 `pydantic` 与 `psycopg2-binary` 均由“Pydantic v2 + PostgreSQL”技术栈直接要求，不属于超范围引入。`pytest`、`httpx` 仅在 `dev` extra，不进入运行时依赖。

### 3.2 解析版本（隔离 venv）

| 包 | 解析版本 | 是否在约束内 |
| --- | --- | --- |
| `fastapi` | 0.162.2 | 是 |
| `uvicorn` | 0.54.0 | 是 |
| `pydantic` | 2.14.3 | 是 |
| `pydantic-settings` | 2.16.2 | 是 |
| `sqlalchemy` | 2.1.8 | 是 |
| `alembic` | 1.20.1 | 是 |
| `psycopg2-binary` | 2.9.13 | 是 |
| `redis` | 6.4.0 | 是 |
| `apscheduler` | 3.11.3 | 是 |
| `pytest` | 9.2.0 | 是 |
| `httpx` | 0.28.1 | 是 |
| `starlette`（传递） | 1.10.0 | 由 FastAPI 约束 |

对照环境解析结果不同但均通过测试：项目 Python 3.13 为 `fastapi 0.115.14 / starlette 0.46.2 / sqlalchemy 2.0.55`；Anaconda Python 3.12 为 `fastapi 0.162.2 / starlette 1.10.0 / sqlalchemy 2.0.52`。这说明宽版本区间允许不同解析结果，功能兼容，但可复现性不足（见 4.2）。

**Python 版本覆盖：** 实测 Python 3.13.9 与 3.12.7；未实测 Python 3.10，`requires-python >=3.10` 的声明未在本机 3.10 解释器上验证。

### 3.3 依赖冲突检查

| 环境 | 命令 | 结果 |
| --- | --- | --- |
| 隔离 venv（仅项目闭包） | `pip check` | `No broken requirements found.` |
| 项目 Python 3.13 | `pip check` | 无损坏依赖 |
| Anaconda Python 3.12 | `pip check` | `paddlex 3.7.2 has requirement PyYAML==6.0.2, but you have pyyaml 6.0.3` |

**判定：**

- 项目依赖闭包无冲突；隔离 venv 的 38 个包全部可解析、可安装、10 条测试通过。
- Anaconda 的 `paddlex` 冲突是既有环境问题，与本项目依赖无关；但当前 shell 的裸 `uvicorn` 命令解析到 Anaconda（Python 3.12.7），因此实际运行时可能受该环境污染。建议项目统一使用独立 venv，不以 base Anaconda 作为验收解释器。

### 3.4 已知漏洞审计

| 项 | 内容 |
| --- | --- |
| 工具 | `pip-audit 2.10.1` |
| 依赖闭包 | 隔离 venv `pip freeze`，38 个包 |
| 数据库 | OSV `querybatch` API（PyPI JSON 接口被本机代理间歇阻断，未使用） |
| 查询日期 | 2026-11-09 |
| 结果 | **38 个包，0 个存在已知漏洞的包，0 个已知漏洞** |

**说明：** “0 个已知漏洞”是 OSV 数据库在查询时点的结果，不等于“绝对无漏洞”。依赖漏洞库会持续更新，建议在 CI 或 pre-push 中固定执行同一审计，并将结果纳入发布门禁。

### 3.5 依赖范围与供应链边界

- 直接运行时依赖 9 个、开发依赖 2 个；其余 27 个为传递依赖，完整闭包 38 个。
- `uvicorn[standard]` 带入的 `httptools`、`watchfiles`、`websockets`、`python-dotenv`、`PyYAML` 等属于该 extra 的正常组成。
- `fastapi 0.162.2` 带入 `opentelemetry-api` 与 `annotated-doc`，属于上游 FastAPI 的传递依赖，不是项目直接引入；当前未配置 OTel exporter，不会主动外发遥测。
- 未引入与 Day 1 技术栈无关的框架、云 SDK、支付/物业/门禁 SDK、音视频处理库或模型权重。
- 未发现 `tenant_id`、多租户抽象、病历/原始录音字段。
- **缺口：** 无锁文件（`uv.lock` / `requirements.lock` / constraints）。不同环境中同一 `pyproject.toml` 会解析出不同版本，建议补充锁文件并在 README 写明安装方式。

### 3.6 密钥与敏感文件

| 检查项 | 结果 |
| --- | --- |
| `.env` 是否被忽略 | 是；`git check-ignore -v .env` → `.gitignore:1:.env` |
| `.env` 是否被读取/打印 | 否；仅确认存在（52 字节），未输出内容 |
| `.env.example` | 432 字节，仅占位值；密钥项以注释形式留空 |
| 硬编码密钥扫描 | 未发现 `sk-...`、`AKIA...`、私钥头、JWT 形态字符串 |
| 敏感文件扫描 | 未发现 `.pem`、`.key`、`.p12`、`.wav`、`.mp3`、`.mp4`、`.pth`、`.pt`、`.onnx`、`.bin`、`.dump`、`.sql.gz` |
| 日志敏感字段 | 当前仅有请求方法与路径；未落身份证号、剂量、密钥 |

**结论：通过。**

---

## 四、存在的问题及改进建议

### 4.1 问题清单

| ID | 等级 | 问题 | 证据 | 改进建议 | 关闭条件 |
| --- | --- | --- | --- | --- | --- |
| P1-01 | **阻断** | 仓库没有任何 commit，全部文件未跟踪，未形成可复现交付基线 | `git log` 报 “does not have any commits yet”；`git status` 全部为 `??` | 在确认文件清单后创建首次 commit；`.env` 已被忽略，提交前用 `git status` 复核暂存区 | `git rev-parse HEAD` 成功，首次 commit 含 `pyproject.toml`、`.env.example`、`.gitignore`、`README.md`、`AGENTS.md`，且不含 `.env` |
| P1-02 | **阻断** | `README.md` 为 0 字节，缺少 `docs/06` 要求的背景/架构/启动/配置/局限 | `wc -c README.md` → 0 | 补写五节；写明 venv 安装、`uvicorn` 非 reload 启动、`/health` 与 `X-Trace-ID` 验证、当前占位模块、已知边界 | README 非空且五节齐全，命令可直接复制执行 |
| P2-01 | **重要** | Day 1 DoD 的“前 4 张表建库”本次无法现场复验 | `alembic current` 连接 `localhost:5432` 被拒绝；Docker daemon 未启动；无 `psql`/`pg_ctl` | 启动本机 PostgreSQL 或临时 Docker Postgres，执行 `alembic upgrade head`，核对 4 张核心表 | `alembic current` 为 `0002_remaining_tables`，`rooms/devices/elders/personas` 均存在，输出留档 |
| P2-02 | **重要** | `AGENTS.md` 宣称“常用命令随 Day 1 生效”，但 `docker compose up -d` 与 `npm --prefix frontend/pad run dev` 当前不可用 | `docker-compose.yml` 0 字节，`docker compose ps` 报 “empty compose file”；`frontend/pad` 仅有 `.gitkeep`，无 `package.json` | 将这两条命令标注为“后续 Day 生效”，或补充最小可运行 compose / 前端骨架 | 命令可执行，或文档明确标注未到生效日 |
| P2-03 | **重要** | `eval/eval_gate.py` 为 0 字节，执行退出码 0，但未做任何评测；`AGENTS.md` 将其描述为“未过不得推送”的门禁 | `python eval/eval_gate.py` 无输出、退出 0；`eval/eval_gate.py` 0 字节；`.git/hooks/pre-push` 不存在 | 在评测逻辑落地前明确标注“占位、未接 pre-push”；落地后实现阈值并接入 hook | `eval_gate.py` 非空、失败时非零退出，且 pre-push 实际调用 |
| P2-04 | **重要** | 无锁文件，依赖解析不可复现 | 隔离 venv 与项目环境解析出不同 `fastapi/starlette/sqlalchemy` 版本；无 `uv.lock`/`requirements.lock` | 生成并提交锁文件或 constraints，CI 按锁文件安装 | 锁文件入库，README 写明安装命令，CI 使用同一锁文件 |
| P3-01 | 建议 | Anaconda base 环境存在既有 `paddlex`/`PyYAML` 冲突，裸 `uvicorn` 默认使用该解释器 | `pip check` 报 `paddlex 3.7.2` 要求 `PyYAML==6.0.2`，实际 6.0.3 | 项目统一使用独立 venv；README 写明激活方式；验收以项目 venv 为准 | 项目环境 `pip check` 干净，验收命令不依赖 base Anaconda |
| P3-02 | 建议 | `uvicorn --reload` 的 reloader 父进程日志为原始文本，不含 `trace_id` | reload 模式启动时输出 3 行非 JSON 日志 | 保持非 reload 验收基线；在 README“局限”中说明；如必须 reload，另行配置父进程日志 | README 记录该边界，验收命令固定非 reload |
| P3-03 | 建议 | 测试出现上游依赖弃用警告 | 隔离 venv：`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`；项目 Python 3.13：`DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated` | 暂不引入 `httpx2`；跟踪 FastAPI/Starlette/anyio 版本，稳定后统一升级 | 升级后警告消失，或项目明确记录抑制理由 |
| P3-04 | 建议 | `requires-python >=3.10` 未在 Python 3.10 实测 | 本次仅覆盖 3.13.9 与 3.12.7 | 若交付环境可能使用 3.10，补一次 3.10 CI 矩阵 | Python 3.10 环境 10 条测试通过 |

### 4.2 整改优先级

**签收前必须完成：**

1. 创建首次 commit，并确认 `.env` 未入库（P1-01）。
2. 补全 `README.md` 五节内容（P1-02）。
3. 启动本机 PostgreSQL，完成 `alembic upgrade head` 与 4 张核心表核对（P2-01）。

**建议在 Day 2 前完成：**

4. 标注或补齐 `docker compose` / `frontend` / `eval_gate` 的生效状态（P2-02、P2-03）。
5. 增加锁文件与独立 venv 安装说明（P2-04、P3-01）。
6. README 记录 `--reload` 日志边界与上游警告（P3-02、P3-03）。

---

## 五、最终验收结论

### 5.1 Day 1 判据对照

| Day 1 判据 | 结果 | 说明 |
| --- | --- | --- |
| FastAPI 骨架可由 uvicorn 启动 | **通过** | 隔离 venv 启动成功，端口可访问 |
| `GET /health` 返回 HTTP 200 + 合法 JSON | **通过** | 响应体字段与 Settings 一致 |
| Pydantic Settings 加载根 `.env` | **通过** | 含 `SecretStr` 与未知键忽略测试 |
| 结构化日志每行含 `trace_id` | **通过** | 23/23 行 JSON 且含 `trace_id`；reload 父进程除外 |
| 目录分层（api/core/models/services 等） | **通过** | 规定目录与占位文件齐全 |
| `AGENTS.md` | **通过** | 约束、禁区、高风险、模型路由齐全 |
| 11 表设计 | **通过** | 4 核心 + 7 占位，模型测试通过 |
| 前 4 张表建库 | **待复验** | 本次无 PostgreSQL/Docker；离线 DDL 已生成 |
| Git 交付基线 | **不通过** | 无首次 commit |
| README | **不通过** | 0 字节 |
| 依赖完整、版本匹配、无冲突 | **通过** | 隔离 venv `pip check` 干净；Anaconda 冲突与本项目无关 |
| 依赖范围合规 | **通过** | 9 运行时 + 2 开发直接依赖，均有技术栈依据 |
| 无已知安全漏洞 | **通过（时点）** | OSV 38 包 0 已知漏洞 |
| 测试 | **通过** | 10/10，通过于 Python 3.13 与 3.12 |
| 密钥/敏感文件边界 | **通过** | `.env` 已忽略；未发现硬编码密钥或敏感二进制 |

### 5.2 结论

**Day 1 核心功能与依赖合规性通过；交付基线未完全闭环，最终结论为“有条件通过（Conditional Pass）”。**

具体表述：

- **功能层面通过：** FastAPI 骨架、`/health`、`trace_id`、结构化 JSON 日志、Pydantic Settings、目录分层、11 表模型与迁移链均满足 Day 1 技术要求。
- **依赖层面通过：** 任务要求的 7 个包全部存在；隔离环境 `pip check` 无冲突；OSV 未发现已知漏洞；未引入超出技术栈的直接依赖。
- **交付层面未闭环：** 没有首次 commit，`README.md` 为空；这两项是 `docs/06` §六的明确要求，不能判定为“完全通过”。
- **证据缺口：** 本次审计时本机 PostgreSQL/Docker 不可用，“前 4 张表建库”只能以离线 DDL 和模型测试证明，未能现场复验实际数据库对象。

完成 4.2 中“签收前必须完成”的 3 项后，可将结论更新为**通过**；在此之前，建议以“有条件通过”作为阶段性交付依据。

### 5.3 声明

- 本报告不构成 `docs/07_验收标准.md` 的全系统验收结论，也不覆盖尚未实现的语音、Agent、权限、Tool/MCP、前端与端到端指标。
- 漏洞审计为 2026-11-09 时点结果；依赖库更新后应重新执行。
- 本报告未提交、未推送任何 Git 变更；报告文件本身位于 `docs/reports/Day01验收报告.md`。

---

## 附录 A：关键验收命令

```bash
# 1. 隔离环境安装与测试
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m pytest -q

# 2. 启动与接口验收（非 reload）
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
curl -i http://127.0.0.1:8000/health
curl -i -H "X-Trace-ID: acceptance-trace-002" http://127.0.0.1:8000/health

# 3. 迁移检查
python -m alembic heads
DATABASE_URL='postgresql+psycopg2://localhost:5432/konban' alembic upgrade head
DATABASE_URL='postgresql+psycopg2://localhost:5432/konban' alembic current

# 4. 依赖审计（示例；pip-audit 不进入项目依赖）
python -m pip freeze --exclude-editable > /tmp/project-freeze.txt
pip-audit -r /tmp/project-freeze.txt
```

## 附录 B：隔离 venv 依赖闭包（38 个）

```text
alembic==1.20.1
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.16.0
APScheduler==3.11.3
certifi==2026.10.23
click==8.5.1
colorama==0.4.6
fastapi==0.162.2
h11==0.16.0
httpcore==1.0.9
httptools==0.9.0
httpx==0.28.1
idna==3.20
iniconfig==2.3.1
Mako==1.4.3
MarkupSafe==3.0.4
opentelemetry-api==1.45.2
packaging==26.3
pluggy==1.7.0
psycopg2-binary==2.9.13
pydantic==2.14.3
pydantic-settings==2.16.2
pydantic_core==2.50.4
Pygments==2.21.0
pytest==9.2.0
python-dotenv==1.2.4
PyYAML==6.0.3
redis==6.4.0
SQLAlchemy==2.1.8
starlette==1.10.0
typing-inspection==0.4.5
typing_extensions==4.16.0
tzdata==2026.6
tzlocal==5.4.5
uvicorn==0.54.0
watchfiles==1.3.0
websockets==17.4
```

## 附录 C：11 张业务表清单

```text
核心表（4）：
  personas
  rooms
  elders
  devices

占位表（7，仅主键）：
  memory_chunks
  medication_plans
  media_library
  health_records
  voiceprints
  work_orders
  conversations
```

## 附录 D：本次未覆盖项

| 类别 | 未覆盖内容 |
| --- | --- |
| 语音 | WebRTC、ASR（置信度）、TTS（viseme）、回声测试、全双工 |
| 模型 | Laya 在线分类、DeepSeek/Qwen 调用、S1 准确率/召回率/闭环率、S2 降级 |
| Agent | LangGraph Supervisor、五个子 Agent、`thread_id`、记忆与 pgvector |
| 安全 | 人/设备 JWT、角色越权、三道闸门、HITL、注入用例 |
| Tool/MCP | weather/workorder/wechat MCP、白名单、≤8 次/轮、审计日志 |
| 前端 | `frontend/pad` 页面、three-vrm、口型驱动 |
| 部署 | Docker Compose 全栈启动、pgvector、Redis、nginx、Langfuse |
| 评测 | `eval_gate.py` 阈值、50 条标注集、端到端 P95 ≤1.5s |
