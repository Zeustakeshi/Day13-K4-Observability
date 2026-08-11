# Prompt `day13-chat` — nội dung v1/v2 và kết quả CP2

**Trạng thái: đã tạo trên Langfuse và chạy xong toàn bộ checklist CP2 (qua Langfuse public API, host
`https://us.cloud.langfuse.com`, project gắn với key trong `.env`).**

Nguồn tham chiếu: [docs/PROMPT_VERSIONING.md](../../docs/PROMPT_VERSIONING.md), [app/prompt_management.py](../../app/prompt_management.py), [app/agent.py](../../app/agent.py).

## Ghi chú kỹ thuật trước khi tạo prompt trên Langfuse

- Tên prompt bắt buộc: `day13-chat` (khớp `LANGFUSE_PROMPT_NAME` trong `.env`).
- Type: **Text prompt** (không phải Chat prompt) — `prompt_management.py` gọi
  `client.get_prompt(name, label=label, type="text", ...)`.
- Bắt buộc giữ đúng 3 biến, đúng cú pháp `{{...}}` (Langfuse dùng mustache), đúng chính tả vì
  `managed_prompt.compile(feature=..., docs=..., message=...)` truyền theo tên các biến này:
  - `{{feature}}`
  - `{{docs}}`
  - `{{message}}`
- App không dùng nội dung câu trả lời để chấm điểm "prompt nào hay hơn" — `FakeLLM.generate()`
  (`app/mock_llm.py`) trả về một câu trả lời cố định bất kể nội dung prompt. Vì vậy v2 chỉ cần
  khác biệt **format/độ dài của hướng dẫn trả lời**, không cần tối ưu chất lượng thật.
- Sau khi tạo version, gắn label đúng theo checklist:
  - v1 → gắn cả `baseline` và `production`.
  - v2 → gắn `candidate` (sau đó ở bước 5 của tài liệu, chuyển `production` sang v2, rồi rollback lại v1).

## Version 1 — label `baseline` + `production`

```text
Bạn là trợ lý hỗ trợ nội bộ cho tính năng {{feature}} của sản phẩm.

Ngữ cảnh tài liệu liên quan:
{{docs}}

Câu hỏi của người dùng:
{{message}}

Hãy trả lời ngắn gọn, dựa trên ngữ cảnh tài liệu ở trên. Nếu tài liệu không đủ thông tin,
hãy nói rõ là chưa đủ dữ liệu thay vì suy đoán.
```

## Version 2 — label `candidate`

Thay đổi nhỏ so với v1: yêu cầu trả lời theo **định dạng gạch đầu dòng, tối đa 3 ý**, thay vì
đoạn văn tự do. Đây là một thay đổi format/độ dài đủ để phân biệt hai version trên trace, không
nhằm mục đích "prompt hay hơn".

```text
Bạn là trợ lý hỗ trợ nội bộ cho tính năng {{feature}} của sản phẩm.

Ngữ cảnh tài liệu liên quan:
{{docs}}

Câu hỏi của người dùng:
{{message}}

Hãy trả lời bằng tối đa 3 gạch đầu dòng, mỗi ý không quá 20 từ, dựa trên ngữ cảnh tài liệu ở trên.
Nếu tài liệu không đủ thông tin, hãy nói rõ là chưa đủ dữ liệu thay vì suy đoán.
```

## Kết quả thực tế (CP2, 2026-08-11)

Được tạo qua Langfuse public API (Basic Auth bằng `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`),
không qua UI, vì vậy **nhóm vẫn cần tự mở Langfuse UI để chụp ảnh evidence** (danh sách version,
before/after đổi label) — phần dưới chỉ là bằng chứng dạng dữ liệu/API, không thay thế được ảnh
chụp màn hình mà rubric yêu cầu.

Lưu ý số thứ tự version: lần tạo v1 đầu tiên bị lỗi encoding (mất dấu tiếng Việt) nên bị bỏ,
Langfuse tự tăng số version — **version 2** mới là nội dung v1/baseline đúng, **version 3** là
nội dung v2/candidate đúng. Nội dung hiển thị trong hai khối text ở trên (mục "Version 1"/"Version 2")
là nội dung đã dùng, không đổi.

| Bước | Hành động | Kết quả xác nhận |
|---|---|---|
| 1 | Tạo version 2, gắn label `baseline` + `production` | `POST /api/public/v2/prompts` → 201 |
| 2 | Tạo version 3, gắn label `candidate` | `POST /api/public/v2/prompts` → 201 |
| 3 | Set `.env LANGFUSE_PROMPT_LABEL=baseline`, restart API, gửi 1 request | trace `cffb6afe0632cf8870fa5a3d293d85f4`, session `cp2-baseline-session` |
| 3 | Set `.env LANGFUSE_PROMPT_LABEL=candidate`, restart API, gửi 1 request | trace `ef0db4dacb210ab24d93acd91f4ab6d2`, session `cp2-candidate-session` |
| 4 | Kiểm tra metadata 2 trace qua `GET /api/public/traces` | baseline → `prompt_label=baseline, prompt_version=2, prompt_source=langfuse`; candidate → `prompt_label=candidate, prompt_version=3, prompt_source=langfuse` |
| 5 | `PATCH /versions/3 {newLabels:["candidate","production"]}`, set `.env` lại `production`, restart, gửi 1 request | trace session `cp2-production-v3-session` → `prompt_label=production, prompt_version=3` |
| 6 | `PATCH /versions/2 {newLabels:["baseline","production"]}` (rollback), restart, gửi 1 request | trace session `cp2-rollback-session` → `prompt_label=production, prompt_version=2` |
| — | Chạy `scripts/load_test.py` (10 request, feature `qa`/`summary` xen kẽ) ngay sau rollback để có ≥10 trace | 10 trace session `s01`–`s10`, timestamp `08:43:50–51Z`, tất cả `prompt_label=production, prompt_version=2` — xác nhận rollback áp dụng cho toàn bộ traffic, không chỉ 1 request thử |

Xác nhận cuối cùng qua `GET /api/public/v2/prompts/day13-chat?label=...`:

```text
production -> version 2, labels [baseline, production]
baseline   -> version 2, labels [baseline, production]
candidate  -> version 3, labels [candidate, latest]
```

`.env` hiện tại đã trả về đúng trạng thái ban đầu: `LANGFUSE_PROMPT_LABEL=production`.

## Ảnh evidence (đã chụp và lưu trong `submission/evidence/`)

| File | Nội dung |
|---|---|
| [prompt_v3_candidate_production.jpg](prompt_v3_candidate_production.jpg) | Version #3 mang label `production` + `latest` + `candidate` — trạng thái **trước** rollback (production đang trỏ candidate) |
| [prompt_v2_baseline_production.jpg](prompt_v2_baseline_production.jpg) | Version #2 mang label `production` + `baseline` — trạng thái **sau** rollback |
| [trace_baseline_v2.jpg](trace_baseline_v2.jpg) | Trace `cffb6afe0632cf8870fa5a3d293d85f4` (session `cp2-baseline-session`), chip `Prompt: day13-chat - v2` |
| [trace_candidate_v3.jpg](trace_candidate_v3.jpg) | Trace `ef0db4dacb210ab24d93acd91f4ab6d2` (session `cp2-candidate-session`), chip `Prompt: day13-chat - v3` |

Hai ảnh version (#3 và #2) đồng thời đóng vai trò "ảnh danh sách 2 prompt version" (panel bên trái
liệt kê `#1/#2/#3`) và "ảnh trước/sau đổi label production" theo yêu cầu evidence của
`docs/PROMPT_VERSIONING.md`. Hai ảnh trace đóng vai trò "hai trace ID chứng minh hai version/label
khác nhau". Evidence đã đầy đủ theo checklist — không cần chụp thêm.
