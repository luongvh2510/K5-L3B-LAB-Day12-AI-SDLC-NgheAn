# Hợp đồng tích hợp (nên chốt sớm; hình thức do nhóm chọn)

Điền trong 15 phút kickoff (hoặc thay bằng một mục trong README / một bảng trên giấy, miễn cả nhóm cùng thống nhất):
1. **Schema file kho** — khớp mục G của PRD-0 (kho ghi khi `gather_end`) + một file kho mẫu hợp lệ: `inventory.sample.json`.
2. **Giao diện giữa `sim/*` và `client/ui`** — trạng thái nào UI được đọc, lệnh nào UI gửi vào.
3. **Danh sách sự kiện** — tên, `data`, ai phát, ai nghe (gather: `gather`, `node_regrown`, `hold_full`, `fish_caught`, `gather_end`...; quan: theo mục E của PRD-0).

Khi đổi hợp đồng sau này: báo cả nhóm và ghi lại lý do (ADR hoặc ghi chú, tùy chọn).

---

## 1. Schema file kho

_(D chốt — P1-02)_

---

## 2. Giao diện sim ↔ UI

> Đề xuất: C (`Cuongngucuteee`) — P1-15. Trạng thái: **đề xuất, chờ cả nhóm đồng ý**.
> Nguồn: đọc từ khung hiện có (`chonoi/runner.py`, `chonoi/sim/gather.py`, `chonoi/sim/quan.py`, `chonoi/live.py`).

### 2.1 Nguyên tắc

1. **UI chỉ ĐỌC snapshot.** Không import, không gọi hàm, không sửa thuộc tính của `GatherSim`/`QuanSim`.
2. **UI chỉ GỬI input** (trạng thái phím đang giữ). Mọi luật (cạnh lên, ramp, chọn đối tượng interact) nằm ở sim.
3. **Snapshot của UI = dòng `snapshot` của headless** (`Session.snapshot()`), cộng vài trường riêng của live (mục 2.4). Thêm trường mới vào snapshot được; **đổi tên hoặc xóa trường thì phải báo cả nhóm** (test hộp đen đọc cùng các trường đó).
4. UI **bỏ qua trường chưa có** (chưa viết luật thì không vẽ, không lỗi).
5. Sáng tạo riêng của UI (âm thanh, hiệu ứng, animation) **suy ra từ snapshot/sự kiện**, không thêm trạng thái vào sim. Nếu cần trạng thái sim mới thì phải tắt được ở headless.

### 2.2 Lệnh UI gửi vào (`POST /input`)

| Trường | Kiểu | Ý nghĩa | Phím (live) |
|---|---|---|---|
| `move` | `[a, b]`, mỗi số trong `[-1, 1]` | gather: `[dx, dd]` (d dương = lặn sâu hơn); quan: `[dx, dz]`. Sim tự chuẩn hóa vector | WASD / mũi tên |
| `interact` | `bool` (đang giữ) | gather: hái nút / cập bến; quan: bếp / bàn. Sim lấy **cạnh lên** | E |
| `catch` | `bool` (đang giữ) | gather: bắt cá. Sim lấy cạnh lên | Space |

Ngoài ra: `POST /restart` chơi lại với cùng seed và scenario (phím R). Input sai trả `400`.

### 2.3 Trường UI đọc (`GET /state`)

**Chung cho mọi mode** (do `runner._common` dựng, nhóm không cần viết lại):

| Trường | UI dùng để |
|---|---|
| `tick`, `mode`, `phase`, `state` | chọn màn vẽ (`gather` / `quan`), nhấp nháy |
| `time_left_ticks` | đồng hồ đếm ngược (÷ `tick_hz`) |
| `money`, `earned`, `reputation`, `score` | HUD tiền / uy tín / điểm |

**gather** (`GatherSim.snapshot`):

| Trường | UI dùng để |
|---|---|
| `player.pos` `[x, d]`, `player.vel`, `player.heading_deg` | vẽ Út Sen, hướng bơi |
| `player.oxygen_ticks`, `player.oxygen_max_ticks` | thanh oxy |
| `player.zero_oxy_ticks` | cảnh báo ngạt (đỏ nhấp nháy) |
| `player.hp`, `player.hp_max`, `player.invuln_ticks` | Máu; nhấp nháy khi đang miễn thương |
| `player.catch_cd_ticks` | vòng hồi chiêu bắt cá |
| `player.at_surface` | trạng thái nổi / lặn, gợi ý "E để hái" |
| `hold` (mảng kind, LIFO), `hold_count`, `hold_capacity` | ô giỏ; báo giỏ đầy |
| `nodes[]`: `id, pos, kind, ready, regrow_ticks` | vẽ nút hái; nút chưa mọc thì mờ + đếm |
| `fish[]`: `id, pos, kind, heading_deg` | vẽ cá |

**quan** (`QuanSim.snapshot`):

| Trường | UI dùng để |
|---|---|
| `player.pos` `[x, z]` | vẽ nhân vật |
| `stock` (kind → số, chỉ số > 0) | HUD kho nguyên liệu |
| `hand` (null hoặc món đang bưng) | món trên tay |
| `stoves[]`: `id, pos, state, dish, cook_ticks_left, ready_ticks` | bếp: trống / đang nấu (thanh tiến độ) / chín |
| `tables[]`: `id, pos, customer_id` | bàn có khách hay trống |
| `customers[]`: trường do B chốt trong lát 3–4 | khách, món gọi, thanh kiên nhẫn |

**Đề nghị B giữ các trường sau trong `customers[]`** (UI cần để vẽ; tên chốt theo PRD-0 mục E/F): `id`, `table_id`, `dish`, `state`, `patience_ticks`, `reserved`. B đổi tên nào thì báo C.

### 2.4 Trường chỉ có ở live (không có trong JSONL headless)

| Trường | Ý nghĩa |
|---|---|
| `meta` | `tuning[mode]` trong `game.contract.json` (biên bản đồ, vị trí bến, bán kính...) để UI vẽ, không hard-code |
| `events` | tối đa 40 dòng sự kiện gần nhất `{type:"event", tick, phase, name, data}`; UI dùng cho thông báo/âm thanh |
| `finished`, `reason` | buổi đã kết thúc và lý do (`docked`, `timeout`, ...) |
| `error` | luật ném lỗi (UI hiện thông báo, không crash) |

### 2.5 Sự kiện UI nghe (phản hồi hình ảnh/âm thanh)

UI **không** phát sự kiện, chỉ nghe. Danh sách đầy đủ do D chốt ở mục 3; UI dự định phản hồi:
- gather: `dive`, `surface`, `oxygen_empty`, `choke`, `faint`, `gather`, `node_regrown`, `fish_caught`, `hold_full`, `gather_end`
- quan: `customer_arrived`, `no_dish`, `cook_started`, `dish_ready`, `dish_picked`, `served`, `paid`, `customer_left`, `quan_end`

Sự kiện nào UI không biết thì bỏ qua.

---

## 3. Danh sách sự kiện

_(D chốt — P1-02; A, B bổ sung `data` của sự kiện mình phát)_

| Tên | `data` | Ai phát | Ai nghe |
|---|---|---|---|
