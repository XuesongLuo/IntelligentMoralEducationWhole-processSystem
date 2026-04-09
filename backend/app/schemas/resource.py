from pydantic import BaseModel, Field

from app.schemas.common import ResponseModel


class ResourceCategoryProgressItem(BaseModel):
    id: int
    code: str
    name: str
    progress: float = 0.0
    completedCount: int = 0
    totalCount: int = 0
    remainingCount: int = 0


class ResourceCategoryListData(BaseModel):
    items: list[ResourceCategoryProgressItem] = []


class ResourceCategoryListResponseModel(ResponseModel):
    data: ResourceCategoryListData


class ResourceListItem(BaseModel):
    id: int
    title: str
    url: str
    isVisible: bool = True
    completed: bool = False
    clickCount: int = 0
    lastClickedAt: str = ""


class ResourceListData(BaseModel):
    categoryId: int
    categoryCode: str
    categoryName: str
    pageNum: int = 1
    pageSize: int = 10
    total: int = 0
    records: list[ResourceListItem] = []


class ResourceListResponseModel(ResponseModel):
    data: ResourceListData


class ResourceHeartbeatRequest(BaseModel):
    categoryId: int | None = None


class ResourceHeartbeatData(BaseModel):
    activeSeconds: int = 0


class ResourceHeartbeatResponseModel(ResponseModel):
    data: ResourceHeartbeatData


class ResourceVisitData(BaseModel):
    resourceId: int
    clickCount: int = 0
    completed: bool = True
    url: str


class ResourceVisitResponseModel(ResponseModel):
    data: ResourceVisitData


class ResourceUpsertRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=1)


class ResourceVisibilityRequest(BaseModel):
    isVisible: bool


class ResourceItemResponseModel(ResponseModel):
    data: ResourceListItem
