from pydantic import BaseModel, Field

from app.schemas.common import ResponseModel

class LoginRequest(BaseModel):
    account: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class StudentRegisterRequest(BaseModel):
    student_no: str = Field(..., min_length=1, max_length=50)
    real_name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=1, max_length=20)
    password: str = Field(..., min_length=6, max_length=100)
    sms_code: str = Field(..., min_length=4, max_length=10)


class TeacherRegisterRequest(BaseModel):
    teacher_no: str = Field(..., min_length=1, max_length=50)
    real_name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=1, max_length=20)
    password: str = Field(..., min_length=6, max_length=100)
    invite_code: str = Field(..., min_length=1, max_length=100)
    sms_code: str = Field(..., min_length=4, max_length=10)


class SendSmsCodeRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20)


class SendSmsCodeResponse(BaseModel):
    expire_seconds: int
    debug_code: str | None = None


class UserInfo(BaseModel):
    id: int
    real_name: str
    role: str
    student_no: str | None = None
    teacher_no: str | None = None
    phone: str | None = None


class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user_info: UserInfo

class RegisterResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user_info: UserInfo

class SendSmsCodeResponseModel(ResponseModel):
    data: SendSmsCodeResponse

class LoginResponseModel(ResponseModel):
    data: LoginResponse


class RegisterResponseModel(ResponseModel):
    data: RegisterResponse


class UserInfoResponseModel(ResponseModel):
    data: UserInfo