# import library 
import re 

# url 
s = 'http://www.example.com/index.html'
s1 = 'trantest.com.vn'
REG = r'([\w\d]+\.[\w\d]+\.[\w\d]+)'
# searching for all capture groups 
obj = re.search(REG, s) 
obj1 = re.search(REG, s1) 
print(obj)
print(obj1)
