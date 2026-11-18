"""
2019 年日记评论按月合并脚本（草稿，补录完再启用）
触发：用户说「2019 补完了」

分组决策（2026-11-18 定稿）：
- 粒度跟着内容密度走：2016-2018 内容少 → 一天一条不动；
  2019 内容多 → 补录完转按月；2020-2024 素材已是月容器原样；
  2025-2026 按周。
- 2019 内部排版用流水式（非表格）：每日一个小节
  ## MM-DD（周X），正文零改动，* * * 分隔符原样保留。
- 密码趣味标题（√[日]{年^月}周）保留在对应小节内首行（待用户最终确认①）。

核心逻辑：
1. 拉 issue 21 全量评论 → 按自然月分组
2. 保留每月第一条评论的 ID（覆盖成整月流水，其余删除）
   —— 与用户提出的一致：不重发，PATCH 覆盖 + DELETE 剩余
3. 删除该月其余每日评论
4. 重建 issue 21 正文索引表（月份 + 直达链接）
5. 全程安全链：
   - 先备份全量评论成本地 JSON（issue21-backup-YYYYMMDD.json）
   - 合并后逐月 diff 校验内容零丢失
   - 465 张图片引用全搬，覆盖先于删除（避免附件断链）
"""

# TODO: 补录完后实现
TOKEN = "..."
ISSUE_NUMBER = 21
REPO = "volatile-Quartz/Dr_Wunderkammer"

def fetch_comments(): ...
def group_by_week(comments): ...
def merge_week_body(daily_bodies): ...
def patch_keep_comment(comment_id, new_body): ...
def delete_drop_comments(comment_ids): ...
def rebuild_index_table(): ...
