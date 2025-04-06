"""
アプリケーション全体で使用する定数
"""

# 記憶タイプ
MEMORY_TYPE_DAILY_RAW = "daily_raw"
MEMORY_TYPE_DAILY_SUMMARY = "daily_summary"
MEMORY_TYPE_LEVEL_10 = "level_10"
MEMORY_TYPE_LEVEL_100 = "level_100"
MEMORY_TYPE_LEVEL_1000 = "level_1000"
MEMORY_TYPE_LEVEL_ARCHIVE = "level_archive"

# 記憶階層構造
MEMORY_HIERARCHY = {
    MEMORY_TYPE_DAILY_RAW: 0,
    MEMORY_TYPE_DAILY_SUMMARY: 1,
    MEMORY_TYPE_LEVEL_10: 2,
    MEMORY_TYPE_LEVEL_100: 3,
    MEMORY_TYPE_LEVEL_1000: 4,
    MEMORY_TYPE_LEVEL_ARCHIVE: 5,
}

# 記憶タイプの日数対応
MEMORY_TYPE_DAYS = {
    MEMORY_TYPE_DAILY_RAW: 1,
    MEMORY_TYPE_DAILY_SUMMARY: 1,
    MEMORY_TYPE_LEVEL_10: 10,
    MEMORY_TYPE_LEVEL_100: 100,
    MEMORY_TYPE_LEVEL_1000: 1000,
    MEMORY_TYPE_LEVEL_ARCHIVE: float("inf"),
}

# セッションタイプ
SESSION_TYPE_CONVERSATION = "conversation"  # 会話セッション
SESSION_TYPE_SLEEP = "sleep"  # 睡眠セッション

# セッションの状態
SESSION_STATUS_ACTIVE = "active"  # アクティブなセッション
SESSION_STATUS_COMPLETED = "completed"  # 完了したセッション
SESSION_STATUS_ERROR = "error"  # エラーが発生したセッション

# セッションのプロパティ名
SESSION_PROP_CURRENT_DAY = "current_day"  # 現在の日
SESSION_PROP_DEVICE_ID = "device_id"  # デバイスID
