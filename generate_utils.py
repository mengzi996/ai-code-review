# generate_utils.py
import requests
import json
import os

# Ollama API 地址
OLLAMA_API = "http://localhost:11434/api/generate"

# 要生成的工具类列表
utils = [
    {
        "name": "DateUtils",
        "prompt": "写一个Java工具类 DateUtils，包含：formatDate(Date date, String pattern) 和 parseDate(String str, String pattern) 方法，使用SimpleDateFormat，线程安全。"
    },
    {
        "name": "StringUtils",
        "prompt": "写一个Java工具类 StringUtils，包含：isBlank(String str)、trim(String str)、join(String[] array, String delimiter) 方法。"
    },
    {
        "name": "FileUtils",
        "prompt": "写一个Java工具类 FileUtils，包含：readFile(String filePath) 和 writeFile(String filePath, String content) 方法，使用try-with-resources，处理IOException。"
    }
]


def call_ollama(prompt, model="deepseek-coder:6.7b"):
    """调用 Ollama API 生成代码"""
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API, json=data)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Error: {e}"


def extract_java_code(text):
    """从AI响应中提取Java代码块"""
    if "```java" in text:
        start = text.find("```java") + 7
        end = text.find("```", start)
        return text[start:end].strip()
    return text.strip()


# 主流程
for util in utils:
    print(f"正在生成 {util['name']}...")

    # 调用 AI
    raw_response = call_ollama(util["prompt"])

    # 提取 Java 代码
    java_code = extract_java_code(raw_response)

    # 保存为 .java 文件
    filename = f"{util['name']}.java"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(java_code)

    print(f"✅ 已生成: {filename}")

print("\n🎉 所有工具类生成完成！")