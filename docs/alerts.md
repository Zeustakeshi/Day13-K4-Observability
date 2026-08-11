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
  1. C mở dashboard panel latency, ghi lại time window P95/P99 vượt ngưỡng, giá trị đỉnh và ảnh panel có SLO line 3000 ms.
  2. A chọn một request chậm trong đúng time window đó, mở trace tương ứng, lưu trace ID và span chiếm nhiều thời gian nhất.
  3. A/C tìm log `response_sent` có cùng correlation ID, đối chiếu `latency_ms`, `feature`, `model`, `session_id` và metadata prompt để bàn giao cho D.
- Mitigation tạm thời: Nếu trace cho thấy prompt/version mới làm tăng token hoặc latency, rollback prompt label về baseline; nếu do tải lab tăng đột biến, giảm concurrency/load test; nếu do incident practice/challenge đang bật, tắt theo lệnh disable sau khi đã chụp đủ evidence. C xác nhận lại P95 quay xuống dưới SLO trên dashboard, A bàn giao trace ID và log line cho D viết incident report.
- Owner: A - Dashboard/SLO/Alert; phối hợp D - Incident/Report tại CP3.

## Alert 2

- Tên: Chat error rate above SLO
- Severity: P1 nếu người dùng nhận lỗi 5xx hàng loạt; P2 nếu error rate chỉ vượt nhẹ.
- SLI/SLO liên quan: Error rate của request `/chat`; SLO nháp: error rate <= 2% trong cửa sổ 60 phút.
- Điều kiện và thời gian duy trì: Error rate > 2% trong 5 phút hoặc có ít nhất 3 request thất bại liên tiếp trong load test.
- Ảnh hưởng tới người dùng: Người dùng không nhận được câu trả lời, API trả lỗi thay vì phản hồi chat.
- Ba bước kiểm tra đầu tiên:
  1. C mở dashboard panel errors, ghi lại time window error rate vượt 2%, số request failed và `error_type` nổi bật.
  2. A mở trace của một request lỗi trong cùng time window, lưu trace ID, span thất bại và thông tin service/generation liên quan.
  3. A/C tìm log `request_failed` có cùng correlation ID, ghi lại `error_type`, `message_preview` đã redact và metadata request để D chứng minh root cause.
- Mitigation tạm thời: Nếu lỗi đến từ dependency/tool trong lab, bật fallback hoặc tắt incident đang gây lỗi sau khi đã lưu evidence; nếu lỗi do prompt/config mới, rollback thay đổi gần nhất; nếu lỗi lan rộng, tạm giảm traffic load test để bảo vệ demo. C theo dõi error rate trở về <= 2%, A cập nhật runbook/evidence cho D.
- Owner: A - Dashboard/SLO/Alert; phối hợp D - Incident/Report tại CP3.

## Alert 3

- Tên: Token or cost spike impacting chat sessions
- Severity: P2; nâng lên P1 nếu cost spike đi kèm latency cao hoặc làm gián đoạn demo.
- SLI/SLO liên quan: Tổng `cost_usd` và tổng `tokens_in`/`tokens_out` của `/chat`; SLO nháp: total cost <= 2.5 USD và token total <= 50000 trong cửa sổ 60 phút.
- Điều kiện và thời gian duy trì: Tổng cost > 2.5 USD trong 60 phút hoặc tổng token > 50000 trong 60 phút; cảnh báo sớm khi tốc độ tăng token/cost cao bất thường trong 10 phút.
- Ảnh hưởng tới người dùng: Câu trả lời có thể chậm hơn, quota/cost tăng nhanh, demo có nguy cơ hết ngân sách hoặc bị throttle.
- Ba bước kiểm tra đầu tiên:
  1. C mở dashboard panel cost và tokens, ghi lại thời điểm bắt đầu tăng, tổng cost/token hiện tại và ảnh threshold 2.5 USD/50000 tokens.
  2. A chọn request/session đóng góp token hoặc cost cao nhất, mở trace và lưu trace ID cùng metadata `prompt_name`, `prompt_label`, `prompt_version`.
  3. A/C tìm log `response_sent` cùng correlation ID, đối chiếu `tokens_in`, `tokens_out`, `cost_usd`, `quality_score` và kiểm tra preview đã redact PII trước khi chuyển cho D.
- Mitigation tạm thời: Rollback prompt label về baseline nếu candidate làm phình token; giới hạn input quá dài hoặc giảm batch load test; nếu cost spike là incident đang bật, tắt sau khi đã lưu metric/trace/log evidence. C xác nhận token/cost không tăng tiếp trên dashboard, A bàn giao trace ID/log line để D chứng minh Metrics -> Traces -> Logs.
- Owner: A - Dashboard/SLO/Alert; phối hợp D - Incident/Report tại CP3.
