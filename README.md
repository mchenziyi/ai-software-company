# AI Software Company — MVP

最小可验证闭环：**用户需求 → PRD → 评审 → 共识 → 冻结**

## 目录结构

```
ai-software-company/
├── .aisc/                    # 系统元数据
│   ├── project.json
│   ├── stages/01-requirement/
│   ├── meetings/01-requirement/
│   └── memory/{agent}/
├── docs/
│   ├── requirement.md        # 用户原始需求
│   └── prd.md                # 当前 PRD 工作副本
└── orchestrator.py           # MVP 编排脚本
```

## 运行

```bash
export DEEPSEEK_API_KEY=sk-...

# 1. 编辑用户需求
vim docs/requirement.md

# 2. 运行 MVP
python3 orchestrator.py
```

## 流程

```
requirement.md  →  PM Agent 起草 PRD v1
                      ↓
               创建评审会议（5 个 Agent 并行审阅）
                      ↓
               Project Manager 汇总裁决
                      ↓
               Revise ←→ Freeze（最多 5 轮，超出升级用户）
```

## MVP 已支持

- Requirement Stage 完整闭环：Draft → Review → Revise → Freeze
- 5 个角色并行评审 + Project Manager 汇总裁决
- 断点续跑：重新运行从当前版本继续，不覆盖已有产物
- 会议审计：每次评审生成独立会议文件，meeting_counter 递增

## MVP 不做的事

- 只有 Requirement 一个 Stage，没有后续 API/DB/开发阶段
- 不涉及 Git 操作
- 不涉及 UI
- Agent 记忆只做基本沉淀，不实现完整的 OKF 检索
