# coding=gbk
import codecs
import os
import os.path
import time
import math
import re

dict = {}  # 建立字典
filelist = {}  # 建立字典，键值是类名，值为文件名
MaxWordLen = 4  # 最大词语长度
WordSum = 0


def establish_dict(dictfile):
    '''输入字典文件的路径，创建字典列表'''
    fd = codecs.open(dictfile, "r", "gbk")
    texts = fd.readlines()  # 读取字典文件入list
    for word in texts:
        word = word[:-2]
        dict[word] = [0, 0, 0]  # 第一个值用来计算tf,第二个值用来计算idf,第三个值用来标识是否累加文档计数
    return dict


def findfiles(rootdir):
    '''输入文件路径，找寻路径下所有文件的文件名，并返回文件名列表'''
    for parent, dirnames, filenames in os.walk(rootdir):  # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for dirname in dirnames:
            # print dirname
            filelist[dirname] = []
            # print parent + "\\".decode("gbk") + dirname
            for sports, dirnames, filenames in os.walk(parent + "\\".decode("gbk") + dirname):
                for filename in filenames:
                    filelist[dirname].append(filename)
    return filelist


def ans(testword):
    '''最大反向匹配测试每个测试字符串中是否存在分词'''
    global WordSum
    for i in range(len(testword)):
        word = testword[i:]
        if word in dict:
            dict[word][0] += 1  # tf计数器加1
            WordSum += 1
            if dict[word][2] == 0:  # 如果文件累加允许
                dict[word][1] += 1  # idf计数器加1
                dict[word][2] = 1  # 此篇文档已加入文档计数。文档计数允许置1
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


def subword(filename):
    '''将指定文件分词'''
    fd = codecs.open(filename, "r", "gbk", "ignore")
    text = fd.readlines()
    for line in text:
        _subword(line, filename)
    for val in dict.values():  # 一篇文档分词完成，把文档累加允许置0
        val[2] = 0
    fd.close()


if __name__ == "__main__":
    begintime = time.time()
    dictfile = r"C:\Users\xiaoxiong\Desktop\test\dict.txt".decode("gbk")
    establish_dict(dictfile)
    rootdir = r"C:\Users\xiaoxiong\Desktop\test\体育分类训练文档".decode("gbk")
    findfiles(rootdir)
    # for file in filelist:
    #     print file, filelist[file]
    FileSum = 0  # 分词文档总数
    for file in filelist:
        # print file,filelist[file]
        for filename in filelist[file]:
            if not (not (filename[len(filename) - 8:] == "_seg.txt".decode("gbk")) and not (
                        filename[len(filename) - 8:] == "_pos.txt".decode("gbk")) and not (
                        filename[len(filename) - 8:] == "_out.txt".decode("gbk"))):
                pass
            else:
                FileSum += 1
                filename = rootdir + "\\".decode("gbk") + file + "\\".decode("gbk") + filename
                # print filename
                subword(filename)
    print "subword done!"
    resultfile = codecs.open(r"C:\Users\xiaoxiong\Desktop\test\result.txt".decode("gbk"), "w", "gbk", "ignore")
    newdict = codecs.open(r"C:\Users\xiaoxiong\Desktop\test\newdict.txt".decode("gbk"), "w", "gbk", "ignore")
    for key2 in dict:
        resultfile.write(key2)
        resultfile.write(" ".decode("gbk"))
        resultfile.write(math.log(FileSum / (dict[key2][1] + 1), 10) * (dict[key2][0] + 0.0) / WordSum) # 向结果文件中输出idf*tf值
        resultfile.write("\r\n".decode("gbk"))
        newdict.write(key2)
        newdict.write(" ".decode("gbk"))
        newdict.write(math.log(FileSum / (dict[key2][1] + 1), 10)) # 构造一个新的字典，形式：word idf
        newdict.write("\r\n".decode("gbk"))
    resultfile.close()
    endtime = time.time()
    print "%d" % int(endtime - begintime)