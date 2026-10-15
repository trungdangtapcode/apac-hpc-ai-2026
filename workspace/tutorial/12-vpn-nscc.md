# Check Point VPN và server NSCC

## Trạng thái cập nhật sau20:47UTC ngày15/10/2026

**Hiện chưa kết nối lại đượcVPN.** Những dòng “đã kết nối” bên dưới là lịch sử
thử nghiệm thành công trước đó. PhiênLinux cũ thoát20:17UTC với`IKE SA expired`.
Đã kiểmsource: snx-rs6.5.1 mặc địnhIKE28800s(8giờ), helper cũ khôngoverride;
helper hiện yêu cầu86400s(24giờ) cho lần kết nối mới, chưa kiểm chứngthời lượng.
Login lại20:40/20:47 bị gateway từ chối xác thực; chưa xác định lý do.
Người dùng báoWindows vẫn kết nối24giờ. SSHControlPersist24giờ là chuyện riêng.
Đọc [đính chính và bằng chứng](../notes/CURRENT.md) trước khi xử lý tiếp.

## Lịch sử cài đặt và thử nghiệm thành công

Kiểm tra ngày15/10/2026. **Đã cài và kết nối VPN rootless thành công.**

IPsec qua TCP (TCPT) đã nhận IP VPN và truyền dữ liệu. Kết nối tới
`aspire2p.nscc.sg` trả về banner OpenSSH. **Đã đăng nhập SSH thành công**, lệnh
`hostname` trả về **`a2ap-login02`**; lần thử này không yêu cầu DUO.
Không cần sudo hoặc Docker daemon. Script mặc định đã đổi sang IPsec/TCPT.

Vào SSH qua phiên VPN đang mở:

```bash
bash /home/apacsc42/workspace/vpn-rootless/vpn.sh ssh
```

Thử nghiệm SSL trước đó qua được xác thực nhưng kẹt bước tạo tunnel; IPsec/UDP
nhận IP nhưng không có dữ liệu về và bị lỗi keepalive. IPsec/TCPT đã hoạt động.
Các ghi chú "đang chờ xác thực" phía dưới thuộc các bước thử trước đó.

## Cập nhật: không có sudo vẫn dựng được môi trường VPN riêng

Đã kiểm tra thực tế: tạo user/network namespace và thiết bị TUN thành công,
dùng `slirp4netns` để namespace có Internet, rồi cài `snx-rs` trong workspace.
Client đã đọc được phương thức `NSCC_LDAP` từ cổng NSCC. Không cần Docker daemon.
Các binary được kiểm tra SHA256 theo release của dự án.

Lỗi TLS được giải quyết bằng intermediate CA GlobalSign đúng chuỗi; chứng chỉ
gateway đã verify thành công. Không tắt kiểm tra chứng chỉ. DNS/hosts chỉ sửa
bên trong namespace, route máy login giữ nguyên.

Phiên xác thực đầu đang chờ; chưa có tunnel và chưa SSH được vào NSCC. Có thể
cần xác nhận DUO. Đây là community client, khác bộ CShell trong tài liệu NSCC;
khả năng tương thích đăng nhập chưa được xác nhận.

[Hướng dẫn rootless và lệnh chạy](/home/apacsc42/workspace/vpn-rootless/README.md).

Nhận định trước rằng thiếu sudo đồng nghĩa không cài được trên máy này là quá
vội. Thiếu sudo chặn cách cài chính thức vào hệ thống; namespace riêng đã hoạt động.

**Các mục bên dưới ghi lại kiểm tra ban đầu trước khi dựng rootless.**

Theo đề Qwen, nền tảng còn lại là **NSCC ASPIRE2A+**, gồm hai node H100,
tổng16 GPU. Đây là cluster riêng, không phải thêm node vào Slurm hiện tại.

## Có cài bằng terminal được không?

Có công cụ Linux, nhưng cách kết nối phụ thuộc cấu hình cổng VPN. Hướng dẫn
[NSCC cho Linux](https://help.nscc.sg/wp-content/uploads/ASPIRE2AP-VPN-Linux.pdf)
dùng terminal để cài, sau đó trình duyệt Mobile Access và DUO để đăng nhập;
cần sudo. Không thể mặc định rằng mọi cổng Check Point đều dùng được một lệnh
CLI. [Tài liệu Check Point](https://sc1.checkpoint.com/documents/SSL_Network_Extender_AdminGuide/Default.htm)
phân biệt Mobile Access và Remote Access VPN.

## Máy hiện tại

- Máy: `login.hpcai2025.smc`, môi trường Podman, user `apacsc42`.
- Rocky Linux9.8 theo `/etc/os-release`; không có SNX hoặc OpenConnect.
- `sudo -n -l` yêu cầu mật khẩu; chưa xác nhận tài khoản có sudo sau xác thực.
- Tiến trình hiện tại không có `CAP_NET_ADMIN`, chưa có quyền sửa route hệ thống.
- Có `/dev/net/tun`, nhưng riêng thiết bị này không đủ để chạy VPN toàn hệ thống.
- Chưa có phiên đồ hoạ qua `DISPLAY`.
- User/network namespace tạo được trong kiểm tra ngắn. Chưa dựng hoặc kiểm chứng
  VPN trong namespace riêng; không coi đây là phương án đã hoạt động.

## Địa chỉ cần dùng

Tài liệu NSCC ghi **`vpn1.nscc.sg`**. Địa chỉ `.org` được cung cấp trong chat
có chứng chỉ không khớp hostname trong kiểm tra TLS; không gửi thông tin đăng
nhập tới đó.

DNS mặc định trên máy này không phân giải được `.sg` trong lần kiểm tra.
DNS công khai Google trả về `103.72.192.1`. Thử TLS tới IP với hostname `.sg`
bị lỗi không xác minh được chuỗi CA bằng kho chứng chỉ hiện tại. Chưa tắt
kiểm tra chứng chỉ để đăng nhập. IP này là kết quả quan sát, không nên đóng
đinh lâu dài vì có thể thay đổi.

## Bước tiếp theo

Cần xác định máy cài VPN có quyền sudo hoặc được quản trị viên cài sẵn client.
Sau đó kiểm tra DNS và chuỗi CA đúng cổng NSCC, cài client phù hợp, xác thực
DUO, rồi thử SSH tới login node NSCC. Mật khẩu/OTP nhập trực tiếp lúc kết nối,
không đặt trong script, Git hay tham số dòng lệnh.

Chưa thay đổi route, DNS hoặc các job nghiên cứu đang chờ trên cluster hiện tại.
