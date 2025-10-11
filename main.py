# main.py
import subprocess

# Chạy web server app.py
p1 = subprocess.Popen(["python3", "app.py"])

# Chạy tool nền autotoken.py
p2 = subprocess.Popen(["python3", "autotoken.py"])

# Giữ cho chương trình chạy mãi cho đến khi dừng
p1.wait()
p2.wait()
