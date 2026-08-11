import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)

# Register Arial font for Vietnamese support
font_dir = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont('Arial', f'{font_dir}/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', f'{font_dir}/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', f'{font_dir}/ariali.ttf'))
pdfmetrics.registerFont(TTFont('Arial-BoldItalic', f'{font_dir}/arialbi.ttf'))

# Define custom styles
styles = getSampleStyleSheet()

# Title Style
title_style = ParagraphStyle(
    'DocTitle',
    fontName='Arial-Bold',
    fontSize=22,
    leading=26,
    textColor=colors.HexColor('#0f172a'),
    alignment=1, # Center
    spaceAfter=15
)

sub_title_style = ParagraphStyle(
    'DocSubTitle',
    fontName='Arial-Italic',
    fontSize=11,
    leading=15,
    textColor=colors.HexColor('#475569'),
    alignment=1,
    spaceAfter=20
)

# Heading Styles
h1_style = ParagraphStyle(
    'H1',
    fontName='Arial-Bold',
    fontSize=15,
    leading=19,
    textColor=colors.HexColor('#1e293b'),
    spaceBefore=14,
    spaceAfter=8,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'H2',
    fontName='Arial-Bold',
    fontSize=12,
    leading=16,
    textColor=colors.HexColor('#2563eb'),
    spaceBefore=10,
    spaceAfter=6,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'Body',
    fontName='Arial',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#334155'),
    spaceAfter=6
)

bullet_style = ParagraphStyle(
    'Bullet',
    fontName='Arial',
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor('#334155'),
    spaceAfter=4,
    leftIndent=15
)

callout_style = ParagraphStyle(
    'Callout',
    fontName='Arial-Italic',
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor('#0f766e'),
    spaceBefore=4,
    spaceAfter=4
)

def build_pdf(filename="Huong_Dan_AI_Observability_Dashboard.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []

    # Banner Header
    story.append(Paragraph("🚀 TỔNG QUAN DỰ ÁN & HƯỚNG DẪN DASHBOARD OBSERVABILITY", title_style))
    story.append(Paragraph("Dự án: Day 13 · AI Observability Lab | Hệ Thống Giám Sát API Chat AI / RAG", sub_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceAfter=15))

    # Section 1: Project Overview
    story.append(Paragraph("📌 1. DỰ ÁN NÀY LÀM VỀ CÁI GÌ? (PROJECT OVERVIEW)", h1_style))
    story.append(Paragraph(
        "Dự án này giải quyết một bài toán thực tế rất lớn trong phát triển phần mềm AI: <b>Làm sao để giám sát và kiểm soát một ứng dụng Chat AI / RAG hoạt động ổn định, chính xác và tiết kiệm chi phí?</b>",
        body_style
    ))
    story.append(Paragraph(
        "Bình thường, khi gọi API AI, chúng ta không biết vì sao câu trả lời bị chậm, vì sao mô hình bị lỗi, hoặc chi phí gọi API tăng vọt bất ngờ. Dự án này xây dựng một <b>Hệ thống Quan sát Toàn diện (Observability System)</b> dựa trên tam giác 3 trụ cột:",
        body_style
    ))

    overview_data = [
        [
            Paragraph("<b>Trụ cột</b>", body_style),
            Paragraph("<b>Công cụ sử dụng</b>", body_style),
            Paragraph("<b>Vai trò & Ý nghĩa</b>", body_style)
        ],
        [
            Paragraph("📊 <b>1. Metrics</b>", body_style),
            Paragraph("Grafana + Loki + Promtail", body_style),
            Paragraph("Theo dõi con số tổng quan thời gian thực (Độ trễ, Tỷ lệ lỗi, Chi phí, Tokens).", body_style)
        ],
        [
            Paragraph("🔍 <b>2. Traces</b>", body_style),
            Paragraph("Langfuse Cloud", body_style),
            Paragraph("Soi chi tiết từng công đoạn xử lý bên trong (RAG search tốn bao lâu, LLM tốn bao lâu).", body_style)
        ],
        [
            Paragraph("📝 <b>3. Logs</b>", body_style),
            Paragraph("Structlog + JSON Lines", body_style),
            Paragraph("Ghi nhật ký hệ thống chi tiết (Chứa correlation_id và tự động che giấu thông tin PII).", body_style)
        ]
    ]

    t_overview = Table(overview_data, colWidths=[1.3*inch, 1.8*inch, 3.8*inch])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 15))

    # Section 2: Dashboard Overview & Panels
    story.append(Paragraph("📊 2. CHI TIẾT 6 BIỂU ĐỒ TRÊN GRAFANA DASHBOARD", h1_style))
    story.append(Paragraph(
        "Dashboard Grafana là nơi trung tâm giúp Kỹ sư / Giám sát viên nhìn vào là biết ngay tình trạng sức khỏe của ứng dụng AI. Dưới đây là giải thích chi tiết ý nghĩa của từng biểu đồ:",
        body_style
    ))

    # Panel 1
    story.append(Paragraph("⚡ 1. Latency Percentiles (Độ Trễ Phần Trăm P50 / P95 / P99)", h2_style))
    story.append(Paragraph("• <b>Nói về cái gì?</b>: Đo lường thời gian mà ứng dụng AI phản hồi lại câu hỏi của người dùng (tính bằng mili-giây ms).", bullet_style))
    story.append(Paragraph("• <b>Giải thích chỉ số</b>: <b>P50</b> = 50% người dùng nhận câu trả lời dưới mốc này. <b>P95</b> = 95% người dùng nhận câu trả lời dưới mốc này. <b>P99</b> = 1% người dùng gặp độ trễ lớn nhất.", bullet_style))
    story.append(Paragraph("• <b>Đơn vị & Ngưỡng SLO</b>: Đơn vị <b>ms</b> | Ngưỡng giới hạn SLO: <b>P95 ≤ 3000 ms</b>.", bullet_style))
    story.append(Paragraph("• <b>Cách đọc cảnh báo</b>: Khi đường P95 vọt quá 3000ms ➡️ Ứng dụng bị nghẽn/chậm nặng, hệ thống sẽ phát cảnh báo đỏ!", callout_style))
    story.append(Spacer(1, 6))

    # Panel 2
    story.append(Paragraph("📈 2. Request Traffic Wave (Lưu Lượng Truy Cập API)", h2_style))
    story.append(Paragraph("• <b>Nói về cái gì?</b>: Đo tổng số lượt người dùng gửi câu hỏi đến API theo từng phút.", bullet_style))
    story.append(Paragraph("• <b>Đơn vị & Ngưỡng SLO</b>: Đơn vị <b>req/min</b> (Số request / phút) | Ngưỡng mục tiêu: <b>≥ 1 req/min</b>.", bullet_style))
    story.append(Paragraph("• <b>Ý nghĩa thực tế</b>: Giúp theo dõi tải của hệ thống. Nếu traffic bằng 0 trong thời gian dài ➡️ API có thể bị sập kết nối.", callout_style))
    story.append(Spacer(1, 6))

    # Panel 3
    story.append(Paragraph("🚨 3. Error Rate and Breakdown (Tỷ Lệ Lỗi & Phân Loại Sự Cố)", h2_style))
    story.append(Paragraph("• <b>Nói về cái gì?</b>: Thống kê phần trăm các yêu cầu bị thất bại (lỗi 5xx) và phân loại nguyên nhân lỗi.", bullet_style))
    story.append(Paragraph("• <b>Đơn vị & Ngưỡng SLO</b>: Đơn vị <b>%</b> | Ngưỡng giới hạn SLO: <b>Error Rate ≤ 2%</b>.", bullet_style))
    story.append(Paragraph("• <b>Phân loại lỗi (Breakdown)</b>: Phân chia chi tiết do <i>TimeoutError</i>, <i>LLMError</i> hay <i>PIIError</i>.", bullet_style))
    story.append(Paragraph("• <b>Ý nghĩa thực tế</b>: Giúp lập tức biết được hệ thống đang bị lỗi gì để sửa ngay lập tức.", callout_style))
    story.append(Spacer(1, 6))

    # Panel 4
    story.append(Paragraph("💰 4. Cost Over Time (Chi Phí Vận Hành Theo Thời Gian)", h2_style))
    story.append(Paragraph("• <b>Nói về cái gì?</b>: Theo dõi tổng số tiền USD đã tiêu tốn cho việc gọi mô hình AI (OpenAI / Claude).", bullet_style))
    story.append(Paragraph("• <b>Đơn vị & Ngưỡng SLO</b>: Đơn vị <b>$ USD</b> | Ngưỡng giới hạn SLO: <b>Total Cost ≤ $2.50 USD</b>.", bullet_style))
    story.append(Paragraph("• <b>Ý nghĩa thực tế</b>: Giúp kiểm soát ngân sách, tránh việc người dùng spams câu hỏi làm bùng nổ chi phí API.", callout_style))
    story.append(Spacer(1, 6))

    # Panel 5
    story.append(Paragraph("🔤 5. Input and Output Tokens (Số Lượng Token Đầu Vào & Đầu Ra)", h2_style))
    story.append(Paragraph("• <b>Nói về cái gì?</b>: Đo lường khối lượng từ/ký tự gửi vào (Tokens In) và mô hình AI sinh ra (Tokens Out).", bullet_style))
    story.append(Paragraph("• <b>Đơn vị & Ngưỡng SLO</b>: Đơn vị <b>tokens</b> | Ngưỡng giới hạn SLO: <b>Total Tokens ≤ 50,000</b>.", bullet_style))
    story.append(Paragraph("• <b>Trực quan hóa</b>: Hiển thị dạng 2 cột đứng song song (Cột Xanh = Tokens In, Cột Vàng = Tokens Out).", bullet_style))
    story.append(Paragraph("• <b>Ý nghĩa thực tế</b>: Token càng lớn thì chi phí càng cao và thời gian phản hồi càng lâu.", callout_style))
    story.append(Spacer(1, 6))

    # Panel 6
    story.append(Paragraph("⭐ 6. Quality Proxy Gauge (Đồng Hồ Đo Chất Lượng Phản Hồi)", h2_style))
    story.append(Paragraph("• <b>Nói về cái gì?</b>: Đánh giá độ chính xác, hữu ích và mức độ liên quan của câu trả lời AI.", bullet_style))
    story.append(Paragraph("• <b>Đơn vị & Ngưỡng SLO</b>: Thang điểm <b>0.0 – 1.0</b> | Ngưỡng mục tiêu: <b>Mean Score ≥ 0.75</b>.", bullet_style))
    story.append(Paragraph("• <b>Trực quan hóa</b>: Đồng hồ Arc Gauge màu sắc (Đỏ < 0.5, Vàng < 0.75, Xanh ≥ 0.75).", bullet_style))
    story.append(Paragraph("• <b>Ý nghĩa thực tế</b>: Đảm bảo AI không trả lời lan man hoặc sai lệch kiến thức nghiệp vụ.", callout_style))
    story.append(Spacer(1, 15))

    # Section 3: Incident Investigation Workflow
    story.append(Paragraph("🔍 3. QUY TRÌNH ĐIỀU TRA SỰ CỐ (METRICS ➔ TRACES ➔ LOGS)", h1_style))
    story.append(Paragraph(
        "Khi hệ thống gặp sự cố, quy trình điều tra 3 bước tiêu chuẩn của dự án diễn ra như sau:",
        body_style
    ))

    workflow_data = [
        [
            Paragraph("<b>Bước 1: Metrics (Grafana)</b>", body_style),
            Paragraph("Phát hiện triệu chứng tổng quan. Ví dụ: Thẻ P95 Latency bật <b>ĐỎ RỰC</b> > 3000ms.", body_style)
        ],
        [
            Paragraph("<b>Bước 2: Traces (Langfuse)</b>", body_style),
            Paragraph("Khoanh vùng vị trí nghẽn. Soi cây Waterfall xem Span nào (`mock_rag` hay `LLM`) tốn nhiều thời gian nhất.", body_style)
        ],
        [
            Paragraph("<b>Bước 3: Logs (logs.jsonl)</b>", body_style),
            Paragraph("Lấy bằng chứng trực tiếp. Tra theo `correlation_id` để đọc log chi tiết và tìm lỗi gốc rễ (Root cause).", body_style)
        ]
    ]

    t_workflow = Table(workflow_data, colWidths=[2.2*inch, 4.7*inch])
    t_workflow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#eff6ff')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bfdbfe')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_workflow)
    story.append(Spacer(1, 20))

    # Footer note
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=10))
    story.append(Paragraph("Tài liệu hướng dẫn được tạo tự động cho dự án Day 13 AI Observability Lab.", sub_title_style))

    doc.build(story)
    print(f"✅ Document successfully created: {filename}")

if __name__ == "__main__":
    build_pdf()
