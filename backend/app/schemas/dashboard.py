from pydantic import BaseModel


class LevelInfo(BaseModel):
    level_value: int
    level_display: str
    level_icon_type: str
    ai_usage_seconds: int
    ai_usage_text: str


class LearningCategoryProgress(BaseModel):
    category_code: str
    category_name: str
    completed_count: int
    total_count: int
    completion_rate: float


class DashboardOverview(BaseModel):
    user: dict
    level: LevelInfo
    learning_stats: dict
    score_comparison: dict