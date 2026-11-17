"""
2019 年日记评论按周合并脚本（草稿，补录完再启用）
触发：用户说「2019 补完了」

核心逻辑：
1. 拉 issue 21 全量评论 → 按周分组（ISO 周历）
2. 保留每周第一天的评论 ID（覆盖成完整周内容，永久链接仅六天失效）
3. 合并格式：每天段落用 ## MM-DD 日期分隔，正文原封不动搬入
4. 删除剩余六天的评论
5. 重建 issue 21 正文索引表（周次 + 日期区间 + 直达链接）
6. 全程安全链：
   - 先备份全量评论成本地 JSON（issue21-backup-YYYYMMDD.json）
   - 合并后逐周 diff 校验内容零丢失
   - 图片引用全搬，覆盖先于删除（避免附件断链）
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
