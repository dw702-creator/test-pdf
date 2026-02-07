import streamlit as st
import pdfplumber
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import os
import re

# ---------------- PDF 텍스트 추출 ----------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# ---------------- 텍스트 정리 ----------------
def clean_text(text):
    text = re.sub(r'\n{2,}', '\n\n', text)   # 과도한 줄바꿈 제거
    text = re.sub(r' +', ' ', text)          # 중복 공백 제거
    return text.strip()


# ---------------- 시험지 PDF 생성 ----------------
def create_exam_pdf(text, original_filename):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = {
        "title": ParagraphStyle(
            "title",
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            leading=22,
            bold=True
        ),
        "info": ParagraphStyle(
            "info",
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=20
        ),
        "body": ParagraphStyle(
            "body",
            fontSize=11,
            leading=16,
            spaceAfter=12
        )
    }

    story = []

    # 제목
    story.append(Paragraph("연세영어학원", styles["title"]))
    story.append(Paragraph(
        "반: ________ &nbsp;&nbsp;&nbsp; 이름: ________ &nbsp;&nbsp;&nbsp; 점수: ________ &nbsp;&nbsp;&nbsp; 선생님 확인: ________",
        styles["info"]
    ))
    story.append(Spacer(1, 12))

    # 본문
    for para in text.split("\n\n"):
        story.append(Paragraph(para, styles["body"]))

    doc.build(story)
    buffer.seek(0)

    base = os.path.splitext(original_filename)[0]
    output_name = f"{base}_새시험지.pdf"

    return buffer, output_name


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Blank Test Generator (PDF)", layout="wide")
st.title("📄 Blank Test Generator (PDF)")
st.markdown("PDF 파일의 텍스트를 인식하여 **새로운 시험지 형태의 PDF**로 재생성합니다.")

uploaded_pdf = st.file_uploader("PDF 파일 업로드", type=["pdf"])

if uploaded_pdf:
    if st.button("시험지 PDF 생성"):
        try:
            raw_text = extract_text_from_pdf(uploaded_pdf)
            clean = clean_text(raw_text)

            if not clean:
                st.error("PDF에서 텍스트를 인식하지 못했습니다.")
            else:
                pdf_buffer, filename = create_exam_pdf(clean, uploaded_pdf.name)
                st.success("시험지 PDF가 생성되었습니다!")

                st.download_button(
                    label="⬇️ 시험지 PDF 다운로드",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf"
                )

        except Exception as e:
            st.error("PDF 처리 중 오류가 발생했습니다.")
            st.exception(e)
else:
    st.info("PDF 파일을 업로드하세요.")
