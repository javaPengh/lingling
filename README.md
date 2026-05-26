# 灵灵老师 V0.1

本仓库是灵灵老师 V0.1 的本地全栈 Web 应用骨架。

## 规格索引

- [项目主规格](docs/项目主规格.md)
- [MVP 核心流程说明](docs/MVP核心流程说明.md)
- [数据模型规格](docs/数据模型规格.md)
- [教学编排器决策规格](docs/教学编排器决策规格.md)
- [灵灵人设与提示词规格](docs/灵灵人设与提示词规格.md)
- [种子数据与演示脚本](docs/种子数据与演示脚本.md)
- [技术架构与选型说明](docs/技术架构与选型说明.md)
- [开发计划与任务分工](docs/开发计划与任务分工.md)

## 目录

```text
lingling/
├─ shared/        # 前后端共享 API 类型
├─ server/        # Node + Express 后端
├─ web/           # React + Vite 前端
├─ docs/          # 产品与技术规格
└─ lingling.db    # SQLite 数据库，运行时生成
```

## 启动

需要 Node.js 24+。后端 SQLite 访问层先使用 Node 内置 `node:sqlite`，不引入额外原生依赖。

```bash
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`，后端默认运行在 `http://localhost:3001`。

## 环境变量

复制 `.env.example` 为 `.env` 后按需填写。V0.1 默认使用 `LLM_MODE=mock`，真实模型密钥只放在后端环境变量中。
