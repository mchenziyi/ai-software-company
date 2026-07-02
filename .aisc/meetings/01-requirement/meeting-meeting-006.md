---
id: meeting-006
round: 5
prd_version: 5
type: requirement_review
stage: requirement
target_artifact: .aisc/stages/01-requirement/artifact/prd-v5.md
moderator: project-manager
participants: tech-lead, ui-designer, backend, frontend, qa
status: needs_revision
created_at: 2026-07-02T09:43:55Z
decision: revise
---

## Decision (Revise)

PRD整体技术方向合理，但存在多个 blocker（CSRF 与刷新接口循环依赖、验收标准缺失、WebSocket 错误码未定义）以及若干重要议题需要明确。建议在下一版中补充 CSRF 完整方案（采用 Double Submit Cookie 并豁免刷新接口）、详细验收标准表格、WebSocket 错误码定义，并解决收藏并发、搜索预期结果等模糊点。

```json
{
  "type": "revise",
  "summary": "PRD整体技术方向合理，但存在多个 blocker（CSRF 与刷新接口循环依赖、验收标准缺失、WebSocket 错误码未定义）以及若干重要议题需要明确。建议在下一版中补充 CSRF 完整方案（采用 Double Submit Cookie 并豁免刷新接口）、详细验收标准表格、WebSocket 错误码定义，并解决收藏并发、搜索预期结果等模糊点。",
  "action_items": [
    {
      "description": "明确 CSRF Token 方案：采用 Double Submit Cookie（服务端生成随机 Token 通过 Set-Cookie 存入 HttpOnly Cookie，前端在非幂等请求头携带 X-CSRF-Token，后端比对）；明确 /api/auth/refresh 端点豁免 CSRF 校验（基于 HttpOnly Refresh Token Cookie 和 SameSite=Strict 防护）。"
    },
    {
      "description": "定义 Refresh Token 过期时间（如 7 天）及滑动过期策略，补充 Cookie 安全属性（Secure、SameSite=Strict、Path=/api/auth）。"
    },
    {
      "description": "补充分片上传完成合并指示：增加 POST /api/upload/{taskId}/complete 接口，服务端验证分片完整性后触发合并。"
    },
    {
      "description": "定义热度排序计算模型和权重因子（如播放量、收藏数、时间衰减函数），并明确计算频率为可配置参数。"
    },
    {
      "description": "明确搜索安全校验的预期响应：SQL 注入/超长输入返回 400 及错误信息，纯空格返回 200 空列表，所有非法输入需具体断言。"
    },
    {
      "description": "完善验收标准：将所有 4.8~4.30+ 条目展开为表格（编号、前置条件、操作步骤、输入数据、预期结果、备注），包括边界条件（page 负数/小数、size 0/101/非数字等）。"
    },
    {
      "description": "定义 WebSocket 鉴权失败错误码（如 WebSocket Close Code 4001）及前重重试策略（鉴权失败后尝试刷新 Token 重连，若 Refresh Token 过期则降级为轮询）。"
    },
    {
      "description": "明确收藏失败处理策略：推荐乐观更新 + 失败回滚，并指定 Toast 文案。"
    },
    {
      "description": "补充前端 CSRF Token 获取的防重入机制（单例模式缓存），并说明 401 刷新后是否需要重新获取。"
    },
    {
      "description": "补充后端文件校验（MIME 类型、大小），并写入验收标准负面测试。"
    },
    {
      "description": "定义注册成功后的跳转行为（与登录一致），补充收藏按钮 loading/离线状态、上传进度条、空搜索 UI、未登录点击收藏弹窗等 UX 细节。"
    },
    {
      "description": "收敛并发收藏测试步骤：使用 JMeter 同步定时器，验证数据库记录数=1 且 favorited=1。"
    },
    {
      "description": "补充分页响应结构字段（items、total、page、size、isLastPage），默认 pageSize=20。"
    },
    {
      "description": "明确排序切换时同排序重复点击的行为（不重置/升降序切换），并补充滚动到顶部。"
    }
  ],
  "conflicts": [
    {
      "topic": "收藏 toggle 的并发安全性实现",
      "sides": [
        "tech-lead 认为 INSERT ... ON DUPLICATE KEY UPDATE 存在并发风险，建议改为 UPDATE + 行锁或 INSERT IGNORE；backend 认为该语句在 InnoDB 下已原子化，可接受。"
      ],
      "resolution": "采纳 tech-lead 的建议，改用 UPDATE favorites SET favorited = NOT favorited ... 配合 INSERT IGNORE 或 SELECT ... FOR UPDATE，并在 PRD 中明确行锁保障。",
      "escalate_to_user": false
    },
    {
      "topic": "CSRF Token 实现方案与刷新接口的循环依赖",
      "sides": [
        "tech-lead 建议采用 Double Submit Cookie 方案；frontend 指出若刷新接口也要求 CSRF Token 将导致死循环。"
      ],
      "resolution": "采用 Double Submit Cookie 方案，并明确 /api/auth/refresh 端点豁免 CSRF 校验，仅依赖 HttpOnly Refresh Token Cookie 的 SameSite=Strict 属性防护。",
      "escalate_to_user": false
    },
    {
      "topic": "收藏失败处理策略应选哪种",
      "sides": [
        "PRD 列出了两种策略（响应后更新回滚 / 乐观更新+回滚），ui-designer 和 frontend 均要求明确一种。"
      ],
      "resolution": "推荐采用乐观更新 + 失败回滚，配合 Toast 提示，以提升用户体验。",
      "escalate_to_user": false
    }
  ],
  "freeze_check": {
    "all_blockers_resolved": false,
    "all_conflicts_resolved": false,
    "ready_for_next_stage": false
  }
}
```