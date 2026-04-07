from pydantic import BaseModel

from app.schemas.common import ResponseModel


class StudentHomeProgressItem(BaseModel):
    id: int
    name: str
    progress: float
    leftCount: int


class StudentHomeScoreDimension(BaseModel):
    key: str
    name: str
    best: float
    worst: float


class StudentHomeData(BaseModel):
    studentId: str
    studentName: str
    phone: str | None = None

    levelValue: int = 0
    aiUsageDuration: str = "00:00:00"
    simulationCompletion: float = 0.0

    studyProgressList: list[StudentHomeProgressItem] = []
    scoreDimensions: list[StudentHomeScoreDimension] = []


class StudentHomeResponseModel(ResponseModel):
    data: StudentHomeData