#!/usr/bin/env python3
"""
AI Software Company — MVP Orchestrator

最小闭环：用户需求 → PRD 起草 → 需求评审 → 共识裁决 → PRD 冻结
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

# ─── Config ───────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent
AISC_DIR = PROJECT_ROOT / ".aisc"
STAGES_DIR = AISC_DIR / "stages"
MEETINGS_DIR = AISC_DIR / "meetings"
MEMORY_DIR = AISC_DIR / "memory"
DOCS_DIR = PROJECT_ROOT / "docs"

# LLM config — 复用 Reasonix 的环境变量
LLM_API_KEY = os.environ.get("DEEPSEEK_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
LLM_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")

# ─── Minimal LLM caller (不依赖任何框架) ─────────────────────

def call_llm(system_prompt: str, user_prompt: str, model: Optional[str] = None) -> str:
    """最简单的 LLM 调用 — 通过 subprocess 调 curl 兼容 Python 3.9 SSL 环境."""
    import subprocess

    body = json.dumps({
        "model": model or LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
    })

    url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
    
    try:
        result = subprocess.run([
            "curl", "-s", "-m", "120",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {LLM_API_KEY}",
            "-d", body,
            url,
        ], capture_output=True, text=True, timeout=130)
        
        if result.returncode != 0:
            return f"[LLM_ERROR] curl exit {result.returncode}: {result.stderr[:500]}"
        
        data = json.loads(result.stdout)
        return data["choices"][0]["message"]["content"]
    except json.JSONDecodeError as e:
        return f"[LLM_ERROR] JSON parse failed: {e}\nRaw: {result.stdout[:500] if 'result' in dir() else 'N/A'}"
    except Exception as e:
        return f"[LLM_ERROR] {e}"

# ─── State helpers ────────────────────────────────────────────

def load_project() -> dict:
    return json.loads((AISC_DIR / "project.json").read_text())

def save_project(proj: dict) -> None:
    (AISC_DIR / "project.json").write_text(json.dumps(proj, indent=2, ensure_ascii=False))

def load_stage(stage_id: str) -> dict:
    for d in STAGES_DIR.iterdir():
        if d.is_dir():
            s = json.loads((d / "stage.json").read_text())
            if s["id"] == stage_id:
                return s
    raise FileNotFoundError(f"Stage {stage_id} not found")

def save_stage(stage: dict) -> None:
    stage_dir = STAGES_DIR / "01-requirement"  # MVP: only one stage
    (stage_dir / "stage.json").write_text(json.dumps(stage, indent=2, ensure_ascii=False))

def save_artifact(stage_id: str, filename: str, content: str, version: int) -> Path:
    stage_dir = next(d for d in STAGES_DIR.iterdir() if d.is_dir() and d.name.startswith("01"))
    artifact_dir = stage_dir / "artifact"
    path = artifact_dir / f"{filename}-v{version}.md"
    path.write_text(content)
    # Also write as current working copy
    (DOCS_DIR / f"{filename}.md").write_text(content)
    return path

def save_meeting(meeting: dict) -> Path:
    stage_dir = next(d for d in MEETINGS_DIR.iterdir() if d.is_dir() and d.name.startswith("01"))
    path = stage_dir / f"meeting-{meeting['id']}.md"
    # YAML frontmatter + markdown body
    frontmatter = "\n".join(f"{k}: {v}" for k, v in meeting["meta"].items())
    content = f"---\n{frontmatter}\n---\n\n{meeting['body']}"
    path.write_text(content)
    return path

def save_memory(agent_id: str, memory_id: str, memory: dict) -> Path:
    path = MEMORY_DIR / agent_id / f"{memory_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(memory, indent=2, ensure_ascii=False))
    return path

# ─── Agent Prompts (from Agent-Prompt设计.md) ─────────────────

PM_AGENT_PROMPT = """你是 Product Manager，一个软件项目的产品经理。
你的工作是：将用户的原始需求转化为清晰、可执行的产品需求文档（PRD）。

# PRD 输出格式

[ARTIFACT]
type: PRD
version: 1
status: draft

---

## 1. 功能目标
<用 2-3 句话描述这个功能要解决什么问题>

## 2. 用户故事
| 角色 | 行为 | 期望结果 |
|------|------|---------|

## 3. 功能点
### 3.1 <功能点名称>
- 描述：
- 输入：
- 输出：
- 前置条件：
- 后置条件：

## 4. 业务规则
- 列出所有业务约束和规则

## 5. 边界条件
| 场景 | 预期行为 |
|------|---------|
| 空数据 | |
| 极限值 | |
| 并发 | |
| 异常输入 | |

## 6. 验收标准
- [ ] 
- [ ] 

## 7. 不做什么（Out of Scope）
- 

## 8. 待澄清问题
[NEEDS CLARIFICATION]
- """

REVIEWER_BASE_PROMPT = """你被邀请参加需求评审会议。

请阅读目标 PRD 的内容，基于你的专业角色，提交评审意见。

# 评审要求
1. 先完整阅读 PRD
2. 从你的专业视角逐一审查
3. 每个意见标注严重程度：
   - 🔴 blocker：不解决无法继续
   - 🟡 important：应该改
   - 🟢 suggestion：建议改，仅供参考
   - ✅ approve：没有问题

4. 输出格式：

[REVIEW_COMMENT]
## {role} 的评审意见

### 🔴 Blocker
- <具体问题>：<为什么是 blocker，建议怎么改>

### 🟡 Important
- <具体问题>

### 🟢 Suggestion
- <建议>

### ✅ Approved
- <确认没问题的部分>

## 总体评价
- [ ] Approve（没有 blocker，同意冻结）
- [ ] Needs Revision（有 blocker 或 important 问题）
- [ ] Reject（方向完全不对）"""

REVIEWER_ROLES = {
    "tech-lead": """
# 你的角色：Tech Lead
你审查 PRD 时关注：技术可行性、性能要求是否明确、是否有技术风险被忽略。
你不对 UI/UX 做判断，不对产品方向做判断。""",

    "ui-designer": """
# 你的角色：UI Designer
你审查 PRD 时关注：用户交互流程是否完整、各种状态（loading/empty/error/edge）是否覆盖。
你不对后端技术做判断。""",

    "backend": """
# 你的角色：Backend Developer
你审查 PRD 时关注：API 大致形态是否可行、数据量级是否有暗示、是否需要考虑分页/缓存。
你不对 UI 做判断。""",

    "frontend": """
# 你的角色：Frontend Developer
你审查 PRD 时关注：前端交互是否可实现、是否需要实时更新、响应式需求。
你不对后端架构做判断。""",

    "qa": """
# 你的角色：QA Tester
你审查 PRD 时关注：验收标准是否可测试、异常流程是否覆盖、边界条件是否完整。
你不对技术方案做判断。""",
}

MODERATOR_PROMPT = """你是 Project Manager，项目的流程调度者。

你收到了一份 PRD 和多位评审人的意见。你的工作是：

1. 按议题聚类评审意见
2. 标注冲突（不同评审人意见矛盾的地方）
3. 标注 blocker（不解决无法继续的问题）
4. 做出决策

**你必须只输出一个 JSON 对象，不要输出任何其他文字，不要用 markdown 代码块包裹。**

JSON 格式：
{
  "type": "revise",
  "summary": "决策摘要，2-3 句话",
  "action_items": [
    {"description": "具体修改任务 1"},
    {"description": "具体修改任务 2"}
  ],
  // 注意：action_items 中每个元素必须是 {"description": "..."} 对象，不能是纯字符串
  "conflicts": [
    {
      "topic": "议题描述",
      "sides": ["Agent A 观点", "Agent B 观点"],
      "resolution": "裁决结果和理由",
      "escalate_to_user": false
    }
  ],
  "freeze_check": {
    "all_blockers_resolved": false,
    "all_conflicts_resolved": true,
    "ready_for_next_stage": false
  }
}

type 取值：
- "adopt": 基本通过，微小修改即可（等同于 freeze）
- "revise": 需要修改后重审
- "reject": 方向不对，打回重做
- "freeze": 冻结，进入下一阶段"""

# ─── MVP Flow ─────────────────────────────────────────────────

def step1_generate_prd(requirement: str, stage: dict) -> str:
    """Step 1: PM Agent 起草 PRD."""
    print("=" * 60)
    print("STEP 1: PM Agent 起草 PRD v1")
    print("=" * 60)
    user_prompt = f"请根据以下用户需求，输出完整 PRD：\n\n{requirement}"
    prd = call_llm(PM_AGENT_PROMPT, user_prompt)
    path = save_artifact(stage["id"], "prd", prd, 1)
    print(f"✅ PRD v1 已保存到 {path}")
    print(f"\n--- PRD v1 前 500 字 ---\n{prd[:500]}...\n")
    return prd

def step2_create_meeting(stage: dict, round_num: int) -> dict:
    """Step 2: Project Manager 创建评审会议."""
    print("=" * 60)
    print(f"STEP 2: 创建 Requirement Review 会议 (第 {round_num} 轮)")
    print("=" * 60)
    # 独立会议计数器：从已有 meeting_ids + 文件系统推断种子
    if "meeting_counter" not in stage:
        max_existing = 0
        # 1) 从 meeting_ids 推断
        for mid in stage.get("meeting_ids", []):
            try:
                num = int(mid.replace("meeting-", ""))
                max_existing = max(max_existing, num)
            except ValueError:
                pass
        # 2) 从已有会议文件兜底（审计一致性）
        stage_num = "01"  # MVP 只有一个 Stage
        meetings_dir = MEETINGS_DIR / f"{stage_num}-requirement"
        if meetings_dir.is_dir():
            for f in meetings_dir.iterdir():
                if f.name.startswith("meeting-meeting-") and f.suffix == ".md":
                    try:
                        num = int(f.stem.replace("meeting-meeting-", ""))
                        max_existing = max(max_existing, num)
                    except ValueError:
                        pass
        stage["meeting_counter"] = max_existing
    counter = stage["meeting_counter"] + 1
    stage["meeting_counter"] = counter
    meeting_id = f"meeting-{counter:03d}"
    meeting = {
        "id": meeting_id,
        "meta": {
            "id": meeting_id,
            "round": round_num,
            "prd_version": stage["current_version"],
            "type": "requirement_review",
            "stage": "requirement",
            "target_artifact": f".aisc/stages/01-requirement/artifact/prd-v{stage['current_version']}.md",
            "moderator": "project-manager",
            "participants": ", ".join(stage["reviewer_agents"]),
            "status": "in_progress",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "body": "",
        "reviews": [],
    }
    if "meeting_ids" not in stage:
        stage["meeting_ids"] = []
    stage["meeting_ids"].append(meeting_id)
    save_stage(stage)
    print(f"✅ Meeting {meeting_id} 已创建，参与者: {meeting['meta']['participants']}")
    return meeting

def step3_parallel_review(prd: str, stage: dict, meeting: dict) -> list[dict]:
    """Step 3: 并行评审 — 所有 Agent 独立审阅 PRD."""
    print("=" * 60)
    print("STEP 3: 并行评审（各 Agent 独立审阅 PRD）")
    print("=" * 60)
    reviews = []
    for agent_id in stage["reviewer_agents"]:
        role_hint = REVIEWER_ROLES.get(agent_id, "")
        system = REVIEWER_BASE_PROMPT.replace("{role}", f"{agent_id} ({role_hint.split(chr(10))[1].strip('# ')}" if role_hint else agent_id)
        system = f"{system}\n{role_hint}"
        user_prompt = f"请评审以下 PRD：\n\n{prd}"
        
        print(f"  ⏳ {agent_id} 正在审阅...")
        review = call_llm(system, user_prompt)
        reviews.append({"agent_id": agent_id, "content": review})
        print(f"  ✅ {agent_id} 审阅完成")
        
        # 提取评审意见摘要
        for line in review.split("\n"):
            if line.strip().startswith("## 总体评价"):
                break
        print(f"     {review.split('总体评价')[-1][:80].strip() if '总体评价' in review else '(opinion recorded)'}")
    
    meeting["reviews"] = reviews
    return reviews

def step4_consensus(prd: str, reviews: list[dict]) -> dict:
    """Step 4: 汇总裁决 — Project Manager 汇总评审意见做决策."""
    print("=" * 60)
    print("STEP 4: 汇总裁决")
    print("=" * 60)
    
    review_text = "\n\n---\n\n".join(
        f"## {r['agent_id']} 的评审意见\n{r['content']}" for r in reviews
    )
    user_prompt = f"""请根据以下信息做出决策（只输出 JSON）：

## PRD 内容
{prd}

## 评审意见
{review_text}"""
    
    raw = call_llm(MODERATOR_PROMPT, user_prompt)
    decision = _parse_decision_json(raw)
    
    dtype = decision.get("type", "unknown")
    summary = decision.get("summary", "")[:200]
    print(f"✅ 决策: {dtype} — {summary}")
    return decision

def _parse_decision_json(raw: str) -> dict:
    """从 LLM 输出中提取 JSON 决策对象，兼容 markdown 代码块包裹."""
    import re
    
    # 尝试直接解析
    text = raw.strip()
    candidates = [text]
    
    # 尝试提取 ```json ... ``` 代码块
    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if m:
        candidates.insert(0, m.group(1).strip())
    
    # 尝试提取第一个 { 到最后一个 }
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        candidates.insert(0, m.group(0))
    
    for c in candidates:
        try:
            result = json.loads(c)
            # 规范化 type 字段
            if "type" in result:
                result["type"] = result["type"].strip().lower()
            return result
        except (json.JSONDecodeError, ValueError):
            continue
    
    # 全部失败：fallback 到旧版正则解析
    print("⚠️  JSON 解析失败，使用 fallback 正则提取 decision type")
    dtype = "unknown"
    for line in raw.split("\n"):
        if line.strip().startswith("type:") or line.strip().startswith('"type"'):
            dtype = line.split(":")[-1].strip().strip('",').lower()
            break
    return {"type": dtype, "summary": raw[:200], "action_items": [], "conflicts": [], "raw": raw}

def step5_freeze_or_revise(decision: dict, prd: str, stage: dict, meeting: dict) -> str:
    """Step 5: 执行决策 — Freeze 或 Revise."""
    print("=" * 60)
    print("STEP 5: 执行决策")
    print("=" * 60)
    
    dtype = decision.get("type", "unknown")
    meeting_id = meeting["id"]
    summary = decision.get("summary", "")
    
    if dtype in ("adopt", "freeze"):
        stage["status"] = "frozen"
        frozen_path = DOCS_DIR / "prd-frozen.md"
        frozen_path.write_text(prd)
        print(f"✅ PRD 已冻结！({frozen_path})")
        
        meeting["meta"]["status"] = "passed"
        meeting["meta"]["decision"] = dtype
        meeting["body"] = f"## Decision ({dtype})\n\n{summary}\n\n```json\n{json.dumps(decision, indent=2, ensure_ascii=False)}\n```"
        save_meeting(meeting)
        save_stage(stage)
        
        for review in meeting["reviews"]:
            save_memory(review["agent_id"], f"{meeting_id}-review", {
                "type": "decision",
                "title": f"参与需求评审 {meeting_id}",
                "content": review["content"][:2000],
                "relations": [{"type": "based_on", "target_type": "meeting", "target_id": meeting_id}],
                "tags": ["需求评审", "PRD"],
            })
        
        print("✅ 所有记忆已保存。MVP 闭环完成！")
        return "frozen"
    
    elif dtype == "revise":
        action_count = len(decision.get("action_items", []))
        print(f"⚠️  决策: 需要修改 ({action_count} 个行动项)")
        meeting["meta"]["status"] = "needs_revision"
        meeting["meta"]["decision"] = "revise"
        meeting["body"] = f"## Decision (Revise)\n\n{summary}\n\n```json\n{json.dumps(decision, indent=2, ensure_ascii=False)}\n```"
        save_meeting(meeting)
        return "revise"
    
    elif dtype == "reject":
        print(f"❌ 决策: 打回重做 — {summary}")
        meeting["meta"]["status"] = "rejected"
        meeting["body"] = f"## Decision (Reject)\n\n{summary}"
        save_meeting(meeting)
        return "reject"
    
    else:
        print(f"❓ 未知决策类型: {dtype}")
        print(f"完整决策:\n{json.dumps(decision, indent=2, ensure_ascii=False)[:1000]}")
        return "unknown"

def step6_revise_prd(decision: dict, stage: dict) -> str:
    """Step 6: PM Agent 根据评审意见修改 PRD."""
    print("=" * 60)
    print("STEP 6: PM Agent 修改 PRD")
    print("=" * 60)
    
    prev_prd = (DOCS_DIR / "prd.md").read_text()
    new_version = stage["current_version"] + 1
    
    # 用结构化的 action_items 替代原始文本
    action_items = decision.get("action_items", [])
    # 兼容两种格式：[{"description":"..."}] 和 ["..."]
    normalized = []
    for a in action_items:
        if isinstance(a, dict):
            normalized.append(a.get("description", str(a)))
        else:
            normalized.append(str(a))
    action_text = "\n".join(f"{i+1}. {desc}" for i, desc in enumerate(normalized))
    
    revision_system = f"""你是 Product Manager。请根据评审决策修改 PRD。

要求：
1. 针对以下每一条 ActionItem 逐一修改
2. 在 PRD 开头注明本次变更内容（changes 字段）
3. 输出完整 PRD，版本号 {new_version}
4. 不要引入 ActionItem 中没有要求的新内容
5. 如果某个 ActionItem 已经在当前 PRD 中满足，标注"已满足，无需修改"

评审决策: {decision.get('summary', '')}

ActionItem 列表:
{action_text}

输出格式：
[ARTIFACT]
type: PRD
version: {new_version}
status: draft
changes: |
  <本次变更摘要>"""
    
    user_prompt = f"""## 当前 PRD (v{stage['current_version']})
{prev_prd}

请根据上述 ActionItem 逐条修改 PRD，输出完整的 v{new_version}。"""
    
    new_prd = call_llm(revision_system, user_prompt)
    stage["current_version"] = new_version
    path = save_artifact(stage["id"], "prd", new_prd, stage["current_version"])
    save_stage(stage)
    print(f"✅ PRD v{stage['current_version']} 已保存到 {path}")
    return new_prd

# ─── Main ──────────────────────────────────────────────────────

def main():
    if not LLM_API_KEY:
        print("❌ 请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY 环境变量")
        sys.exit(1)

    # 读取用户需求
    req_path = DOCS_DIR / "requirement.md"
    if not req_path.exists():
        print(f"❌ 请先在 {req_path} 写入用户需求")
        print("   示例: echo '做一个 AI 视频平台，用户可以上传视频、浏览视频列表...' > docs/requirement.md")
        sys.exit(1)
    requirement = req_path.read_text()
    print(f"📋 用户需求: {requirement[:200]}...\n")

    # 加载状态
    project = load_project()
    stage = load_stage("stage-requirement")
    
    # 断点续跑：从 current_version 决定起始轮次
    prd_exists = (DOCS_DIR / "prd.md").exists()
    if prd_exists and stage.get("current_version", 1) > 1:
        round_num = stage["current_version"]
        print(f"📋 检测到已有 PRD v{round_num}，从第 {round_num} 轮继续评审\n")
    else:
        round_num = 1
        stage["current_version"] = 1
        save_stage(stage)
    
    MAX_ROUNDS = 5
    
    while round_num <= MAX_ROUNDS:
        print(f"\n{'=' * 60}")
        print(f" 第 {round_num} 轮评审")
        print(f"{'=' * 60}\n")
        
        if round_num == 1 and not prd_exists:
            prd = step1_generate_prd(requirement, stage)
        else:
            prd = (DOCS_DIR / "prd.md").read_text()
            if not prd.strip():
                print("❌ docs/prd.md 为空，无法继续")
                break
        
        meeting = step2_create_meeting(stage, round_num)
        reviews = step3_parallel_review(prd, stage, meeting)
        decision = step4_consensus(prd, reviews)
        result = step5_freeze_or_revise(decision, prd, stage, meeting)
        
        if result == "frozen":
            break
        elif result == "revise":
            if round_num >= MAX_ROUNDS:
                print(f"\n⚠️  已达最大评审轮次 ({MAX_ROUNDS})，需要用户介入决策。")
                break
            step6_revise_prd(decision, stage)
            round_num += 1
        else:
            print(f"\n❌ 无法处理的决策类型，终止。")
            break

    print(f"\n{'=' * 60}")
    print(f" MVP 流程结束。Stage 状态: {stage['status']}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
