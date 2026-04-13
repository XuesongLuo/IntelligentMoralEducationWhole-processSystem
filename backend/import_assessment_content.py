from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.models.assessment_paper import AssessmentPaper
from app.models.assessment_paper_question import AssessmentPaperQuestion
from app.models.assessment_question import AssessmentQuestion
from app.models.auth_user import AuthUser


WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
DEFAULT_DOC_ROOT = Path(r"D:\CoWorkProjects\需求分析文档")
SURVEY_1_NAME = "第一次问卷采集表.docx"
SURVEY_2_NAME = "第二次问卷采集表.docx"
EXAM_NAME = "科研考试和思政考试试卷.docx"
SUPPORTED_PAPER_TYPES = {"survey", "integrity"}


@dataclass
class ImportedQuestion:
    question_type: str
    title: str
    options_json: list[dict[str, str]] | None = None
    answer_json: Any = None
    score: int = 0


@dataclass
class ImportedPaper:
    paper_type: str
    title: str
    version_no: int
    duration_seconds: int
    source_path: Path
    questions: list[ImportedQuestion] = field(default_factory=list)


@dataclass
class ImportSummaryItem:
    paper_type: str
    title: str
    version_no: int
    question_count: int
    status: str
    source_name: str


def read_docx_lines(path: Path) -> list[str]:
    with ZipFile(path) as archive:
        xml_text = archive.read("word/document.xml")

    root = ET.fromstring(xml_text)
    lines: list[str] = []
    for paragraph in root.findall(".//w:p", WORD_NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", WORD_NS)).strip()
        if text:
            lines.append(normalize_line(text))
    return lines


def normalize_line(line: str) -> str:
    return (
        line.replace("\u3000", " ")
        .replace("", "")
        .replace("•", "")
        .replace("–", "-")
        .replace("“", '"')
        .replace("”", '"')
        .strip()
    )


def build_option_items(options: list[str]) -> list[dict[str, str]]:
    return [{"label": chr(ord("A") + index), "text": option} for index, option in enumerate(options)]


def is_survey_heading(line: str) -> bool:
    if re.match(r"^[一二三四五六七八九十]+、", line):
        return True
    return line in {
        "高中",
        "本科",
        '硕士研究生（无则填 "无"）',
        '博士研究生（无则填 "无"）',
    }


def extract_checkbox_options(text: str) -> tuple[str, list[str]]:
    if "□" not in text:
        return text.strip(), []

    first_box = text.find("□")
    prompt = text[:first_box].strip().rstrip("：:")
    option_part = text[first_box:]
    options = [item.strip() for item in re.findall(r"□\s*([^□]+?)(?=\s*□|$)", option_part) if item.strip()]
    return prompt, options


def parse_survey_question(line: str) -> ImportedQuestion | None:
    if not line or is_survey_heading(line):
        return None

    numbered = re.sub(r"^\d+[.．、]\s*", "", line)
    prompt, options = extract_checkbox_options(numbered)

    if options:
        question_type = "multiple" if any(keyword in prompt for keyword in ("可多选", "限选", "多选")) else "single"
        return ImportedQuestion(
            question_type=question_type,
            title=prompt or numbered,
            options_json=build_option_items(options),
        )

    if "____" in numbered or "________________" in numbered:
        return ImportedQuestion(question_type="fill_blank", title=numbered.rstrip("：:"))

    return None


def parse_survey_doc(path: Path, title: str, version_no: int) -> ImportedPaper:
    paper = ImportedPaper(
        paper_type="survey",
        title=title,
        version_no=version_no,
        duration_seconds=5400,
        source_path=path,
    )
    for line in read_docx_lines(path):
        question = parse_survey_question(line)
        if question:
            paper.questions.append(question)
    return paper


def parse_exam_heading(line: str) -> tuple[str, int] | None:
    patterns = [
        (r"^科研诚信试卷（第\s*(\d+)\s*套）$", "integrity"),
        (r"^科研诚信\s*第\s*(\d+)\s*套$", "integrity"),
        (r"^思政试卷（第\s*(\d+)\s*套）$", "ideology"),
        (r"^思政\s*第\s*(\d+)\s*套$", "ideology"),
    ]
    for pattern, paper_type in patterns:
        match = re.match(pattern, line)
        if match:
            return paper_type, int(match.group(1))
    return None


def split_exam_options(line: str) -> list[dict[str, str]]:
    matches = list(re.finditer(r"([A-D])\.\s*", line))
    if not matches:
        return []

    options: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(line)
        options.append({"label": match.group(1), "text": line[start:end].strip()})
    return options


def parse_exam_doc(path: Path) -> list[ImportedPaper]:
    papers: list[ImportedPaper] = []
    current_paper: ImportedPaper | None = None
    current_question_type: str | None = None
    current_question: ImportedQuestion | None = None

    def flush_question() -> None:
        nonlocal current_question
        if current_paper and current_question:
            current_paper.questions.append(current_question)
        current_question = None

    for raw_line in read_docx_lines(path):
        line = raw_line.strip()
        if not line:
            continue

        heading = parse_exam_heading(line)
        if heading:
            flush_question()
            paper_type, version_no = heading
            title_prefix = "科研诚信试卷" if paper_type == "integrity" else "思政试卷"
            current_paper = ImportedPaper(
                paper_type=paper_type,
                title=f"{title_prefix}（第{version_no}套）",
                version_no=version_no,
                duration_seconds=7200,
                source_path=path,
            )
            papers.append(current_paper)
            current_question_type = None
            continue

        if line.startswith(("一、单选题", "单选题")):
            flush_question()
            current_question_type = "single"
            continue
        if line.startswith(("二、多选题", "多选题")):
            flush_question()
            current_question_type = "multiple"
            continue
        if line.startswith(("三、判断题", "判断题")):
            flush_question()
            current_question_type = "boolean"
            continue

        if not current_paper or not current_question_type:
            continue

        if current_question_type in {"single", "multiple"} and re.search(r"\bA\.\s*", line):
            if current_question:
                current_question.options_json = split_exam_options(line)
            continue

        question_match = re.match(r"^(?:\d+[.．、]\s*)?(.+?)[（(]\s*[）)]\s*$", line)
        if question_match:
            flush_question()
            title = question_match.group(1).strip()
            current_question = ImportedQuestion(
                question_type=current_question_type,
                title=title,
                options_json=build_option_items(["对", "错"]) if current_question_type == "boolean" else None,
            )
            continue

        if current_question:
            current_question.title = f"{current_question.title} {line}".strip()

    flush_question()
    return papers


def build_default_papers(doc_root: Path) -> list[ImportedPaper]:
    papers = [
        parse_survey_doc(doc_root / SURVEY_1_NAME, "德育画像构建问卷一", 1),
        parse_survey_doc(doc_root / SURVEY_2_NAME, "德育画像构建问卷二", 2),
    ]
    papers.extend(parse_exam_doc(doc_root / EXAM_NAME))
    return papers


def get_import_owner_id(db: Session) -> int | None:
    teacher = (
        db.query(AuthUser)
        .filter(AuthUser.role == "teacher")
        .order_by(AuthUser.id.asc())
        .first()
    )
    return teacher.id if teacher else None


def upsert_paper(
    db: Session,
    *,
    paper_type: str,
    title: str,
    version_no: int,
    duration_seconds: int,
    created_by_user_id: int | None,
) -> AssessmentPaper:
    paper = (
        db.query(AssessmentPaper)
        .filter(
            AssessmentPaper.paper_type == paper_type,
            AssessmentPaper.version_no == version_no,
        )
        .first()
    )

    if paper:
        paper.title = title
        paper.duration_seconds = duration_seconds
        paper.is_active = True
        paper.created_by_user_id = created_by_user_id
        return paper

    paper = AssessmentPaper(
        paper_type=paper_type,
        title=title,
        version_no=version_no,
        duration_seconds=duration_seconds,
        is_active=True,
        created_by_user_id=created_by_user_id,
    )
    db.add(paper)
    db.flush()
    return paper


def upsert_question(
    db: Session,
    *,
    paper_type: str,
    question_type: str,
    title: str,
    options_json: list[dict[str, str]] | None,
    answer_json: Any,
    score: int,
    created_by_user_id: int | None,
) -> AssessmentQuestion:
    question = (
        db.query(AssessmentQuestion)
        .filter(
            AssessmentQuestion.paper_type == paper_type,
            AssessmentQuestion.question_type == question_type,
            AssessmentQuestion.title == title,
        )
        .first()
    )

    if question:
        question.options_json = options_json
        question.answer_json = answer_json
        question.score = score
        question.created_by_user_id = created_by_user_id
        return question

    question = AssessmentQuestion(
        paper_type=paper_type,
        question_type=question_type,
        title=title,
        options_json=options_json,
        answer_json=answer_json,
        score=score,
        created_by_user_id=created_by_user_id,
    )
    db.add(question)
    db.flush()
    return question


def relink_paper_questions(db: Session, paper: AssessmentPaper, questions: list[AssessmentQuestion]) -> None:
    db.query(AssessmentPaperQuestion).filter(AssessmentPaperQuestion.paper_id == paper.id).delete()
    db.flush()

    for index, question in enumerate(questions, start=1):
        db.add(
            AssessmentPaperQuestion(
                paper_id=paper.id,
                question_id=question.id,
                sort_order=index,
            )
        )
    db.flush()


def import_papers(
    db: Session,
    papers: list[ImportedPaper],
    *,
    created_by_user_id: int | None,
) -> list[ImportSummaryItem]:
    summary: list[ImportSummaryItem] = []

    for paper_data in papers:
        if paper_data.paper_type not in SUPPORTED_PAPER_TYPES:
            summary.append(
                ImportSummaryItem(
                    paper_type=paper_data.paper_type,
                    title=paper_data.title,
                    version_no=paper_data.version_no,
                    question_count=len(paper_data.questions),
                    status="skipped",
                    source_name=paper_data.source_path.name,
                )
            )
            continue

        paper = upsert_paper(
            db,
            paper_type=paper_data.paper_type,
            title=paper_data.title,
            version_no=paper_data.version_no,
            duration_seconds=paper_data.duration_seconds,
            created_by_user_id=created_by_user_id,
        )
        questions = [
            upsert_question(
                db,
                paper_type=paper_data.paper_type,
                question_type=question.question_type,
                title=question.title,
                options_json=question.options_json,
                answer_json=question.answer_json,
                score=question.score,
                created_by_user_id=created_by_user_id,
            )
            for question in paper_data.questions
        ]
        relink_paper_questions(db, paper, questions)
        summary.append(
            ImportSummaryItem(
                paper_type=paper_data.paper_type,
                title=paper.title,
                version_no=paper.version_no,
                question_count=len(questions),
                status="imported",
                source_name=paper_data.source_path.name,
            )
        )

    return summary


def print_summary(summary: list[ImportSummaryItem]) -> None:
    print("\nImport summary:")
    total_imported = 0
    for item in summary:
        label = item.paper_type
        print(
            f"- [{item.status}] {label} v{item.version_no} {item.title} | "
            f"{item.question_count} questions | source={item.source_name}"
        )
        if item.status == "imported":
            total_imported += 1

    print(f"\nImported papers: {total_imported}")
    if summary:
        grouped: dict[str, int] = {}
        for item in summary:
            if item.status != "imported":
                continue
            grouped[item.paper_type] = grouped.get(item.paper_type, 0) + item.question_count
        for paper_type, count in grouped.items():
            print(f"- {paper_type}: {count} questions")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import questionnaire and exam content from DOCX files.")
    parser.add_argument(
        "--doc-root",
        type=Path,
        default=DEFAULT_DOC_ROOT,
        help="Folder containing the provided DOCX source files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse content and print summary without writing to database.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    Base.metadata.create_all(bind=engine)

    papers = build_default_papers(args.doc_root)
    db = SessionLocal()
    try:
        owner_id = get_import_owner_id(db)
        summary = import_papers(db, papers, created_by_user_id=owner_id)
        if args.dry_run:
            db.rollback()
            print("Dry run complete.")
        else:
            db.commit()
            print("Import complete.")
        print_summary(summary)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
