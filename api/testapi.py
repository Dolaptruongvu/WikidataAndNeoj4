import requests


url = "http://127.0.0.1:5000/getPoliticantDetails"


payload = {
    "name": "Nguyễn Xuân Phúc"
}

try:
    # Gửi POST request
    response = requests.post(url, json=payload)
    print(response)

   
    if response.status_code == 200:
        
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition:
            
            filename = content_disposition.split("filename=")[-1].strip('"')
            print(f"Tên file từ API: {filename}")
        else:
            filename = "politicant_details.csv"
            print(f"Không tìm thấy tên file trong tiêu đề. Sử dụng tên mặc định: {filename}")

        
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"File CSV đã được lưu thành công: {filename}")
    else:
        print(f"Request thất bại. Status code: {response.status_code}")
        print("Chi tiết lỗi:", response.json())
except Exception as e:
    print(f"Lỗi xảy ra: {e}")