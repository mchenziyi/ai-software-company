---
id: meeting-003
round: 2
prd_version: 2
type: requirement_review
stage: requirement
target_artifact: .aisc/stages/01-requirement/artifact/prd-v2.md
moderator: project-manager
participants: tech-lead, ui-designer, backend, frontend, qa
status: needs_revision
created_at: 2026-07-02T09:30:08Z
decision: revise
---

## Decision (Revise)

PRD整体方向合理，但存在搜索触发方式矛盾、CSRF实现不可行、上传方案冲突、收藏并发竞态、状态展示缺失等多个 blocker 和细节冲突，需修订关键设计后重新评审。

```json
{
  "type": "revise",
  "summary": "PRD整体方向合理，但存在搜索触发方式矛盾、CSRF实现不可行、上传方案冲突、收藏并发竞态、状态展示缺失等多个 blocker 和细节冲突，需修订关键设计后重新评审。",
  "action_items": [
    {
      "description": "统一搜索触发机制：明确为提交式触发（点击按钮或回车），移除前端300ms防抖；或改用实时搜索带防抖，但需更新PRD描述"
    },
    {
      "description": "修正CSRF Token传递方式：改为非HttpOnly的Cookie（如XSRF-TOKEN）前端读取后通过X-CSRF-Token请求头传递，或采用SameSite属性方案"
    },
    {
      "description": "统一视频上传方案：明确采用云存储直传，补充临时凭证获取接口（如POST /api/upload/{taskId}/signPart）和分片上传URL签名逻辑，删除经应用服务器代理的描述"
    },
    {
      "description": "补充上传状态查询接口（GET /api/upload/{taskId}/status）及状态变更推送机制（WebSocket/轮询），并增加‘上传失败’状态"
    },
    {
      "description": "定义收藏Toggle的原子操作实现：建议使用INSERT ... ON DUPLICATE KEY UPDATE或REPLACE INTO，确保并发下幂等"
    },
    {
      "description": "明确未登录收藏交互：统一为点击后弹窗提示‘请先登录’，点击‘去登录’跳转至/login?redirect=当前页，登录后不回自动收藏（除非额外协商）"
    },
    {
      "description": "补充续传机制：定义GET /api/upload/{taskId}/parts接口查询已上传分片，并说明凭证刷新和重试策略"
    },
    {
      "description": "补充后台转码容错、热度排序算法、响应式布局、空搜索行为、服务端标签校验、处理超时上限等缺失细节"
    },
    {
      "description": "更新验收标准：覆盖续传测试、并发收藏、服务端标签校验、分页超限搜索场景、全局加载重试按钮等"
    }
  ],
  "conflicts": [
    {
      "topic": "搜索触发方式：提交式触发 vs 防抖",
      "sides": [
        "PRD要求‘提交式触发（点击搜索按钮或按回车）’，同时要求‘前端300ms防抖’（防抖通常用于实时搜索）",
        "ui-designer 和 frontend 均指出两者矛盾，需统一"
      ],
      "resolution": "建议采用纯提交式触发，移除输入框防抖；若需实时搜索则改用防抖并更新PRD。请产品经理决策。",
      "escalate_to_user": true
    },
    {
      "topic": "CSRF Token传递方式",
      "sides": [
        "PRD要求‘通过HTTP-only Cookie传递CSRF token’",
        "backend 和 frontend 指出HTTP-only Cookie无法被JS读取，前端无法携带"
      ],
      "resolution": "改为非HttpOnly的Cookie（如XSRF-TOKEN），前端读取后通过X-CSRF-Token请求头传递，或使用SameSite属性。",
      "escalate_to_user": false
    },
    {
      "topic": "收藏Toggle并发竞态处理方案",
      "sides": [
        "tech-lead建议捕获唯一键冲突后删除再返回false",
        "backend建议使用原子操作INSERT ... ON DUPLICATE KEY UPDATE"
      ],
      "resolution": "采用backend的原子操作方案，更简洁可靠；同时确保接口返回当前收藏状态。",
      "escalate_to_user": false
    },
    {
      "topic": "未登录收藏交互不明确",
      "sides": [
        "业务规则4.1要求‘收藏按钮需显示‘请先登录’提示’",
        "验收标准7中写‘弹出提示或跳转登录页’（二选一）"
      ],
      "resolution": "统一为弹窗提示‘请先登录’，点击‘去登录’跳转至登录页并携带redirect参数；登录后不回自动收藏，除非PRD明确。",
      "escalate_to_user": true
    }
  ],
  "freeze_check": {
    "all_blockers_resolved": false,
    "all_conflicts_resolved": false,
    "ready_for_next_stage": false
  }
}
```