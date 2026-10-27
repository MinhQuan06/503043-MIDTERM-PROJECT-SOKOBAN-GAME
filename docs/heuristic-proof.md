# Chung minh heuristic (Req 4)

> Khung cau hoi de tu dien noi dung. Khong copy nguyen van tu slide nhom khac hay bat ky nguon nao - day la phan noi dung cham diem, phai tu viet.

## 1. Dinh nghia heuristic

- Heuristic dang dung la gi? Mo ta bang loi + cong thuc.
- Tham chieu toi ham trong code: `core/heuristic.py` (`compute_push_distances`, `make_heuristic`).
- Vi sao day KHONG phai Manhattan/Euclidean distance don thuan (no khac o diem nao)?

Trả lời: 
- Heuristic đang dùng là push-distance, tức là tổng các lần đẩy box để đưa tới goal, làm sao cho chi phí đẩy thùng là ít hơn chi phí tối ưu thực tế. Tính khoảng cách từ mỗi thùng đến ô đích gần nhất, sau đó cộng các khoảng cách đó lại
- Việc không dùng Manhattan/Euclidean distance là vì chúng đi xuyên tường luôn, không phản ánh đúng mê cung, còn push-distance tính theo cặp ô (ô box + ô agent đứng sau để đẩy), không phải khoảng cách đơn thuần agent→box

## 2. Chung minh Admissible (h(n) <= h*(n))

- Phat bieu claim.
- Lap luan: moi box can it nhat bao nhieu luot day de toi goal gan nhat, theo khoang cach BFS tren luoi (khong tinh vat can/box khac)?
- Vi sao tong cac khoang cach do la can duoi an toan cho chi phi that (h*(n))?

Trả lời:
- Khoảng cách ước lượng chính là giá trị cận dưới của h*(n) hay nói cách khác h*(n) = min của tổng lượt đẩy các box sẽ luôn lớn hoặc bằng h(n) vì h(n) chính là cận dưới.N ếu h(n) > h*(n) thì không admissible, nên ta cần chứng minh điều đó không xảy ra. Vì là việc bỏ qua box khác làm vật cản là 1 phép nới lỏng ràng buộc (relaxation), chi phí thật luôn ≥ ước lượng vì thực tế có thể bị box khác chặn đường, ước lượng thì không, nên ước lượng luôn sẽ nhỏ hơn thực tế, cho nên tổng chi phí tối ưu (min) thực tế sẽ không bao giờ nhỏ hơn ước lượng. Mỗi thùng có một mức chi phí tối thiểu riêng. Vì mỗi lượt đẩy chỉ đẩy 1 thùng, ta cộng các mức tối thiểu đó để thu được mức chi phí tối thiểu cho toàn bộ các thùng.
- Mỗi thùng khi chi phí tối ưu thực tế sẽ không nhỏ hơn. Và khi cộng lại các chi phí ước lượng đó, thì nó vẫn là tổng cận dưới của tổng chi phí tối ưu thực tế. Nhiều box chọn chung 1 goal gần nhất chỉ làm ước lượng thấp hơn hoặc bằng, không bao giờ cao hơn chi phí thật

- Note câu để báo cáo: "Tính admissibility của hàm heuristic được chứng minh bằng cách xác định khoảng cách BFS tối thiểu từ mỗi thùng đến ô đích gần nhất trên lưới đã đơn giản hóa, không xét các thùng khác có thể gây cản trở. Do các yếu tố này chỉ có thể làm tăng độ khó của bài toán thực tế, khoảng cách thu được tạo thành cận dưới cho số lượt đẩy cần thiết của từng thùng. Tổng các cận dưới này không vượt quá chi phí tối ưu thực tế, do đó \(h(n)\leq h^*(n)\), và hàm heuristic là admissible"
## 3. Chung minh Consistent (h(n) - h(n') <= cost(n, n'))

- Phat bieu claim.
- Lap luan: 1 buoc di/day chi phi bang 1. Khoang cach BFS cua box (neu bi day) thay doi toi da bao nhieu?
- Neu buoc do khong day box nao thi h thay doi the nao?

Trả lời:
- Sau 1 bước đi, giá trị heuristic không được giảm nhiều hơn chi phí của bước đi đó. Tức là h(n) hiện tại - h(n) sau hiện tại sẽ nhỏ hơn hoặc bằng chi phí bước đi. Và khi thùng bị đẩy thì khoảng cách ngắn nhất đến đích chỉ có thể thay đổi tối đa 1, Khoảng cách có thể giảm 1, khoảng cách có thể tăng 1, hoặc khoảng cách không đổi. Vì chỉ có 1 thùng được đẩy trong 1 bước, các thùng còn lại giữ nguyên vị trí. Nếu khoảng cách của thùng A giảm nhiều nhất 1, thì tổng heuristic cũng giảm nhiều nhất 1. Vì push-distance là khoảng cách BFS, mà BFS có tính chất 2 ô kề nhau (trước/sau khi đẩy) chênh lệch khoảng cách tối đa 1, nên đây là lý do kỹ thuật vì sao giảm tối đa 1 luôn đúng
- Nếu không thay đổi box thì h(n) sẽ không thay đổi, chỉ có những box được đẩy thì h(n) sẽ được thay đổi
## 4. Kiem chung thuc nghiem

- Dan ket qua chay `tests/test_heuristic.py` (PASS/FAIL, bao nhieu transition da kiem tra, tren map nao).
- Giai thich ngan gon: test nay kiem tra dieu gi tuong ung voi phan 2 va 3 o tren?

Trả lời:
- Chạy tests/test_heuristic.py trên map1 → PASS, xác nhận h(initial) ≤ optimal_cost và không có vi phạm consistency qua 500 transition lấy mẫu bằng BFS từ initial state, và tương ứng kiểm chứng thực nghiệm cho phần 2 (admissible, dòng assert đầu) và phần 3 (consistent, assert trong vòng lặp)

## 5. (Tuy chon) Lien he voi so lieu Req 3

- Dan 1-2 dong tu `docs/experiments/results.csv` / `results.png` de minh hoa heuristic nay giup A* hieu qua hon UCS the nao (vi du: so node expanded).

Trả lời:
- Việc áp dụng heuristic admissible và consistent, A* cắt giảm số node expand gấp ~38 lần so với UCS trên map1 (485175 → 12801), vẫn giữ cost tối ưu không đổi (34)