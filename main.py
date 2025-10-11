import subprocess

# Chạy app.py (server chính)
p1 = subprocess.Popen(["python3", "app.py"])

# Chạy autotoken.py (tự động token)
p2 = subprocess.Popen(["python3", "autotoken.py"])

# Đợi cả hai tiến trình
p1.wait()
p2.wait()
