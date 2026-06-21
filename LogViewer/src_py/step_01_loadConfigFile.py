

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

file_path = parser.get("DEFAULT", "logviewer.file.path",  fallback='').strip()  #fallback : 해당 값이 없을 경우 반환하는 Default 값
context_line = parser.get("DEFAULT", "logviewer.context.lines",  fallback='').strip()
keyword = parser.get("DEFAULT", "logviewer.condition.keywords",  fallback='').strip()

print("filePath = " ,file_path)
print("contextLine = ", context_line )
print("keyword = ", keyword)

print("1. 파일 Read ----------------------------")

# Properties에 있는 파일명을 읽어옴 -> log로
with open(file_path, "r", encoding="utf-8") as log:
    l_lines = log.readlines()


    # 추출 내용
    extract_list = ""
    line_list = []
    l = 1

    # 1줄씩 읽으면서 Matching되는 Line이 있으면 추출 내용에 추가
    for line in l_lines :
        if keyword in line.upper():
            extract_list += line
            line_list.append(l)
           # print()
        l += 1   # Python에서는 증감연산자를 지원하지 않음


# 추출 결과 Print
print("2.extract_list = ----------------------------")
print("추출 Line = ", line_list)
print()
print("<추출 내용>")
# print(extract_list)

# 문자열이 비어있지 않은 상태인지 체크 - print(bool(not "abc".strip())) = False
print(bool(not "abc".strip()))