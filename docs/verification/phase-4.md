# Ma trận truy vết Phase 4

Cập nhật 2026-11-22 theo kết quả xác minh trên `main`. Nguồn yêu cầu: Ticket-04 "Phát hành v1.0.0" (30 phút, hạn đẩy tag `phase-4` và công bố GitHub Release `v1.0.0` lúc 3:00), nhóm đọc trên lab board; mã AC theo `docs/plan/phase-4.md` (mã việc trên Sheet lệch 1 so với mã AC).
Cột kết quả ghi trung thực: **đạt**, **đạt một phần**, **chưa đạt**.

## Chạy lại (tại commit gắn tag)

```
PYTHONPATH=tests:. python3 -m unittest discover -s tests        # 388 test, OK (63.084s)
python3 tools/smoke_phase1.py                                    # 27/27 (chạy contract 1.1 sinh từ game.contract.json)
python3 tools/smoke_phase2.py                                    # 15/15 (như trên)
python3 tools/smoke_phase3.py                                    # 13/13, contract 1.3 thật
python3 tools/check_determinism.py                               # OK: gather, quan, day giống từng byte qua 2 lần chạy (seed 1, 600 tick)
python3 tools/check_no_hardcode.py                               # OK
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json # lệnh của bench_cmd
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json        # lệnh của soak_cmd
```
Bench: 32.673 khung (32673 frames), avg 1089.09 FPS, 1% low 517.85 FPS, `load_ms` 96.97. Soak: `days_completed` 10, `crashes` 0, `duration_s` 6.29s. CI Ubuntu: [run 44918861655](https://github.com/luongvh2510/K5-L3B-LAB-Day12-AI-SDLC-NgheAn/actions/runs/44918861655) và [run 44919726436](https://github.com/luongvh2510/K5-L3B-LAB-Day12-AI-SDLC-NgheAn/actions/runs/44919726436); CI Ubuntu push main trên commit gắn tag `phase-4`.

## A. Lõi (mọi nhóm)

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P4-01 Contract `contract_version` "1.3", khai `bench_cmd` và `soak_cmd` ở gốc; gameplay, tuning, kho, JSONL theo v1.2 | Test nạp contract, test chạy chính hai lệnh khai báo như hộp đen; phá thử | `tests/test_p4_contract.py` (7 test), PR #55; phá thử 5 cách, bắt 5/5; dạng lệnh khớp Ticket-04 (runner nối `--seed --duration --out` và `--seed --days --out`, `clarify` P4-02) | Đạt |
| AC-P4-02 Benchmark có render: `bench_cmd --seed 42 --duration 30 --out bench.json`, cảnh lặn (độ tươi, cá bơi, Cá Sấu, Út Sen đứng yên ở bến), 1280×720, làm nóng 3 s rồi đo 30 s, đúng 5 trường | Test cảnh và cấu trúc; chạy lệnh đúng đề; so mốc báo cáo | `chonoi/bench.py`, `tests/test_p4_bench.py` (9 test), PR #52 và #56, [p4-03-bench.md](../proof/phase-4/p4-03-bench.md), [bench.json](../proof/phase-4/bench.json); chạy lại: 32.673 khung (32673 frames), avg 1089.09 FPS, 1% low 517.85 FPS, `load_ms` 96.97; phá thử 5/5 | Đạt một phần: đây là bộ vẽ phần mềm trong bộ nhớ, không phải FPS của trình duyệt (đề chấp nhận); "hiệu ứng mặc định" của đề chưa rõ gồm gì, bộ vẽ chỉ có nền nước gradient; A đã ghi nhận phần D sửa trong hồ sơ và retro của A (PR #60) |
| AC-P4-03 Soak headless: `soak_cmd --seed 7 --days 10 --out soak.json`, 10 Ngày một tiến trình, Ngày 6–10 lặp kế hoạch D1–D5, xuất `days`, `days_completed`, `crashes`, `results[]`, `duration_s` | Test cấu trúc, tất định, kế hoạch lặp, đếm crash; chạy lệnh đúng đề; phá thử | `chonoi/soak.py`, `tests/test_p4_soak.py` (9 test), PR #54, [p4-04-soak.md](../proof/phase-4/p4-04-soak.md), [soak.json](../proof/phase-4/soak.json); chạy lại: `days_completed` 10, `crashes` 0, `duration_s` 6.29s; phá thử 7/7 | Đạt (đúng điều kiện đề: `days_completed = days`, `crashes = 0`); hạn chế: bot chỉ lặn, hái và về bến, không nấu, không phục vụ, không mua ở Shop nên tiền luôn 0 và uy tín về 0 từ Ngày 3 |
| AC-P4-04 Ba cảnh báo dễ nhận biết (thủy quái gần, oxy sắp hết, khách sắp giận) bằng chữ hoặc biểu tượng và chế độ tương phản cao, có test đọc snapshot | Test điều kiện kích hoạt; ảnh chụp trình duyệt | `chonoi/alerts.py`, `tests/test_p4_alerts.py` (14 test), PR #42, [p4-04-alerts.md](../proof/phase-4/p4-04-alerts.md) và ảnh; phá thử bắt hết | Đạt một phần: mốc 25% của oxy và khách là giả định (`clarify` #16). Phím H đã được D bấm thật trên trình duyệt và chụp cùng HUD độ tươi của quán v1.2 thật: [ảnh thường](../proof/phase-4/p4-08-hud-quan-v12.jpg), [ảnh tương phản cao](../proof/phase-4/p4-08-hud-quan-v12-hc.jpg) |
| AC-P4-05 Đóng gói: README chạy từ clone sạch ≤ 3 lệnh (môi trường, điều khiển, test, headless, benchmark), `CHANGELOG.md` theo phase, `CREDITS.md`, `LICENSE`, CI Ubuntu | Test đóng gói; đọc file | `README.md`, `CHANGELOG.md`, `CREDITS.md`, `LICENSE`, `.github/workflows/ci.yml`, `tests/test_packaging.py` (5 test), PR #39 | Đạt một phần: giấy phép MIT là giả định chờ PO (`clarify` #13) |
| AC-P4-06 Thử clone sạch bằng ≤ 3 lệnh, CI Ubuntu làm bằng chứng ngoài Windows, hồi quy P1–P3 | Clone từ GitHub vào thư mục mới, chạy lệnh; CI Ubuntu | [p4-07-clean-clone.md](../proof/phase-4/p4-07-clean-clone.md), PR #57; CI Ubuntu [run 44918861655](https://github.com/luongvh2510/K5-L3B-LAB-Day12-AI-SDLC-NgheAn/actions/runs/44918861655) và [run 44919726436](https://github.com/luongvh2510/K5-L3B-LAB-Day12-AI-SDLC-NgheAn/actions/runs/44919726436) (`push main`) đều thành công | Đạt một phần: chưa thử trên macOS hay Linux thật của người dùng; CI chỉ kiểm máy chủ khởi động, không mở trình duyệt |

## B. Hồi quy, ghi chép và phát hành

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P4-07 Retro rà hành động đã chốt ở retro Phase 2 (đã làm chưa, vì sao), nêu một lỗi AI và cách nhóm xác minh; hồ sơ cá nhân đủ 4 người (≤ 200 từ, có link commit); standup phút 20; nhật ký AI đủ người | Đọc `docs/retro.md`, `docs/members/`, `docs/standup.md`, `docs/ai-usage-log.md`; kiểm link commit và số từ | Đủ 4 hồ sơ (153 đến 183 từ, 19 link commit đều có thật); retro Phase 4 có phần của cả 4 người; standup có dòng Phase 4 của cả 4 người; TuHoAnh (B) đã hoàn tất nhật ký AI Phase 3 P3-04 và Phase 4 P4-01, xác nhận retro Phase 3 và bổ sung retro Phase 4; tài khoản Git `HoAnhTu245` và `TuHoAnh` đã được xác nhận | Đạt |
| AC-P4-08 Hồi quy Phase 1–3 còn hiệu lực; `docs/verification/phase-4.md` khớp commit gắn tag; tag `phase-4` và GitHub Release `v1.0.0` cùng commit trên `main` chậm nhất 3:00 | Chạy lại lệnh ở đầu file; `git tag`; trang Release | 388 test OK; smoke Phase 1–3 lần lượt 27/27, 15/15, 13/13; kiểm tất định và hard-code OK; [release notes](../release-notes-v1.0.0.md) | Sẵn sàng gắn tag `phase-4` và Release `v1.0.0` (388 test và toàn bộ smoke đều đạt) |

### Test và công cụ đổi trong Phase 4 và lý do
- Contract lên 1.3: `tests/test_contract_v11.py`, `tests/test_p3_v12_cli.py` và `tools/smoke_phase3.py` đổi khẳng định phiên bản từ "1.2" sang "1.3"; `tests/test_gather_prd.py` chuyển điều kiện `invuln_ticks` thành "mọi bản trừ 1.0" (PR #55). Kho cá thể và số chuẩn không đổi.
- `.github/workflows/ci.yml` (khung giảng viên) chỉ thêm bước: hồi quy Phase 1–3 và `bench_cmd`, `soak_cmd` bản ngắn (PR #57).

## C. Ticket-04 mục "Mở rộng"
Không làm (nhóm 4 người không bắt buộc): bảng xếp hạng cục bộ, phụ đề SFX. README mục "Sáng tạo của nhóm" ghi chưa có mở rộng ngoài đề.

## Đánh giá ngắn

- **Đạt:** contract 1.3 và hai lệnh, soak 10 Ngày không sập, bench đúng lệnh và đạt mốc báo cáo, ba cảnh báo và tương phản cao, đóng gói và clone sạch, hồi quy Phase 1–3 xanh trên Windows và CI Ubuntu; retro và nhật ký AI đã hoàn tất.
- **Đạt một phần:** bench (hiệu ứng mặc định chưa rõ, A chưa xác nhận), cảnh báo (mốc 25% giả định), đóng gói (giấy phép MIT giả định), clone sạch (chưa thử macOS/Linux thật).
- **Sẵn sàng:** gắn tag `phase-4` và tạo Release `v1.0.0`.
- **Hạn chế chung:** Ticket-03 và Ticket-04 đã đối chiếu với đề trên lab board; Ticket-02 chưa nên một số luật Phase 2 vẫn là giả định (`docs/clarify.md`); chưa có bộ test ẩn của giảng viên; soak không kiểm luồng nấu, phục vụ, Shop; bench đo bộ vẽ phần mềm.
- **Checklist phát hành:** gắn tag `phase-4` và tạo Release `v1.0.0` trên commit đã kiểm chứng, kèm bản đóng gói.
