# ATK-Pro – Trình Tái Tạo Gạch Tổ Tiên
**Lưu ý:** Dự án này được phát triển, duy trì và hỗ trợ hoàn toàn bởi một người duy nhất. Mọi phản hồi, báo cáo hoặc đóng góp đều được hoan nghênh, nhưng không có đội ngũ hay cơ cấu công ty nào đứng sau việc phát triển.
## Mô tả
ATK-Pro là một công cụ tiên tiến để tái tạo, lưu trữ và tra cứu hình ảnh và tài liệu phả hệ được số hóa từ cổng thông tin Antenati. Dự án hỗ trợ quản lý đa ngôn ngữ và phân phối dưới dạng ứng dụng độc lập cho Windows.
## Các chức năng chính
- Tái tạo ảnh tự động từ các ô IIIF
- Hỗ trợ đa ngôn ngữ (20 ngôn ngữ)
- Giao diện đồ họa hiện đại (Qt)
- Tạo tệp EXE độc lập và trình cài đặt đa ngôn ngữ
## Cài đặt
1. Tải xuống trình cài đặt ATK-Pro-Setup-v2.0.exe hoặc tệp thực thi độc lập ATK-Pro.exe từ phần phát hành.
1. Làm theo hướng dẫn trên màn hình để hoàn tất cài đặt.
1. Khởi động ATK-Pro từ menu Start hoặc từ thư mục cài đặt.
## Cấu trúc dự án
- `src/` – Mã nguồn chính (GUI, logic, module)
- `assets/` – Tài sản đa ngôn ngữ (hướng dẫn, mẫu, tài nguyên)
- `locales/` – Tệp dịch .ini cho mỗi ngôn ngữ
- `docs_generali/` – Thuật ngữ, tài liệu chung, lộ trình
- `scripts/` – Script bảo trì, dịch thuật, xác thực
- `tests/` – Kiểm thử tự động và kiểm thử bao phủ
- `dist/` – Đầu ra bản dựng/trình cài đặt
## Tài liệu
- Tài liệu lịch sử và chi tiết hiện đã được lưu trữ tại `docs_generali/archivio/`.
- Tệp README này và tệp `CHANGELOG.md` tóm tắt trạng thái và các cột mốc chính của dự án.
## Lịch sử và phát triển
Dự án ra đời như một sự phát triển của các công cụ phả hệ kỹ thuật số, chú trọng đến tính minh bạch, lưu trữ lịch sử và hỗ trợ quốc tế. Mỗi cột mốc đều được theo dõi và ghi lại trong kho lưu trữ.
## Tín dụng
Phát triển và bảo trì: Daniele Pigoli
Đóng góp: xem nhật ký thay đổi và ghi chú phát hành
## Nhật ký thay đổi
Tham khảo tệp `docs_generali/CHANGELOG.md` để biết những thay đổi và cột mốc chính của dự án.
Để biết chi tiết lịch sử và ghi chú đầy đủ, hãy xem thư mục `docs_generali/archivio/`.

-----
## Tình trạng hiện tại
- Tất cả các mô-đun đang hoạt động đã được kiểm tra với phạm vi bao phủ trực tiếp và phòng thủ
- Chú thích với khối `# === Phạm vi kiểm thử ===` trong các mô-đun đã xác thực
- Mô-đun main.py, mặc dù có độ bao phủ một phần (64%), đã được xác thực về mặt logic vì nó mang tính điều phối
### Các bước tiếp theo
- Chuẩn bị phiên bản 2.1 với sự phát triển tăng dần và tài liệu cập nhật

✍️ Được biên soạn bởi Daniele Pigoli – với mục đích kết hợp sự chặt chẽ về kỹ thuật và ký ức lịch sử.
