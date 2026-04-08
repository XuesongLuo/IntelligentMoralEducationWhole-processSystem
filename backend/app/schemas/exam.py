from pydantic import BaseModel

from app.schemas.common import ResponseModel


class ExamNoticeData(BaseModel):
    items: list[str] = []


class ExamNoticeResponseModel(ResponseModel):
    data: ExamNoticeData


class ExamInfoData(BaseModel):
    examId: int
    paperName: str


class ExamInfoResponseModel(ResponseModel):
    data: ExamInfoData


class ExamQuestionOption(BaseModel):
    label: str
    value: str | bool | int


class ExamQuestionItem(BaseModel):
    id: int
    type: str
    title: str
    options: list[ExamQuestionOption] = []


class ExamPaperData(BaseModel):
    examId: int
    paperName: str
    durationSeconds: int = 3600
    questions: list[ExamQuestionItem] = []


class ExamPaperResponseModel(ResponseModel):
    data: ExamPaperData


class SubmitExamAnswerItem(BaseModel):
    questionId: int | str
    answer: list | dict | str | bool | int | float | None = None


class SubmitExamRequest(BaseModel):
    examId: int | str
    examType: str
    answers: list[SubmitExamAnswerItem] = []
    forced: bool = False


class SubmitExamResponseData(BaseModel):
    success: bool = True
    resultId: int


class SubmitExamResponseModel(ResponseModel):
    data: SubmitExamResponseData


class ExamHeartbeatRequest(BaseModel):
    examId: int | str
    examType: str


class ExamHeartbeatData(BaseModel):
    activeSeconds: int = 0
    submitted: bool = False


class ExamHeartbeatResponseModel(ResponseModel):
    data: ExamHeartbeatData


class ExamResultListItem(BaseModel):
    id: int
    title: str
    submitTime: str | None = None
    durationMinutes: int = 0
    analysisReady: bool = False


class ExamResultListData(BaseModel):
    records: list[ExamResultListItem] = []
    total: int = 0


class ExamResultListResponseModel(ResponseModel):
    data: ExamResultListData


class ExamResultAnswerItem(BaseModel):
    questionId: int
    questionTitle: str
    answer: list | dict | str | bool | int | float | None = None


class ExamResultAnalysisDimension(BaseModel):
    dimension: str
    score: float
    reason: str


class ExamResultAnalysis(BaseModel):
    dimensions: list[ExamResultAnalysisDimension] = []
    summary: str = ""


class ExamResultDetailData(BaseModel):
    paperName: str = ""
    studentNo: str = ""
    realName: str = ""
    submitTime: str = ""
    durationMinutes: int = 0
    answerList: list[ExamResultAnswerItem] = []
    aiAnalysis: ExamResultAnalysis = ExamResultAnalysis()


class ExamResultDetailResponseModel(ResponseModel):
    data: ExamResultDetailData
