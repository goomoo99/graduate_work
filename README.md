# 毕业设计

## 基于弹幕情感分析的直播高光时刻判断模型设计

1. 数据清洗与预处理
2. 基于词典的句子情感值计算模型
3. 基于机器学习的片段情感分析与高光时刻判断模型
4. 系统设计与实现

## 直播弹幕情感分析与高光检测系统

### 技术架构

- 前端：Bootstrap+Echarts
- 框架：Flask
- 数据处理与分析中用到的各类词典与模型数据：自己整理或生成

### 功能

- 自定义词典：支持用户上传自定义词典，与系统词典合并
- 弹幕单文本分析：输入一条弹幕，判断其情感倾向
- 数据预处理：上传弹幕原始数据，进行清洗、按时间聚合、提取情感特征
- 弹幕片段分析：上传处理后的弹幕片段数据，多个维度进行情感可视化，并检测高光片段

### 文件结构

- 系统界面与使用方法 [用户手册](https://github.com/zhou-xingxing/graduate_work/blob/master/直播弹幕情感分析与高光检测系统用户手册.pdf)

- 弹幕数据 ./data
- 各类词典文件 ./dict
- 各种实验代码 ./code  ./notebook
- flask系统代码 ./sentiment_system
