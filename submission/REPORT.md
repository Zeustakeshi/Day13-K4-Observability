# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction: [evidence/redacted_log_samples.png](evidence/redacted_log_samples.png)
- Evidence trace waterfall: [evidence/trace_baseline_v2.jpg](evidence/trace_baseline_v2.jpg), [evidence/trace_candidate_v3.jpg](evidence/trace_candidate_v3.jpg)
- Giải thích một span đáng chú ý: span `run` (generation) trong trace `cffb6afe0632cf8870fa5a3d293d85f4`
  — latency 1.10s, cost $0.00264, gắn với prompt `day13-chat - v2` qua link Prompt trong trace detail.

## 4. Prompt versioning

- Prompt name: `day13-chat` (type `text`, giữ 3 biến `{{feature}}`, `{{docs}}`, `{{message}}`).
- Version/label baseline: version 2, label `baseline` (+ `production` sau khi rollback).
- Version/label candidate: version 3, label `candidate` (từng được gắn thêm `production` tạm thời).
- Trace ID của mỗi version:
  - `baseline` (v2): `cffb6afe0632cf8870fa5a3d293d85f4`
  - `candidate` (v3): `ef0db4dacb210ab24d93acd91f4ab6d2`
  - `production` trỏ v3 (sau khi đổi label): `174fd07377ff...` (session `cp2-production-v3-session`)
  - `production` sau rollback về v2: `e55d596f91b5...` (session `cp2-rollback-session`)
- Bằng chứng đổi label hoặc rollback: xác nhận qua Langfuse API — trước khi đổi, `production -> v2`;
  sau `PATCH /api/public/v2/prompts/day13-chat/versions/3 {newLabels:["candidate","production"]}`,
  `production -> v3`; sau rollback `PATCH .../versions/2 {newLabels:["baseline","production"]}`,
  `production -> v2` trở lại. 10 trace chạy `load_test.py` ngay sau rollback (session `s01`–`s10`,
  timestamp `08:43:50–51Z`) đều ghi `prompt_label=production, prompt_version=2`, xác nhận rollback
  có hiệu lực trên toàn bộ traffic thật, không chỉ 1 request thử. Chi tiết đầy đủ và nội dung
  prompt trong [evidence/prompt_versions.md](evidence/prompt_versions.md).
- Ảnh evidence:
  - [evidence/prompt_v3_candidate_production.jpg](evidence/prompt_v3_candidate_production.jpg) — version #3 mang label `production` (trước rollback)
  - [evidence/prompt_v2_baseline_production.jpg](evidence/prompt_v2_baseline_production.jpg) — version #2 mang label `production` (sau rollback)
  - [evidence/trace_baseline_v2.jpg](evidence/trace_baseline_v2.jpg) — trace baseline, chip `Prompt: day13-chat - v2`
  - [evidence/trace_candidate_v3.jpg](evidence/trace_candidate_v3.jpg) — trace candidate, chip `Prompt: day13-chat - v3`

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
