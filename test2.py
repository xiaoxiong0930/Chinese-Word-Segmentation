# coding=gbk
import codecs
import os
import os.path
import time
import math
import re

idfdict = {}  # �����ֵ�
MaxWordLen = 4  # �����ﳤ��
WordSum = 0  # ������
feature = {} # ѵ������������
correct = 0 # ��ȷ�ķ����ĵ���


def establish_dict(dictfile):
    '''�����ֵ��ļ���·���������ֵ��б�'''
    fd = codecs.open(dictfile, "r", "gbk")
    texts = fd.readlines()  # ��ȡ�ֵ��ļ���list
    for line in texts:
        li = re.findall(r"(.*?) (.*)\r\n".decode("gbk"), line, re.S)
        idf = float(li[0][1])
        word = li[0][0]
        idfdict[word] = [0, idf, 0.0]  # ��һ�������ǳ��ֵĴ�������һ��������idf,���һ��һ�������idf*tf
    fd.close()


def findfiles(rootdir):
    '''�����ļ�·������Ѱ·���������ļ����ļ������������ļ����б�'''
    filelist = {}  # �����ֵ䣬��ֵ��������ֵΪ�ļ���
    for parent, dirnames, filenames in os.walk(rootdir):  # �����������ֱ𷵻�1.��Ŀ¼ 2.�����ļ������֣�����·���� 3.�����ļ�����
        for dirname in dirnames:
            filelist[dirname] = []
            for sports, dirnames, filenames in os.walk(parent + "\\".decode("gbk") + dirname):
                for filename in filenames:
                    filelist[dirname].append(filename)
    return filelist


def ans(testword):
    '''�����ƥ�����ÿ�������ַ������Ƿ���ڷִ�'''
    global WordSum, idfdict
    for i in range(len(testword)):
        word = testword[i:]
        if word in idfdict:
            idfdict[word][0] += 1  # ��Ƶ��������1
            WordSum += 1
            break
    return len(testword) - i


def _subword(line, filename):
    '''��ָ���ַ����ִ�'''
    result = []
    line = re.sub("<.*?>".decode("gbk"), "".decode("gbk"), line)
    line = re.sub("<\.*?>".decode("gbk"), "".decode("gbk"), line)  # �����ı��е�html��ǩ
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
    '''��ָ���ļ��ִ�'''
    fd = codecs.open(filename, "r", "gbk", "ignore")
    text = fd.readlines()
    for line in text:
        _subword(line, filename)
    fd.close()


def es_feature():
    global WordSum, feature, idfdict
    rootdir = r"C:\Users\xiaoxiong\Desktop\test\��������ѵ���ĵ�".decode("gbk")
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
        for word in idfdict:  # ����idf*tfֵ
            idfdict[word][2] = (idfdict[word][0] + 0.0 / WordSum) * idfdict[word][1]
        static = sorted(idfdict.iteritems(), key=lambda d: d[1][2], reverse=True)  # ����
        num = 20
        feature[file] = []  # �洢ÿ�����������
        featurefile.write("#" + file + "\r\n".decode("gbk"))
        for i in range(num):  # �������20����
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
    tmp_feature = {}  # ÿ���ļ�������
    hit_class = {} # ���еķ���
    resultfile = r"C:\Users\xiaoxiong\Desktop\test\classify.txt".decode("gbk")
    fd = codecs.open(resultfile,"w","gbk")
    rootdir = r"C:\Users\xiaoxiong\Desktop\test\������������ĵ�".decode("gbk")
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
                for word in idfdict:  # ����idf*tfֵ
                    idfdict[word][2] = (idfdict[word][0] + 0.0 / WordSum) * idfdict[word][1]
                static = sorted(idfdict.iteritems(), key=lambda d: d[1][2], reverse=True)  # ����
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