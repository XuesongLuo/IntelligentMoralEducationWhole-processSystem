# AI Integration Contract

This project now uses an async exam-analysis flow:

1. The frontend submits the paper to the backend.
2. The backend stores the attempt and answers immediately.
3. The backend sends a JSON payload to the configured AI service webhook.
4. After analysis finishes, the AI service calls back into the backend.
5. The backend saves the analysis result into `assessment_ai_reports` and updates the attempt status.

## Required Backend Config

Set these values in the backend `.env`:

```env
AI_ANALYSIS_WEBHOOK_URL=http://your-ai-service/analyze
AI_CALLBACK_TOKEN=your-shared-secret
BACKEND_PUBLIC_BASE_URL=http://your-backend-host:8000
```

Notes:

- `AI_ANALYSIS_WEBHOOK_URL` is the endpoint the backend calls after a submission.
- `AI_CALLBACK_TOKEN` is the shared secret used by the AI service when calling back.
- `BACKEND_PUBLIC_BASE_URL` must be reachable by the AI service.

## Outbound Payload Sent To AI

When a paper is submitted, the backend sends a `POST` request to `AI_ANALYSIS_WEBHOOK_URL`.

Example payload:

```json
{
  "attempt_id": 123,
  "paper": {
    "id": 8,
    "title": "科研诚信考核试卷一",
    "paper_type": "integrity"
  },
  "user": {
    "id": 15,
    "role": "student",
    "real_name": "张三",
    "student_no": "20260001",
    "teacher_no": null
  },
  "submitted_at": "2026-04-08 22:10:00",
  "duration_seconds": 1260,
  "answers": [
    {
      "question_id": 101,
      "question_type": "single",
      "title": "发现实验数据与预期不一致时，最合适的做法是：",
      "answer": ["C"],
      "score": 30
    },
    {
      "question_id": 102,
      "question_type": "essay",
      "title": "请简要说明你会如何处理导师要求“优化”实验结果的情况。",
      "answer": "我会保留原始数据并与导师沟通规范要求。",
      "score": 0
    }
  ],
  "callback": {
    "url": "http://your-backend-host:8000/api/v1/exam/ai/callback",
    "method": "POST",
    "header_name": "X-AI-Callback-Token",
    "token": "your-shared-secret"
  }
}
```

## AI Callback API

The AI service should `POST` to:

```text
/api/v1/exam/ai/callback
```

Required header:

```text
X-AI-Callback-Token: <AI_CALLBACK_TOKEN>
```

Recommended callback body:

```json
{
  "attempt_id": 123,
  "status": "completed",
  "score_research_integrity": 92,
  "score_communication_anxiety": 81,
  "score_career_identity": 85,
  "score_humanistic_care": 79,
  "score_comprehensive_balance": 86,
  "total_score": 84.6,
  "summary": "科研规范意识较强，建议继续提升复杂情境下的表达与决策稳定性。"
}
```

Accepted fields:

- `attempt_id`: required, matches the backend attempt record.
- `status`: recommended values are `processing`, `completed`, or `failed`.
- `score_research_integrity`
- `score_communication_anxiety`
- `score_career_identity`
- `score_humanistic_care`
- `score_comprehensive_balance`
- `total_score`
- `summary`
- `comprehensive_advice`

Notes:

- If both `summary` and `comprehensive_advice` are present, the backend prefers `summary`.
- The backend stores the full callback body in `assessment_ai_reports.raw_response_json`.

## Status Behavior

- Submission complete, AI not finished yet:
  - `assessment_attempts.status = ai_processing`
  - `assessment_ai_reports.status = processing`
- AI callback success:
  - `assessment_attempts.status = completed`
  - `assessment_ai_reports.status = completed`
- AI dispatch failed:
  - `assessment_attempts.status = submitted`
  - `assessment_ai_reports.status = failed`

## UI Behavior

- The results list shows "模型分析中" while `assessment_ai_reports.status != completed`.
- The detail dialog shows the current `summary` if present, even before scores are available.

## Current Limits

- The backend currently prevents duplicate submit requests for the same active Redis exam session.
- Heartbeat time is accumulated in Redis every 30 seconds and written to `duration_seconds` when submitting.
- Objective auto-scoring is intentionally not used for the final AI result path; AI is the source of truth for the analysis panel.
