---
id: meeting-004
round: 3
prd_version: 3
type: requirement_review
stage: requirement
target_artifact: .aisc/stages/01-requirement/artifact/prd-v3.md
moderator: project-manager
participants: tech-lead, ui-designer, backend, frontend, qa
status: needs_revision
created_at: 2026-07-02T09:34:32Z
decision: revise
---

## Decision (Revise)

{
  "type": "revise",
  "summary": "多位评审人提出了 blocker 和重要问题。需要修改的包括：CSRF Token 传递方案（改为 HttpOnly Cookie + 响应头）、收藏接口实现（改为 toggle 接口）、分片上传并发控制、WebSocket 细节、响应式布局断点、UI 状态（上传处理中、空搜索、分页超限反馈等）、验收标准格式化、搜索安全校验等

```json
{
  "type": "revise",
  "summary": "{\n  \"type\": \"revise\",\n  \"summary\": \"多位评审人提出了 blocker 和重要问题。需要修改的包括：CSRF Token 传递方案（改为 HttpOnly Cookie + 响应头）、收藏接口实现（改为 toggle 接口）、分片上传并发控制、WebSocket 细节、响应式布局断点、UI 状态（上传处理中、空搜索、分页超限反馈等）、验收标准格式化、搜索安全校验等",
  "action_items": [],
  "conflicts": [],
  "raw": "{\n  \"type\": \"revise\",\n  \"summary\": \"多位评审人提出了 blocker 和重要问题。需要修改的包括：CSRF Token 传递方案（改为 HttpOnly Cookie + 响应头）、收藏接口实现（改为 toggle 接口）、分片上传并发控制、WebSocket 细节、响应式布局断点、UI 状态（上传处理中、空搜索、分页超限反馈等）、验收标准格式化、搜索安全校验等。修改后需重新评审。\",\n  \"action_items\": [\n    {\"description\": \"将 CSRF Token 传递方式改为 HttpOnly Cookie + 服务端响应头（如 X-CSRF-Token）或 meta 标签，前端读取后放入 X-CSRF-Token 请求头，保留 SameSite=Strict 和自定义请求头验证。\"},\n    {\"description\": \"修改收藏 Toggle 实现：改为 POST /api/favorites/toggle 接口，后端原子判断存在则删除、不存在则插入；或拆分为 POST/DELETE 并配合行锁或唯一索引保证幂等。\"},\n    {\"description\": \"明确分片上传前端并发控制：建议并发数为 3~5，后端并行处理分片签名请求并防重放。\"},\n    {\"description\": \"增加 Refresh Token 轮转机制：每次刷新 Access Token 时同时返回新 Refresh Token，废弃旧 Token。\"},\n    {\"description\": \"明确热度排序算法：采用指数衰减公式 (score = 播放量 + 3*收藏数 * e^(-λ*(now-created_at))，λ=0.01/天)，并说明计算方式（定时任务更新字段，查询时直接排序）。\"},\n    {\"description\": \"补充 WebSocket 连接细节：端点、认证方式（URL 参数携带 JWT）、连接时机（进入上传页面时）、重连策略、降级到轮询的触发条件（如重试 3 次失败后改用 5 秒轮询）。\"},\n    {\"description\": \"明确上传总时长 2 小时为软限制：前端提示用户可续期，或根据文件大小动态计算超时。\"},\n    {\"description\": \"延长分片签名有效期至 30 分钟以减少过期重试。\"},\n    {\"description\": \"定义响应式布局断点：手机 <768px，平板 768-1024px，桌面 >1024px；并描述关键组件布局变化。\"},\n    {\"description\": \"补充上传处理中阶段的 UI：显示动态进度条（如“转码中 60%”）或“正在处理，请稍候”提示，且禁用删除/编辑操作。\"},\n    {\"description\": \"修改未登录收藏弹窗文案为“请先登录，登录后请再次点击收藏按钮”，避免用户预期自动收藏。\"},\n    {\"description\": \"补充空搜索行为 UI：清空搜索框并点击搜索时重置为第一页全部视频，显示加载动画；无视频时展示空状态提示。\"},\n    {\"description\": \"分页超限时 UI：自动跳转至最后一页并显示 toast“已跳转至最后一页”。\"},\n    {\"description\": \"实现收藏 Toggle 乐观更新：本地立即反转图标，请求失败时恢复原状并显示错误 toast。\"},\n    {\"description\": \"补充上传失败 UI：显示失败原因（如格式不支持、网络中断），并提供“重新上传”和“删除”按钮。\"},\n    {\"description\": \"考虑搜索分页性能优化：建议游标分页或缓存 count 结果；若保持 offset 分页，对 count 查询做短期缓存。\"},\n    {\"description\": \"补充 CSRF Token 生成与校验细节：随机字符串+过期时间+用户标识签名"
}
```