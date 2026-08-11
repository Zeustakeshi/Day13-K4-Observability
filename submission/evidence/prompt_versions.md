# Prompt `day13-chat` — nội dung v1/v2 (soạn trước, dán vào Langfuse khi CP2 mở)

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

## Sau khi tạo xong trên Langfuse — việc cần làm tiếp (theo checklist tài liệu)

1. Tạo v1 trên Langfuse với nội dung ở trên, gắn label `baseline` + `production`.
2. Tạo v2 với nội dung ở trên, gắn label `candidate`.
3. Chạy cùng một input qua API với `LANGFUSE_PROMPT_LABEL=baseline`, sau đó đổi `.env` sang
   `LANGFUSE_PROMPT_LABEL=candidate`, chạy lại (nhớ restart uvicorn sau khi đổi `.env`).
4. Mở hai trace trên Langfuse, kiểm tra metadata `prompt_name`, `prompt_label`, `prompt_version`
   (đã có sẵn trong `update_current_trace`/`update_current_generation` ở `app/agent.py`) và xác
   nhận link tới đúng prompt version.
5. Trên Langfuse, chuyển label `production` sang v2, chạy lại một request, chụp ảnh evidence.
6. Rollback `production` về v1, chụp ảnh evidence trước/sau.
7. Điền hai trace ID + đường dẫn ảnh vào `submission/REPORT.md`, mục "4. Prompt versioning".
