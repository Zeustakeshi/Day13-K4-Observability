# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

Ghi chú cho incident report: theo RUBRIC.md mục A2/B1, mỗi alert khi điều tra phải để lại bằng chứng nối được Metrics -> Traces -> Logs. Báo cáo cần nêu metric/SLO nào vượt ngưỡng, trace ID của request bất thường, và log line có cùng correlation ID để chứng minh root cause, fix action và preventive measure.

## Alert 1

- Tên: Chat response latency SLO burn
- Severity: P1 nếu P95 vượt SLO liên tục; P2 nếu mới vượt ngưỡng cảnh báo.
- SLI/SLO liên quan: P95 latency của request `/chat`; SLO nháp: P95 <= 3000 ms trong cửa sổ 60 phút.
- Điều kiện và thời gian duy trì: P95 latency > 3000 ms trong 5 phút hoặc 3 cửa sổ refresh liên tiếp.
- Ảnh hưởng tới người dùng: Người dùng thấy câu trả lời chậm, dễ retry hoặc bỏ phiên chat.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel latency, ghi lại khoảng thời gian P95/P99 tăng và một request chậm tiêu biểu.
  2. Mở trace của request chậm, lưu trace ID và span chiếm nhiều thời gian nhất.
  3. Tìm log `response_sent` có cùng correlation ID, đối chiếu `latency_ms`, `feature`, `model`, `session_id` và metadata prompt.
- Mitigation tạm thời: Rollback prompt label nếu trace cho thấy phiên bản prompt mới làm tăng token/latency; giảm concurrency hoặc tắt kịch bản incident đang bật; thông báo D dùng trace ID và log line này để viết incident report.
- Owner: A - Dashboard/SLO/Alert; phối hợp D - Incident/Report tại CP3.

## Alert 2

- Tên: Chat error rate above SLO
- Severity: P1 nếu người dùng nhận lỗi 5xx hàng loạt; P2 nếu error rate chỉ vượt nhẹ.
- SLI/SLO liên quan: Error rate của request `/chat`; SLO nháp: error rate <= 2% trong cửa sổ 60 phút.
- Điều kiện và thời gian duy trì: Error rate > 2% trong 5 phút hoặc có ít nhất 3 request thất bại liên tiếp trong load test.
- Ảnh hưởng tới người dùng: Người dùng không nhận được câu trả lời, API trả lỗi thay vì phản hồi chat.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel errors, ghi lại error rate và `error_type` nổi bật.
  2. Mở trace của một request lỗi, lưu trace ID và span thất bại.
  3. Tìm log `request_failed` có cùng correlation ID, ghi lại `error_type`, `message_preview` đã redact và metadata request.
- Mitigation tạm thời: Tắt dependency/kịch bản gây lỗi nếu đang trong lab incident; dùng fallback an toàn cho request mới; giữ lại trace ID và log line để chứng minh root cause trong report.
- Owner: A - Dashboard/SLO/Alert; phối hợp D - Incident/Report tại CP3.

## Alert 3

- Tên: Token or cost spike impacting chat sessions
- Severity: P2; nâng lên P1 nếu cost spike đi kèm latency cao hoặc làm gián đoạn demo.
- SLI/SLO liên quan: Tổng `cost_usd` và tổng `tokens_in`/`tokens_out` của `/chat`; SLO nháp: total cost <= 2.5 USD và token total <= 50000 trong cửa sổ 60 phút.
- Điều kiện và thời gian duy trì: Tổng cost > 2.5 USD trong 60 phút hoặc tổng token > 50000 trong 60 phút; cảnh báo sớm khi tốc độ tăng token/cost cao bất thường trong 10 phút.
- Ảnh hưởng tới người dùng: Câu trả lời có thể chậm hơn, quota/cost tăng nhanh, demo có nguy cơ hết ngân sách hoặc bị throttle.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel cost và tokens, ghi lại thời điểm bắt đầu tăng và request/session đóng góp nhiều nhất.
  2. Mở trace của request có token/cost cao, lưu trace ID và metadata `prompt_name`, `prompt_label`, `prompt_version`.
  3. Tìm log `response_sent` cùng correlation ID, đối chiếu `tokens_in`, `tokens_out`, `cost_usd`, `quality_score` và kiểm tra không có PII trong preview.
- Mitigation tạm thời: Rollback prompt label về bản baseline nếu prompt candidate làm phình token; giới hạn input quá dài hoặc giảm batch load test; bàn giao trace ID/log line cho D để chứng minh Metrics -> Traces -> Logs.
- Owner: A - Dashboard/SLO/Alert; phối hợp D - Incident/Report tại CP3.
