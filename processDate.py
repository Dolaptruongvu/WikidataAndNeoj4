import pandas as pd

# Đọc file CSV
df = pd.read_csv('./query.csv')

# Chuyển đổi cột 'dateOfBirth', 'dateOfDeath', 'startTime', 'endTime' sang định dạng 'YYYY-MM-DD'
df['dateOfBirth'] = pd.to_datetime(df['dateOfBirth'], errors='coerce').dt.strftime('%Y-%m-%d')
df['dateOfDeath'] = pd.to_datetime(df['dateOfDeath'], errors='coerce').dt.strftime('%Y-%m-%d')

df['startTime'] = pd.to_datetime(df['startTime'], errors='coerce').dt.strftime('%Y-%m-%d')
df['endTime'] = pd.to_datetime(df['endTime'], errors='coerce').dt.strftime('%Y-%m-%d')


# Ghi lại file CSV đã làm sạch
df.to_csv('query_cleaned_fixed.csv', index=False)

# Hiển thị kết quả đã xử lý (để kiểm tra)
df.head()
