

import configparser


print() #공백문자
print() #공백문자

# Config 파일 읽기
properties_file = "./logviewer.properties"
file_path=""
context_line=0
keyword=""

with open(properties_file, "r", encoding="utf-8") as properties:
    p_lines = "[DEFAULT]"+properties.read() # properties를 line으로 저장
parser = configparser.RawConfigParser()
parser.read_string(p_lines)

file_path = parser.get("DEFAULT", "logviewer.file.path",  fallback='').strip()
context_line = parser.get("DEFAULT", "logviewer.context.lines",  fallback='').strip()
with open(file_path, "r", encoding="utf-8") as log:
    l_lines = log.readlines()

keyword = parser.get("DEFAULT", "logviewer.condition.keywords",  fallback='').strip()

print("filePath = " ,file_path)
print("contextLine = ", context_line )
print("keyword = ", keyword)

print("1. ----------------------------")

extract_list = ""


    for line in l_lines :
        if keyword in line.upper():
            extract_list += line
           # print()

print("2.extract_list = ----------------------------")
print(extract_list)

