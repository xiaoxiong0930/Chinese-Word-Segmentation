# coding=gbk
import codecs
import os
import os.path
import time
import math
import re

idfdict = {}  # 建立字典
MaxWordLen = 4  # 最大词语长度
WordSum = 0  # 词总数
feature = {} # 训练集的特征库
correct = 0 # 正确的分类文档数


def establish_dict(dictfile):
    '''输入字典文件的路径，创建字典列表'''
    fd = codecs.open(dictfile, "r", "gbk")
    texts = fd.readlines()  # 读取字典文件入list
    for line in texts:
        li = re.findall(r"(.*?) (.*)\r\n".decode("gbk"), line, re.S)
        idf = float(li[0][1])
        word = li[0][0]
        idfdict[word] = [0, idf, 0.0]  # 第一个参数是出现的次数，后一个参数是idf,最后一首一个来存放idf*tf
    fd.close()


def findfiles(rootdir):
    '''输入文件路径，找寻路径下所有文件的文件名，并返回文件名列表'''
    filelist = {}  # 建立字典，键值是类名，值为文件名
    for parent, dirnames, filenames in os.walk(rootdir):  # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for dirname in dirnames:
            filelist[dirname] = []
            for sports, dirnames, filenames in os.walk(parent + "\\".decode("gbk") + dirname):
                for filename in filenames:
                    filelist[dirname].append(filename)
    return filelist


def ans(testword):
    '''最大反向匹配测试每个测试字符串中是否存在分词'''
    global WordSum, idfdict
    for i in range(len(testword)):
        word = testword[i:]
        if word in idfdict:
            idfdict[word][0] += 1  # 词频计数器加1
            WordSum += 1
            break
    return len(testword) - i


def _subword(line, filename):
    '''将指定字符串分词'''
    result = []
    line = re.sub("<.*?>".decode("gbk"), "".decode("gbk"), line)
    line = re.sub("<\.*?>".decode("gbk"), "".decode("gbk"), line)  # 过滤文本中的html标签
    while len(line) != 0:
        if len(line) > MaxWordLen:
            testword = line[len(line) - MaxWordLen:]
        else:
            testword = line
        word_len = ans(testword)
        result.insert(0, line[len(line) - word_len:])
        line = line[:len(line) - word_len]
    fd = codecs.open(filename[:len(filename) - 4] + "_out.txt".decode("gbk"), "a", "gbk")
    for i in result:
        fd.write(i)
        fd.write(" ".decode("gbk"))
    fd.write("\r\n".decode("gbk"))
    fd.close()


def subword(filename):
    '''将指定文件分词'''
    fd = codecs.open(filename, "r", "gbk", "ignore")
    text = fd.readlines()
    for line in text:
        _subword(line, filename)
    fd.close()


def es_feature():
    global WordSum, feature, idfdict
    rootdir = r"C:\Users\xiaoxiong\Desktop\test\体育分类训练文档".decode("gbk")
    filelist = findfiles(rootdir)
    featurefile = codecs.open(r"C:\Users\xiaoxiong\Desktop\test\feature.txt", "w", "gbk", "ignore")
    for file in filelist:
        for filename in filelist[file]:
            if not (not (filename[len(filename) - 8:] == "_seg.txt".decode("gbk")) and not (
                        filename[len(filename) - 8:] == "_pos.txt".decode("gbk")) and not (
                        filename[len(filename) - 8:] == "_out.txt".decode("gbk"))):
                pass
            else:
                filename = rootdir + "\\".decode("gbk") + file + "\\".decode("gbk") + filename
                subword(filename)
        for word in idfdict:  # 计算idf*tf值
            idfdict[word][2] = (idfdict[word][0] + 0.0 / WordSum) * idfdict[word][1]
        static = sorted(idfdict.iteritems(), key=lambda d: d[1][2], reverse=True)  # 排序
        num = 20
        feature[file] = []  # 存储每个类的特征词
        featurefile.write("#" + file + "\r\n".decode("gbk"))
        for i in range(num):  # 输出最大的20个词
            featurefile.write(static[i][0])
            featurefile.write("\r\n".decode("gbk"))
            feature[file].append(static[i][0])
        WordSum = 0
        for word in idfdict:
            idfdict[word][0] = 0
            idfdict[word][2] = 0
    featurefile.close()


def classify():
    global WordSum, feature, idfdict, correct
    tmp_feature = {}  # 每个文件的特征
    hit_class = {} # 命中的分类
    resultfile = r"C:\Users\xiaoxiong\Desktop\test\classify.txt".decode("gbk")
    fd = codecs.open(resultfile,"w","gbk")
    rootdir = r"C:\Users\xiaoxiong\Desktop\test\体育分类测试文档".decode("gbk")
    filelist = findfiles(rootdir)
    for file in filelist:
        for filename in filelist[file]:
            if not (not (filename[len(filename) - 8:] == "_seg.txt".decode("gbk")) and not (
                        filename[len(filename) - 8:] == "_pos.txt".decode("gbk")) and not (
                        filename[len(filename) - 8:] == "_out.txt".decode("gbk"))):
                pass
            else:
                filename = rootdir + "\\".decode("gbk") + file + "\\".decode("gbk") + filename
                subword(filename)
                for word in idfdict:  # 计算idf*tf值
                    idfdict[word][2] = (idfdict[word][0] + 0.0 / WordSum) * idfdict[word][1]
                static = sorted(idfdict.iteritems(), key=lambda d: d[1][2], reverse=True)  # 排序
                num = 20
                tmp_feature[filename] = []
                for i in range(num):
                    tmp_feature[filename].append(static[i][0])
                for lei in feature:
                    hit = 0
                    for one in tmp_feature[filename]:
                        if one in feature[lei]:
                            hit += 1
                    hit_class[lei] = hit
                    # print lei,hit
                fd.write(filename)
                fd.write(" ".decode("gbk"))
                top = sorted(hit_class.iteritems(), key=lambda d: d[1], reverse=True)[0][0]
                fd.write(top)
                fd.write("\r\n".decode("gbk"))
                for word in idfdict:
                    idfdict[word][0] = idfdict[word][2] = 0
    fd.close()



if __name__ == "__main__":
    begintime = time.time()
    dictfile = r"C:\Users\xiaoxiong\Desktop\test\newdict.txt".decode("gbk")
    establish_dict(dictfile)
    es_feature()
    classify()
    endtime = time.time()
    print "%d" % int(endtime - begintime)
