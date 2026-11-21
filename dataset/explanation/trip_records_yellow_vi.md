# Từ Điển Dữ Liệu Chuyến Đi Taxi Vàng (Yellow Taxi Trip Records Data Dictionary)

*Nguồn gốc dữ liệu: New York City Taxi and Limousine Commission (NYC TLC)*  
*Ngày cập nhật tài liệu gốc: 18/03/2025*

---

## 1. Giải thích các thuật ngữ viết tắt quan trọng

| Thuật ngữ | Tên đầy đủ tiếng Anh | Giải thích chi tiết |
| :--- | :--- | :--- |
| **TPEP** | **Taxicab Passenger Enhancements Program** | • **Chương trình Cải tiến Trải nghiệm Hành khách Đi Taxi** do Ủy ban Taxi và Xe limousine New York (NYC TLC) ban hành.<br>• Là tổ hợp công nghệ phần cứng và phần mềm bắt buộc trang bị trên tất cả xe taxi vàng (Yellow Cabs) tại New York, bao gồm: đồng hồ tính cước điện tử (taximeter), máy quẹt thẻ thanh toán (POS), màn hình thông tin cho khách ở ghế sau (PIM), và thiết bị định vị GPS.<br>• Các trường dữ liệu có tiền tố `tpep_` (ví dụ `tpep_pickup_datetime`) được hệ thống TPEP ghi nhận tự động. |
| **MTA** | **Metropolitan Transportation Authority** | • **Cơ quan Giao thông Đô thị New York**, cơ quan phụ trách toàn bộ mạng lưới giao thông công cộng khu vực đô thị New York (tàu điện ngầm New York Subway, xe buýt công cộng, các tuyến đường sắt ngoại ô, cầu và hầm thu phí).<br>• Khoản thuế `mta_tax` (0.50 USD/chuyến) do đồng hồ taxi tự động thu và nộp về ngân sách MTA để duy trì và nâng cấp hạ tầng giao thông công cộng. |
| **TLC** | **Taxi and Limousine Commission** | • **Ủy ban Taxi và Xe Limousine Thành phố New York**, cơ quan chính quyền quản lý và cấp phép cho toàn bộ taxi vàng, taxi xanh (Green/Boro taxis), xe cho thuê theo hợp đồng (FHV như Uber, Lyft) tại New York. |
| **CBD** | **Central Business District** | • **Khu vực trung tâm thương mại Manhattan** (thường tính từ phố 60 trở xuống đến cực nam Manhattan). Phí `cbd_congestion_fee` được thu khi di chuyển vào khu vực này nhằm giảm ùn tắc giao thông. |

---

## 2. Bảng mô tả chi tiết các trường dữ liệu (Data Dictionary)

| STT | Tên trường (Field Name) | Ý nghĩa tiếng Việt | Mô tả chi tiết và quy ước giá trị |
| :---: | :--- | :--- | :--- |
| 1 | **VendorID** | Mã nhà cung cấp thiết bị TPEP | Mã định danh nhà cung cấp giải pháp công nghệ TPEP ghi nhận bản ghi chuyến đi:<br>• **1** = Creative Mobile Technologies, LLC (CMT)<br>• **2** = Curb Mobility, LLC (trước đây là Verifone / VTS)<br>• **6** = Myle Technologies Inc<br>• **7** = Helix |
| 2 | **tpep_pickup_datetime** | Thời gian đón khách | Ngày và giờ chính xác khi tài xế bật đồng hồ tính cước (bắt đầu chuyến đi). |
| 3 | **tpep_dropoff_datetime** | Thời gian trả khách | Ngày và giờ chính xác khi tài xế tắt đồng hồ tính cước (kết thúc chuyến đi). |
| 4 | **passenger_count** | Số lượng hành khách | Số lượng hành khách đi xe (do tài xế nhập thủ công vào đồng hồ tính cước). |
| 5 | **trip_distance** | Quãng đường chuyến đi | Tổng khoảng cách di chuyển của chuyến đi tính bằng dặm (miles), đo lường bởi đồng hồ tính cước thông qua cảm biến xe / GPS. |
| 6 | **RatecodeID** | Mã loại biểu giá cước | Mã biểu giá cước cuối cùng được áp dụng khi kết thúc chuyến đi:<br>• **1** = Giá cước tiêu chuẩn (Standard rate)<br>• **2** = Tuyến cố định Sân bay JFK (JFK flat rate)<br>• **3** = Tuyến Newark (Newark rate)<br>• **4** = Tuyến ngoại ô Nassau hoặc Westchester<br>• **5** = Cước phí thương lượng (Negotiated fare)<br>• **6** = Chuyến đi theo nhóm (Group ride)<br>• **99** = Giá trị trống / Không xác định (Null/unknown) |
| 7 | **store_and_fwd_flag** | Cờ lưu trữ và chuyển tiếp | Đánh dấu bản ghi chuyến đi có bị lưu tạm trong bộ nhớ xe trước khi gửi về máy chủ nhà cung cấp do mất sóng/kết nối mạng hay không:<br>• **Y** = Có lưu và chuyển tiếp sau (store and forward)<br>• **N** = Không lưu tạm (gửi dữ liệu trực tuyến thành công ngay lập tức) |
| 8 | **PULocationID** | Mã phân vùng đón khách | Mã số định danh phân vùng taxi của TLC (TLC Taxi Zone ID) nơi đồng hồ tính cước được bật (tra cứu theo bảng Taxi Zones Lookup). |
| 9 | **DOLocationID** | Mã phân vùng trả khách | Mã số định danh phân vùng taxi của TLC (TLC Taxi Zone ID) nơi đồng hồ tính cước được tắt (tra cứu theo bảng Taxi Zones Lookup). |
| 10 | **payment_type** | Phương thức thanh toán | Mã số biểu thị phương thức thanh toán tiền cước của hành khách:<br>• **0** = Chuyến đi giá linh hoạt (Flex Fare trip)<br>• **1** = Thanh toán qua thẻ tín dụng (Credit card)<br>• **2** = Thanh toán bằng tiền mặt (Cash)<br>• **3** = Miễn phí (No charge)<br>• **4** = Tranh chấp / Khiếu nại cước (Dispute)<br>• **5** = Không xác định (Unknown)<br>• **6** = Chuyến đi bị hủy (Voided trip) |
| 11 | **fare_amount** | Cước cơ bản theo đồng hồ | Tiền cước tính theo thời gian và quãng đường di chuyển được đồng hồ tự động đo lường. |
| 12 | **extra** | Phụ phí phát sinh | Các khoản phụ phí linh tinh, bao gồm: phụ phí giờ cao điểm buổi chiều (16h - 20h vào ngày làm việc: 1.00 USD), phụ phí qua đêm (20h - 06h: 0.50 USD). |
| 13 | **mta_tax** | Thuế giao thông MTA | Thuế tự động kích hoạt dựa trên biểu giá đồng hồ (mức tiêu chuẩn là 0.50 USD/chuyến). |
| 14 | **tip_amount** | Tiền boa (Tip) | Tiền tip cho tài xế. **Lưu ý quan trọng**: Trường này chỉ được hệ thống tự động ghi nhận khi hành khách quẹt thẻ tín dụng; tiền tip đưa bằng tiền mặt không được lưu trong trường này. |
| 15 | **tolls_amount** | Phí cầu đường | Tổng số tiền phí cầu đường (phí qua cầu, hầm thu phí) phát sinh trong suốt chuyến đi. |
| 16 | **improvement_surcharge** | Phụ phí cải tiến cơ sở hạ tầng | Phụ phí thu tại thời điểm bắt đầu chuyến đi (bắt đầu áp dụng từ năm 2015, tiêu chuẩn 0.30 - 1.00 USD tùy giai đoạn quy định của TLC). |
| 17 | **total_amount** | Tổng số tiền thu của khách | Tổng số tiền phải thanh toán của hành khách (không bao gồm tiền tip bằng tiền mặt). |
| 18 | **congestion_surcharge** | Phụ phí ùn tắc bang New York | Phụ phí ùn tắc giao thông bang New York (NYS congestion surcharge, thường là 2.50 USD cho taxi vàng di chuyển qua vùng phía nam phố 96 Manhattan). |
| 19 | **airport_fee** | Phí sân bay | Phí dịch vụ sân bay chỉ áp dụng khi đón khách tại hai sân bay: LaGuardia (LGA) và John F. Kennedy (JFK) (thường là 1.25 USD). |
| 20 | **cbd_congestion_fee** | Phí giảm ùn tắc trung tâm (CBD) | Phí thu trên mỗi chuyến đi áp dụng cho Vùng Cứu trợ Ùn tắc (Congestion Relief Zone) của MTA, bắt đầu có hiệu lực từ ngày 05/01/2025. |

---

## 3. Các lưu ý quan trọng khi thiết kế ETL và Data Warehouse

1. **Công thức cấu thành Tổng doanh thu (`total_amount`):**
   ```text
   total_amount = fare_amount + extra + mta_tax + tip_amount + tolls_amount + improvement_surcharge + congestion_surcharge + airport_fee + cbd_congestion_fee
   ```
2. **Xử lý dữ liệu Tiền tip (`tip_amount`):**
   - Chỉ có ý nghĩa phân tích chính xác với phương thức thanh toán là **Thẻ tín dụng (`payment_type = 1`)**.
   - Với các chuyến trả bằng tiền mặt (`payment_type = 2`), trường này thường ghi nhận là 0 (vì hệ thống TPEP không ghi nhận được tiền tip trao tay). Do đó, khi tính toán **tỷ lệ tiền tip trung bình (% tip)** trong yêu cầu nâng cao, cần lọc hoặc xử lý riêng cho các giao dịch bằng thẻ tín dụng.
3. **Tính toán thời gian và tốc độ di chuyển:**
   - Thời gian di chuyển (Trip Duration):
     ```text
     trip_duration = tpep_dropoff_datetime - tpep_pickup_datetime
     ```
   - Tốc độ di chuyển trung bình (Trip Speed):
     ```text
     trip_speed = trip_distance / trip_duration
     ```
   - Cần lọc các bản ghi bất thường (anomalies) như: `trip_duration <= 0`, `trip_distance <= 0`, hoặc tốc độ phi thực tế trước khi nạp vào Dimensional Data Store (DDS).

