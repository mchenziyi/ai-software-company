---
id: meeting-001
round: 1
prd_version: 1
type: requirement_review
stage: requirement
target_artifact: .aisc/stages/01-requirement/artifact/prd-v1.md
moderator: project-manager
participants: tech-lead, ui-designer, backend, frontend, qa
status: needs_revision
created_at: 2026-07-02T11:28:47Z
decision: revise
---

## Decision (Revise)

PRD 整体方向正确，但存在多个阻塞性问题，包括个人上传管理功能缺失、大文件上传方式未明确、视频状态流转不完整，以及封面图来源和收藏反馈机制等重要议题。需要在进入 API 设计前修正以上问题和澄清歧义。

```json
{
  "type": "revise",
  "summary": "PRD 整体方向正确，但存在多个阻塞性问题，包括个人上传管理功能缺失、大文件上传方式未明确、视频状态流转不完整，以及封面图来源和收藏反馈机制等重要议题。需要在进入 API 设计前修正以上问题和澄清歧义。",
  "action_items": [
    {
      "description": "增加“我的上传”页面或接口，让用户能查看自己上传的所有视频（包含处理中状态），并明确上传后状态对上传者的可见性。"
    },
    {
      "description": "明确大文件上传方式：支持分片上传或预签名 URL，或将文件大小上限降低至 512MB。"
    },
    {
      "description": "明确定义视频状态机：上传后 → pending → available，统一 status 枚举（如 pending、available、rejected），并说明处理中视频对普通用户不可见。"
    },
    {
      "description": "明确视频封面图来源：用户上传自定义封面、使用默认占位图，或将自动截取第一帧纳入本版本范围（需调整 Out of Scope）。"
    },
    {
      "description": "移除或替换播放量字段：若无可播放场景，改为点击量或显示“暂无”。"
    },
    {
      "description": "补充搜索功能的具体规则：排序方式（按上传时间降序或相关度）、是否区分大小写、关键词长度限制、触发方式（回车/点击按钮）。"
    },
    {
      "description": "明确收藏/取消收藏的反馈机制：采用乐观更新还是悲观更新，网络失败时如何回滚 UI 并给出错误提示。"
    },
    {
      "description": "明确分页接口参数：允许客户端通过 size 参数自定义每页条数，或保持固定 20 条并文档化。"
    },
    {
      "description": "补充 XSS 防御策略：后端在输出时对所有用户文本字段（标题、描述、标签）进行 HTML 转义，搜索时保留原始输入。"
    },
    {
      "description": "统一空数据提示处理：后端返回空列表，前端根据场景显示对应文案（如“暂无视频”、“您还没有收藏视频”）。"
    }
  ],
  "conflicts": [],
  "freeze_check": {
    "all_blockers_resolved": false,
    "all_conflicts_resolved": true,
    "ready_for_next_stage": false
  }
}
```