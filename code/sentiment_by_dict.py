# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 18:46:50 2020

@author: lenovo
"""

#基于词典的情感分析
import jieba
import os,time,csv
from pyltp import Segmentor
from data_cleaning import *
from langconv import *
import pandas as pd


# 加载自定义词典
jieba.load_userdict(r'../dict/self_dict.txt')


LTP_DATA_DIR = r'../ltp_data_v3.4.0/ltp_data_v3.4.0'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
segmentor = Segmentor()  # 初始化实例
segmentor.load_with_lexicon(cws_model_path, r"../dict/self_dict.txt")  # 加载模型，第二个参数是您的外部词典文件路径

pos_dict=pd.read_csv(r'../dict/self_positive_dict.txt',header=None)
pos_dict=pos_dict[0].tolist()

neg_dict=pd.read_csv(r'../dict/self_negative_dict.txt',header=None)
neg_dict=neg_dict[0].tolist()

not_dict=pd.read_csv(r'../dict/self_not.txt',header=None)
not_dict=not_dict[0].tolist()

with open("../dict/self_degree.txt",'r',encoding='utf-8') as f:    
    degree=eval(f.read()) #把字典转化为str 

degree_most=degree['most']
degree_more=degree['more']
degree_less=degree['less']
degree_least=degree['least']

print('正面情感词:',len(pos_dict))
print('负面情感词:',len(neg_dict))
print('否定词:',len(not_dict))
print('程度副词:',len(degree_most),len(degree_more),len(degree_less),len(degree_least))

#数据清洗
def danmu_clean(sentence):
    with open(r"../dict/dyemot.txt", 'r')as f:
        emot_dict = eval(f.read())
        
    sentence=symbol_replace(sentence)
    sentence=tradition2simple(sentence)
    sentence=sim_replace(sentence)
    sentence=emoji_replace(sentence)
    
    return sentence


#jieba分词
def jieba_word(sentence):
    seg_list = jieba.cut(sentence)
    seg_result = []
# 去多余空格
    for i in seg_list:
        if i==' ':
            continue
        else:
            seg_result.append(i)
    
    return seg_result

#ltp分词
def ltp_word(sentence):
    seg_result = segmentor.segment(sentence)
    return list(seg_result)


#计算情感得分    
def sentence_score(seg_result):
    pos_score=0
    neg_score=0
    
    for i in range(0,len(seg_result)):        
        if seg_result[i] in pos_dict:
#            print('pos:',seg_result[i])
            tmp=1
#            向前查1-2个词
            for j in [1,2]:
                if i-j<0:
                    break
#                有标点说明前后无联系，提前结束
                if seg_result[i-j]==',' or seg_result[i-j]=='.':
                    break
                else:
                    if seg_result[i-j] in not_dict:
                        tmp=tmp*-1
                        continue
                    elif seg_result[i-j] in degree_most:
                        tmp=tmp*1.75
                        continue
                    elif seg_result[i-j] in degree_more:
                        tmp=tmp*1.5
                        continue
                    elif seg_result[i-j] in degree_less:
                        tmp=tmp*0.75
                        continue
                    elif seg_result[i-j] in degree_least:
                        tmp=tmp*0.5
                        continue
            pos_score+=tmp
        elif seg_result[i] in neg_dict:
#            print('neg:',seg_result[i])
            tmp=1
#            向前查1-2个词
            for j in [1,2]:
                if i-j<0:
                    break
                if seg_result[i-j]==',' or seg_result[i-j]=='.':
                    break
                else:
                    if seg_result[i-j] in not_dict:
#                        负面词被否定词修饰视为无情感或略微正向
                        tmp=tmp*0
                        continue
                    elif seg_result[i-j] in degree_most:
                        tmp=tmp*1.75
                        continue
                    elif seg_result[i-j] in degree_more:
                        tmp=tmp*1.5
                        continue
                    elif seg_result[i-j] in degree_less:
                        tmp=tmp*0.75
                        continue
                    elif seg_result[i-j] in degree_least:
                        tmp=tmp*0.5
                        continue
            neg_score+=tmp
    
    score=pos_score-neg_score
#    print('score',score)
#    如果句子最后有叹号
    if  seg_result[-1]=='!':
        score*=1.5
    return score    
                           
                        
#输出单条弹幕情感分析结果                        
def sentiment_result(sentence):                

#    只有在测试单条弹幕时才需要清洗
    sentence=danmu_clean(sentence)
#    特殊处理两种情况
    if sentence=='???':
#        print('负面')
        jieba_res=-1
        ltp_res=-1
        return (jieba_res,ltp_res)  
#        return jieba_res
    if sentence=='!!!':
#        print('正面')
        jieba_res=1
        ltp_res=1
        return (jieba_res,ltp_res)  
#        return jieba_res
    if len(sentence)==0 or sentence==',' or sentence=='.':
#        print('中性')
        jieba_res=0
        ltp_res=0
        return (jieba_res,ltp_res) 
#        return jieba_res
    
    
    jieba_list=jieba_word(sentence)
    ltp_list=ltp_word(sentence)
#    
#    print('jieba_list:',jieba_list)
#    print('ltp_list:',ltp_list)
#    
    sentiment_jieba=sentence_score(jieba_list)
    sentiment_ltp=sentence_score(ltp_list)
    
    if sentiment_jieba>0:
        print('jieba:','socre',sentiment_jieba,'class','正面')
    elif sentiment_jieba<0:
        print('jieba:','socre',sentiment_jieba,'class','负面')
    else:
        print('jieba:','socre',sentiment_jieba,'class','中性')
        
    if sentiment_ltp>0:
        print('ltp:','socre',sentiment_ltp,'class','正面')
    elif sentiment_ltp<0:
        print('ltp:','socre',sentiment_ltp,'class','负面')
    else:
        print('ltp:','socre',sentiment_ltp,'class','中性')    
    
    if sentiment_jieba>0:
        jieba_res=1
    elif sentiment_jieba<0:
        jieba_res=-1
    else:
        jieba_res=0
        
    if sentiment_ltp>0:
        ltp_res=1
    elif sentiment_ltp<0:
        ltp_res=-1
    else:
        ltp_res=0
    
    return (jieba_res,ltp_res)    
#    return sentiment_jieba

#按时间段判断情感
def sentiment_fragment(danmu_list):
    sentiment_score_list=[]
    sentiment_pos_score=[]
    sentiment_neg_score=[]
    for i in danmu_list:
        score=sentiment_result(i)
        sentiment_score_list.append(score)
        if score>0:
            sentiment_pos_score.append(score)
        if score<0:
            sentiment_neg_score.append(score)
    num=len(sentiment_score_list)        
    avg=sum(sentiment_score_list)/num
#返回情感值累积和、平均值、正向和、负向和
#    return (sum(sentiment_score_list),avg,sum(sentiment_pos_score),sum(sentiment_neg_score))
#返回情感均值、正面情感均值、正面弹幕比、负面情感均值、负面弹幕比
    return  (avg,sum(sentiment_pos_score)/num,len(sentiment_pos_score)/num,sum(sentiment_neg_score)/num,len(sentiment_neg_score)/num)  



#❤️
#❤ 这两种红心不一样   
#sentence="完了 带尼玛节奏 满嘴跑火车 老干爹的两个大鹅 来了 赢了 萌神真的萌 就这 样的 太菜了"
#i=sentiment_result(sentence)
#print(i)
#    
#测试弹幕
def test_danmu():    
    test_data=pd.read_csv(r'../data/test300_result_verify.csv')
    print('测试数量：',len(test_data))
    jieba_flag=[]
    ltp_flag=[]
    start_time=time.clock()
    for index,row in test_data.iterrows():
        danmu=str(row['danmu'])
        jieba_res,ltp_res=sentiment_result(danmu)
    #    print(jieba_res,ltp_res)
        jieba_flag.append(jieba_res)
        ltp_flag.append(ltp_res)
    end_time=time.clock()
    print('测试用时：',end_time-start_time)
    test_data['jieba']=jieba_flag
    test_data['ltp']=ltp_flag
    test_data.to_csv(r'../data/new_test300_result_verify.csv',index=None)
    
test_danmu()    
#
#测试时间段弹幕
def test_danmu_frag():
#    运行36秒
    data=pd.read_csv(r'../code/frag_cleaned_test_room911_20000.csv')
    time_group=data.groupby('fragment')    
    time_frag=[]
#    score_frag=[]
    avg_frag=[]
    pos_avg_frag=[]
    pos_pro_frag=[]
#    pos_frag=[]
#    neg_frag=[]
    start_time=time.clock()
    for gn,gl in time_group:
#        以每组第一条弹幕时间为坐标值
        time_frag.append(gl['time'].tolist()[0])
        avg,pos_avg,pos_pro=sentiment_fragment(gl['content'].tolist())
        
        avg_frag.append(avg)
        pos_avg_frag.append(pos_avg)
        pos_pro_frag.append(pos_pro)
    end_time=time.clock()
    print('测试用时：',end_time-start_time)
    dic={'time_frag':time_frag,'avg_score':avg_frag,'pos_avg':pos_avg_frag,'pos_proportion':pos_pro_frag}
    senti_frag=pd.DataFrame(dic)
    senti_frag.to_csv(r'../code/new2_senti_frag_cleaned_test_room911_20000.csv',index=None)

#test_danmu_frag()

#为时间段加特征
def feature_danmu_frag():
#    170-180s
    data=pd.read_csv(r'../data/room36252/new_flagfeature_final_room36252danmu0318.csv') 
    avg_ls=[]
    pos_avg_ls=[]
    pos_prop_ls=[]
    neg_avg_ls=[]
    neg_prop_ls=[]
    start_time=time.clock()
    for index,row in data.iterrows():
#        print(row['danmu'],type(row['danmu']))
        avg,pos_avg,pos_prop,neg_avg,neg_prop=sentiment_fragment(eval(row['danmu']))
        
        avg_ls.append(avg)
        pos_avg_ls.append(pos_avg)
        pos_prop_ls.append(pos_prop)
        neg_avg_ls.append(neg_avg)
        neg_prop_ls.append(neg_prop)
    
    end_time=time.clock()
    print('测试用时：',end_time-start_time)
    data['avg_score']=avg_ls
    data['pos_avg_score']=pos_avg_ls
    data['pos_proportion']=pos_prop_ls
    data['neg_avg_score']=neg_avg_ls
    data['neg_proportion']=neg_prop_ls
    
    data.to_csv(r'../data/room36252/new_flagfeature_final_room36252danmu0318.csv',index=None)
    
    
    
        
#feature_danmu_frag()

#test_list=['哈哈哈', 'qg这么菜回去排位吧', '爱思指挥', '???', '5秒真男人的时代已经过去,在这个直播间就来#挑战666#', '哈哈哈', '啊啊啊', '666', '指挥问题太多了', '哈哈哈 舒服了', '爱思吧', '哈哈哈', '杀疯了', '爱思是指挥', 'qg都得连线指挥', '这...语音,带混响啊😂', '这个回音哈哈哈', '扣g现在怎么变得好菜呀?', '???', '爱思', '九年在hero明显1就是最菜的', '爱思指挥', 'fly不知道在干嘛', '给我死!', '现在qg的指挥是许诺吗?感觉有点懵,不知道该干嘛,很被动', '杀人', '那个是效应?', '???', '爱思指挥', '杀人杀人', '给我死', '爱思', '我凑', '啊啊啊', '诶嘛吓死我了', '这是爱思还是笑影啊', '给我杀人', '这是爱思呢声音不是笑影', '肥哲别看了学不会的', '哈哈哈', '回音真大', '爱思指挥', '主播不要逗', '爱思指挥的', '哈哈哈', '哈哈哈嘎', '给我死', '哈哈哈', '哈哈哈,给我死,哈哈哈', '哈哈哈', 'ag的指挥强太多了', '五个人的游戏 别怪来怪去了', '给我死哈哈哈', '让我死?', '哈哈哈', '爱思指挥', '我在#挑战666#中最好成绩是6.61秒,你能超越我吗?', '爱思吧', '还是爱思声音多', '给我死', '我勒个去', '哈哈哈', '这个声音感觉隔的好远哈哈哈', '这个语音 怎么这么搞笑', '给我死', '笑死', '杀人杀人', '哈哈哈', '???', '???', '给我死!', '哈哈哈', '哈哈哈', '爱思指挥的', '我看qg啥都缺,缺教练缺指挥缺辅助', '困了累了,就来一把紧张刺激的#挑战666#,一局提神醒脑,两局永不疲劳!', '爱思多一点', '爱思是主指挥', 'fly太惨了', '爱思', '哈哈哈', '哈哈哈', '爱思', '谁指挥', '哈哈哈', '哈哈哈', '哈哈哈', '给我死', '哈哈哈', '哈哈哈', '给我死哈哈哈', '哈哈哈', '哈哈哈', '哈哈哈', '很不错666啊', '哈哈哈', '杀人', '哈哈哈', '哈哈哈有种排位的感觉', '啊啊啊!～～', '哈哈哈', '哈哈哈', '哈哈哈', '哪个是笑影', '哈哈哈这个表情', '哈哈哈4', '哈哈哈', '给我杀人', '笑死我了', '哈哈哈', '给我死', '哈哈哈', '收了?', '许诺长得也还可以', '鸭诺', '哈哈哈啊哈哈哈', '哈哈哈', '隔着开黑呢', '哈哈哈', '哈哈哈', '杀人杀人', '太狠了', '主播是真的顶', '给👴🏻死!✌🏻', '哈哈哈', '啊', '43伤害', '江西老表', '标题错了吧', '好可爱啊啊啊', '杀人杀人', '杀人就完了', '顶级射手一诺', '杀人杀人', '刺痛不配赢', 'nice?', '一诺：杀人杀人哈哈哈', '一诺!', '哈哈哈', '开火开火哈哈哈', '哈哈哈', '哈哈哈', '太强了', '给我死', '哈哈哈', '哈哈哈', '哈哈哈', '啊啊啊杀疯了哈哈哈', '哈哈哈', '哈哈哈  奇奇怪怪的叫声', '哈哈哈', '杀人,给我杀人', '哈哈哈', '哈哈哈', '艾斯', '哈哈哈', '嗷嗷!', '哈哈哈', '爽', '说白了,qg的指挥就是不行', '给我死!杀人!', '哈哈哈', '666', '给我死', '这也太欢乐了', '哈哈哈', '哈哈哈', '哈哈哈', '一诺nb', '这个语音回放声音好小', '给我死', '哈哈哈', '主播是真的顶', '哈哈哈开黑呢', '42...', '猛男怒吼', '好稳', '我透', '舒服', '被虐哭了,请求大佬支援#挑战666#', '42.5太恐怖了', '杀人杀人', '他们在哪里打的比赛', '哈哈哈', 'mua', '听不清', '预感qg官博沦陷了', '哈哈哈', '爱思', '一诺棒', '一脸懵逼哈哈哈', '一诺个渣男', '哈哈哈', '一诺', '...', '乱', 'qg输在名字', '哈哈哈', '哈哈哈', '哈哈哈', '怎么这么搞笑', '太狠了', '听不清是谁...', '哈哈哈', '6哥说的让我死?', '好可爱', '哈哈哈,给我死!哈哈哈', 'ag打破的魔咒还少吗?', '哈哈哈一诺', '奈斯', '被虐哭了,请求大佬支援#挑战666#', '我一诺弟弟', '刺痛还得打野还得射手只有一个刺痛', '太狂了', '先杀人', '哈哈哈', '这个眼神', '3／0带走', '给我死', '哈哈哈', '笑死我了', '亲亲一诺', '爱思指挥', '啊啊啊', '给我死哈哈哈,', '给我死', '杀人杀人哈哈哈', '哈哈哈', '像网吧', '交流有点乱', '徐必成', '笑死我了哈哈哈', '给我杀', '杀人杀人', 'yeee哈哈哈', '666', '杀', '哦哦', '给我死', '怎么没有头', '诺崽!', '我觉得应该打萌芽的', '哈哈哈啊哈哈哈', '猛男赛后语音哈哈哈', '一诺挺厉害的啊', '爱思指挥', '我真的听到了开我', '哈哈哈', '哈哈哈', '一诺江西的啊', '爱思指挥', '哈哈哈', '杀人', '爱思主指挥', '瞪!', '笑死', '亲亲', '打排位呢!', '啊啊啊诺崽', '一诺还是顶啊', '给我杀人', '漂亮', '爱思', '太骚了', '杀人杀人', '给我死', '是的是的', '月光?', '没听清楚', '好可爱', '淦', '一诺宝贝', '猛男', '打qg盯住fly不让他进场就可以了', '哈哈哈', '双指挥', '老干爹乱杀', '就听到了杀人', 'bp为啥要放鲁班大师?还ban张飞', '一诺牛壁', '这个输出...', '一诺牛逼', '笑死我了', '???', '七年', '哈哈哈怎么这么好笑', '给我死给我死给我死', '果然是杀人杀人', '哈哈哈', '给我死', '还有一诺', '江西仔', '嗯嗯!', '杀人杀人,随便搞', '杀人!', '有笑影的声音', '给我死,哈哈哈', '一诺江西人吗', '哈哈哈好可爱', '好可爱', '给爷死哈哈哈', '七年', '七年', '爱思多一点', '笑影负责喊杀人', '被虐哭了,请求大佬支援#挑战666#', '一诺', '给👴死', '哈哈哈', '好雄浑', '双指挥稳的一批', '哈哈哈', '爱思主指挥', '主要是爱思', '太逗了哈哈哈', '笑影声音好像不是这样的啊', '嘻嘻', '一诺弟弟好可爱', '随便g', '哈哈哈', ':笑影没说话', '亲亲一诺', '我听到了一诺我要杀', '一诺的杀人', '一个陌生男子的有磁性的声音', '笑的好傻啊', '杀人杀人杀人', '杀人杀人', '为啥不给一诺出个fmvp', '杀他奥利给', '给我杀人', '第二把谁mvp', '哈哈哈', '和打排位没啥区别哈哈哈', '就爱思吧', '七年', '没有阑尾的男人43', '啊～给我死～', '爱思声音比较大', '不是一诺', '一诺杀人杀人', '???', '小眼睛单眼皮太丑了', '主播是真的顶', '杀杀杀', 'ag牛逼', '杀人!', '笑影声音很重', '赵云看住了关羽那是哪个猛男在吼哈哈哈', '6.6', '可爱', '不是一诺', '乱七八糟...', '你给我死,像打狗一样', '给我死!哈哈哈', '21st是什么', '不是一诺', '爱思七年吧', '不是一诺', '爱思主指挥', '咦额额鹅鹅鹅鹅鹅鹅鹅', '那个腿', '哪个是笑影的声音', '笑影少', '6.6说话没?', '拖米又躺下了', '亲亲一诺', '哈哈哈', '哈哈哈', '不是一诺叭', '7年', '小影', '七年吧', '感觉他们声音好搞笑', '射手出身不打射手就醉了', '终极高手出来的.ag用了两个 都牛逼', '我在#挑战666#的最好成绩是6.75秒,点击弹幕立即挑战〉〉', '那是七年', '猛男怒吼', '杀杀杀', '我怎么感觉是月光', '5秒真男人的时代已经过去,在这个直播间就来#挑战666#', '杀人杀人', '还能这么听', '一诺的杀人', '杀人', '就那个猛男怒吼', '全程杀杀杀', '❤❤❤', 'h', '大鹅和vg谁厉害', '是一诺', '江西仔,哈哈哈', '哈哈哈', '一诺是公鸭', '八秒大招八秒大招', '?...听个锤子', '爱思', '???', '干!', '是有笑影的声音', '雄浑的声音', '大点声音', '不是', '死', '主指挥爱思', '口罩', '我听成项羽的声音了?', '双指挥nb', '一诺一直说给我杀人', '项羽?', '郭老师  求求你拯救一下qg吧[打call]', '是爱思啦', '七年你也没听过吧', '老干爹乱杀', '7年', '不是一诺', '杀人杀人杀人', '不像一诺的', '可爱', '给我死', '七年的', '爱思是指挥', '给我死', '一诺还好', '唉,太失望了', '笑影张良说几秒大招', '一诺的声音就是 一直破音', '七年呢', '自带混响', '一诺跟艾斯指挥', '灵儿这个腿可以', '拖米?', '一诺说的杀人', '爱思指挥', '一诺说杀人', '一诺就说了杀人', '现在qg的指挥是许诺还是末将?感觉有点懵,不知道该干嘛,很被动', '一诺吃火锅嗓子变粗了', '啊哈哈哈,好可爱', '不是一诺', '一诺江西哪的?', '哈哈哈', '一诺烟嗓哈哈哈', '不是', '腿来了', '七年', '不是一诺', '这谁顶得住啊', '拖米笑死人', '不是一诺', '邪魅一笑', '先杀人', '一诺声音哪有这么粗你们说啥呢', '杀人!', '七年真工具人', '不是', '怎么没上冠军阵容啊?', '我感觉fly好久没打了有点不在状态', '死', 'qg现在谁指挥', '先杀人杀人', '一诺：杀人杀人', '七年', '刺痛喜哈哈哈欢玩最贵的皮肤', '不是一诺', '这啥啊', '3／0带走', '好', '一诺 @aunfrozen：第二把谁mvp', '七年?', '今天状态不错呀', '爽,哈哈哈.', '真:毒奶', '又有椅子了?', '七年', '666', '记得擦嘴', '一诺奶奶的', '恶!', '口罩包不住托米的下巴', '不是一诺', '不许', '不好', '不是一诺声音', '不是一诺弟弟', '一诺弟弟：给我!死', '666', '爱思主指挥', '6+1=7', '6.6', '这样打的时候教练可以在旁边支招嘛', '666', '七年 七年话挺多的', '我也是', '笑影声音很细的,应该是七年', '不允许', '不是一诺', '七年的', '上次没770真的真的qg拿不了冠军', '不行', '咋不给一诺出一个fmvp皮肤', '好', '给我死', '不是一诺', '不行', '猪哼头发多了?', '就这三个人', '不允许', '唉', '拖米和灵儿换了个位置', '之前还不是说ag万年老二', '666', '采访说了爱思指挥', '666', '666', '困了累了,就来一把紧张刺激的#挑战666#,一局提神醒脑,两局永不疲劳!', 'kjfjds', '说杀人的是一诺', '只听到了杀人杀人', '杀人肯定是一诺喊的', '不许', '不是一诺', '666', '结算', '不行', '666', '去吧去吧', '666', '一诺就只在喊杀人', '杀杀杀,给我死', '不行', '一诺说杀人', '一诺声音的辨识度挺好的', '666', 'c', '哈哈哈', '666', '不好', '不是一诺', '666', '是不是6哥说的让我死?', '666', '666', '一诺是公鸭嗓!', '不好', '666', '冲冲冲', '不是一诺', '哈哈哈']
#
#
#avg,pos_avg,pos_pro,neg_avg,neg_pos=sentiment_fragment(test_list)
#print(avg,pos_avg,pos_pro,neg_avg,neg_pos)    


segmentor.release()    
    