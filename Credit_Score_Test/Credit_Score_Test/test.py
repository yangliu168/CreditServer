import os
print("--------------------------------")
print((os.path.abspath(__file__)))
print("--------------------------------")
print((os.path.dirname(os.path.abspath(__file__))))
print("--------------------------------")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)