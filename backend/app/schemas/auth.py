from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    account: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class UserInfo(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    student_no: str | None = None
    teacher_no: str | None = None
    phone: str | None = None
    email: str | None = None


class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user_info: UserInfo