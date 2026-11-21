# Quán Ăn Chợ Nổi v1.0.0

Game 2D nhỏ của nhóm NgheAn (lab Day 12, AI SDLC): buổi sáng Út Sen **lặn bắt cá, hái rau** trên sông (tránh Cá Sấu, canh oxy và Máu), buổi tối **mở quán** nấu và phục vụ khách, cuối Ngày ghé **Shop** nâng cấp oxy và Máu. Một Ngày chạy liền ba pha, chơi 1 đến 5 Ngày.

## Điểm mới của bản 1.0.0 (so với các tag phase trước)
- **Độ tươi (Phase 3, thay đổi phá vỡ):** kho là kho cá thể có độ tươi (`contract_version` 1.2). Hàng hao tươi theo thời gian, ươn khi dưới 30 điểm (vẫn chiếm ô nhưng không nấu được), giữ chỗ theo id, giá món tính theo độ tươi trung bình; cửa sổ chơi có HUD độ tươi, hàng ươn và đơn bị ảnh hưởng.
- **Đo hiệu năng và soak (Phase 4, contract 1.3):** `bench_cmd` đo bộ vẽ phần mềm cảnh lặn, `soak_cmd` chạy 10 Ngày liền trong một tiến trình để kiểm độ bền.
- **Cảnh báo dễ nhận biết:** thủy quái gần, oxy sắp hết, khách sắp giận, có biểu tượng và chữ (không chỉ màu); chế độ tương phản cao (phím H hoặc `?hc=1`).
- **Đóng gói:** README chạy từ clone sạch bằng 3 lệnh, `CHANGELOG.md` theo từng phase, `CREDITS.md`, `LICENSE`, CI Ubuntu.

## Cách chạy (clone sạch, 3 lệnh, macOS hoặc Linux)

Cần Python 3 (CI dùng 3.12), không cần cài gói nào.

```bash
git clone https://github.com/luongvh2510/K5-L3B-LAB-Day12-AI-SDLC-NgheAn.git
cd K5-L3B-LAB-Day12-AI-SDLC-NgheAn
python3 -m chonoi.live
```

Mở địa chỉ in ra (mặc định `http://127.0.0.1:8000/`), chọn chế độ ở menu rồi chơi. WASD hoặc mũi tên để bơi và đi, E để cập bến, hái, thao tác bếp và bàn, Space bắt cá, P hoặc Esc tạm dừng, 1 và 2 mua ở Shop, Enter sang Ngày mới, H tương phản cao.

Lệnh cho người phát triển và chấm tự động:

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests                       # toàn bộ test
python3 -m chonoi.headless --mode day --days 1 --seed 1 --ticks 600 --out out.jsonl   # headless (Test Contract)
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json              # bench_cmd
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json                     # soak_cmd
python3 tools/check_determinism.py                                            # cùng seed, output giống từng byte
```

## Số liệu kiểm chứng
- Test: 388 test OK; smoke Phase 1 27/27, Phase 2 15/15, Phase 3 13/13; kiểm tất định và kiểm hard-code OK.
- Bench (`--seed 42 --duration 30`, bộ vẽ phần mềm 1280×720 trong bộ nhớ): 32.673 khung (32673 frames), 1089.09 FPS trung bình, 517.85 FPS 1% low, `load_ms` 96.97; đạt mốc báo cáo của đề (avg ≥ 60, 1% low ≥ 30, load ≤ 10 s).
- Soak (`--seed 7 --days 10`): 10/10 Ngày, 0 crash, `duration_s` 6.29s.
- CI Ubuntu: xem workflow CI trên tag `phase-4` (các lần chạy `push main` đã xác minh: [run 44918861655](https://github.com/luongvh2510/K5-L3B-LAB-Day12-AI-SDLC-NgheAn/actions/runs/44918861655), [run 44919726436](https://github.com/luongvh2510/K5-L3B-LAB-Day12-AI-SDLC-NgheAn/actions/runs/44919726436)).
- Ma trận truy vết: [docs/verification/phase-4.md](verification/phase-4.md); bằng chứng ở `docs/proof/`.

## Thay đổi phá vỡ cần biết
- Từ `contract_version` 1.2 **file kho là mảng cá thể** `{"items": [{"id": "I1", "kind": "ca_linh", "fresh": 100}, ...]}`. File kho đếm của v1.1 (`{"items": {"ca_loc": 2}}`) hoặc sai schema bị từ chối (mã thoát 2) ở `--inventory`. Cách chuyển file cũ: `counts_to_individuals` trong `chonoi/inventory.py`. Chi tiết ở `CHANGELOG.md`.

## Giới hạn đã biết (nói thẳng)
- **Đề của Ticket-02 không có trong repo** nên một số luật Phase 2 (Cá Sấu, số chuẩn) là giả định đã ghi ở `docs/clarify.md`, chưa có bộ kiểm của giảng viên để đối chiếu. Ticket-03 và Ticket-04 đã được đối chiếu với đề trên lab board (khóa `freshness`, công thức giá, payload `spoiled`, lệnh bench và soak).
- **Bench đo bộ vẽ phần mềm trong bộ nhớ**, không phải FPS của giao diện trình duyệt; "hiệu ứng mặc định" của đề chưa rõ nên chưa có.
- **Soak dùng bot chỉ lặn, hái và về bến**: không nấu, không phục vụ, không mua ở Shop, nên kiểm độ bền nhiều Ngày chứ không kiểm kinh tế hay luồng nấu, phục vụ.
- **Giấy phép MIT là giả định** chờ xác nhận (`clarify` #13); mốc 25% của cảnh báo oxy và khách cũng là giả định (`clarify` #16).
- **Chưa thử trên macOS hay Linux thật của người dùng**; Ubuntu chỉ qua CI, và CI chỉ kiểm máy chủ khởi động.
- Chưa làm phần mở rộng (bảng xếp hạng, phụ đề SFX).

## Đính kèm
- **Bản đóng gói chạy được:** tạo từ đúng commit gắn tag bằng `git archive --format=zip --prefix=quan-an-cho-noi-v1.0.0/ -o quan-an-cho-noi-v1.0.0.zip phase-4`; giải nén rồi chạy `python3 -m chonoi.live` (không cần cài gói).

## Ghi công
Nhóm NgheAn: Nguyễn Đức Nhật, Hồ Anh Tú, Phan Trần Mạnh Cường, Võ Hồng Lương. Khung starter và đề do giảng viên cấp. Công cụ AI đã dùng theo từng phase ghi ở `docs/ai-usage-log.md` và `CREDITS.md`. Không dùng asset ngoài; hình vẽ bằng Canvas, chữ dùng font hệ thống, không có âm thanh. Giấy phép: MIT, xem `LICENSE`.
