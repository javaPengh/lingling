# AGENTS.md

## Python Environment

The backend always uses the Conda `base` Python environment:

```powershell
D:\ai_study_app\anaconda3\python.exe
```

Use this environment for running the backend, installing backend dependencies, and executing backend scripts.

## Backend Placement Rule

Follow the FastAPI layering under `server/`:

- HTTP request/response only: `server/api/routes/`
- Business logic: `server/services/`
- SQLite access only: `server/dao/`
- Pydantic entities and DTOs: `server/models/`
- LLM adapters and prompts: `server/llm/`
- Global config and enums: `server/core/`

When adding files, place them by responsibility rather than convenience.

## Documentation Rule

- New files need a file-level docstring or comment explaining their responsibility.
- New public interfaces and functions need docstrings explaining what they do.
- New entity classes need class docstrings, and every entity field needs a field description.
- New enum classes need class docstrings, and every enum member needs a short comment.
- After completing a development task, update `docs/实施历史与变更记录.md` with the actual implementation at a coarse task level. Treat other files under `docs/` as plans/specifications/reference material. If the implementation differs from those plan documents, record the difference and the reason; if the reason is unknown, ask the user before writing it. Keep the history focused on key facts, and do not add verification-result or follow-up sections.

## 扩展性原则(写代码与设计时遵循)
本项目当前阶段是 MVP 演示,但愿景是一个商业化学习软件。因此写代码和做设计时,不要把实现框死在"只为演示够用"的层面,要为未来的真实业务规模预留扩展空间。
具体把握以下区分:

- 在"改起来贵"的地方必须预留扩展性:数据模型、数据库结构、后端架构、模块分层、API 接口设计。这些事后重构成本极高,从一开始就要按"将来会有大量真实用户/数据"来设计。
- 在"改起来便宜"的地方按当前阶段需要来做,不必过度设计:具体的界面形态、视觉样式、交互细节。这些改动成本低,且不同阶段本就该有不同形态,不要为想象中的未来形态牺牲当前的体验和清晰度。
- 判断准则:预留扩展性,是为了避免"未来不得不推倒重写";不是为了"现在就把每个细节都做成未来的样子"。
