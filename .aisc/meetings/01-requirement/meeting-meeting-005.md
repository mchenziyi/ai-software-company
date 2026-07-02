---
id: meeting-005
round: 4
prd_version: 4
type: requirement_review
stage: requirement
target_artifact: .aisc/stages/01-requirement/artifact/prd-v4.md
moderator: project-manager
participants: tech-lead, ui-designer, backend, frontend, qa
status: needs_revision
created_at: 2026-07-02T09:38:54Z
decision: revise
---

## Decision (Revise)

PRD整体方向正确且细节较完备，但存在前端提出的CSRF Token生命周期未闭环、Token存储刷新策略不明确以及QA提出的验收标准4.7不可测试等blocker。另外多个评审人共同指出搜索安全策略、WebSocket鉴权方式、收藏数据库实现、前端校验缺失等重要问题。需针对这些blocker和重要问题进行修订后重新评审。

```json
{
  "type": "revise",
  "summary": "PRD整体方向正确且细节较完备，但存在前端提出的CSRF Token生命周期未闭环、Token存储刷新策略不明确以及QA提出的验收标准4.7不可测试等blocker。另外多个评审人共同指出搜索安全策略、WebSocket鉴权方式、收藏数据库实现、前端校验缺失等重要问题。需针对这些blocker和重要问题进行修订后重新评审。",
  "action_items": [
    {
      "description": "补充CSRF Token在页面刷新后重新获取的机制（例如增加GET /api/csrf端点，或确保每次响应都返回X-CSRF-Token头）"
    },
    {
      "description": "明确Access Token和Refresh Token的存储方案（建议Refresh Token置于HttpOnly Cookie，Access Token存内存），并实现401拦截器自动刷新Access Token"
    },
    {
      "description": "补充验收标准4.7的操作步骤和预期结果，明确并发收藏测试的具体动作和通过标准"
    },
    {
      "description": "细化分片上传初始凭证定义，明确与signPart凭证的关系、格式和用途，两者生命周期分离"
    },
    {
      "description": "明确WebSocket鉴权方式，采用连接后第一条消息携带JWT进行鉴权（避免URL参数泄露），并定义鉴权失败时服务端主动关闭连接"
    },
    {
      "description": "修改收藏toggle数据库实现，使用favorited字段（0/1）而非deleted，并在(user_id, video_id)上建唯一索引"
    },
    {
      "description": "搜索安全校验改为强制使用参数化查询+字符白名单校验+长度限制（≤100字符），移除黑名单过滤SQL注入关键字的表述"
    },
    {
      "description": "明确热度排序衰减计算实现方式：推荐使用定时任务预计算热力值并缓存，避免实时查询时的性能问题"
    },
    {
      "description": "补充收藏失败状态处理策略：建议采用响应后更新UI并显示错误提示（Toast），或乐观更新+回滚机制"
    },
    {
      "description": "明确上传重试按钮行为：应调用续传接口查询已上传分片，仅补传缺失分片，而非重新init"
    },
    {
      "description": "定义排序切换时的页码重置行为：切换排序后重置page=1并重新请求"
    },
    {
      "description": "增加前端文件选择校验：在客户端立即检查文件格式（mp4/webm/mov）和大小（≤500MB）并给出反馈"
    },
    {
      "description": "分页接口增加每页数量最大值限制（1-100），超出时返回参数错误或截断"
    },
    {
      "description": "明确分片续传时凭证获取策略：建议每个分片每次上传前必须重新获取signPart凭证，避免凭证复用带来的边界问题"
    },
    {
      "description": "搜索输入框增加前端基本校验：长度限制≤100字符、去除首尾空格、禁止提交仅空格字符串"
    },
    {
      "description": "补充大量的验收标准，至少覆盖：视频上传（格式/大小/标题/标签异常、重试/超时/UI状态）、搜索（安全校验/空搜索/分页超限/排序切换）、WebSocket（连接失败/心跳丢失/重连/降级）、Token刷新、未登录用户行为、响应式布局等核心场景的happy path、异常和边界"
    },
    {
      "description": "细化CSRF防护验收标准4.4：补充正向用例（携带合法Token返回200）和至少三种负向测试（不携带、错误Token、篡改），并明确预期结果"
    },
    {
      "description": "增加分页超限验收标准：请求大于总页数的页码，验证响应包含isLastPage:true且数据为最后一页"
    },
    {
      "description": "增加搜索安全校验测试用例：SQL注入、超长、纯空格、HTML标签等输入，验证服务端正确处理"
    }
  ],
  "conflicts": [
    {
      "topic": "WebSocket鉴权方式",
      "sides": [
        "tech-lead建议在首次建立连接后的第一条消息中携带JWT进行鉴权",
        "backend建议通过Authorization头或认证消息进行鉴权（避免URL参数）"
      ],
      "resolution": "采用tech-lead的方案：连接后第一条消息携带JWT，因为浏览器WebSocket不支持自定义HTTP头，且URL参数日志泄露风险高。同时要求服务端鉴权失败时主动关闭并返回错误码。该方案兼顾安全与实现可行性。",
      "escalate_to_user": false
    }
  ],
  "freeze_check": {
    "all_blockers_resolved": false,
    "all_conflicts_resolved": true,
    "ready_for_next_stage": false
  }
}
```