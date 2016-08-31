# coding=gbk
import codecs
import os
import os.path
import time
import math
import re

dict = {}  # �����ֵ�
filelist = {}  # �����ֵ䣬��ֵ��������ֵΪ�ļ���
MaxWordLen = 4  # �����ﳤ��
WordSum = 0


def establish_dict(dictfile):
    '''�����ֵ��ļ���·���������ֵ��б�'''
    fd = codecs.open(dictfile, "r", "gbk")
    texts = fd.readlines()  # ��ȡ�ֵ��ļ���list
    for word in texts:
        word = word[:-2]
        dict[word] = [0, 0, 0]  # ��һ��ֵ��������tf,�ڶ���ֵ��������idf,������ֵ������ʶ�Ƿ��ۼ��ĵ�����
    return dict


def findfiles(rootdir):
    '''�����ļ�·������Ѱ·���������ļ����ļ������������ļ����б�'''
    for parent, dirnames, filenames in os.walk(rootdir):  # �����������ֱ𷵻�1.��Ŀ¼ 2.�����ļ������֣�����·���� 3.�����ļ�����
        for dirname in dirnames:
            # print dirname
            filelist[dirname] = []
            # print parent + "\\".decode("gbk") + dirname
            for sports, dirnames, filenames in os.walk(parent + "\\".decode("gbk") + dirname):
                for filename in filenames:
                    filelist[dirname].append(filename)
    return filelist


def ans(testword):
    '''�����ƥ�����ÿ�������ַ������Ƿ���ڷִ�'''
    global WordSum
    for i in range(len(testword)):
        word = testword[i:]
        if word in dict:
            dict[word][0] += 1  # tf��������1
            WordSum += 1
            if dict[word][2] == 0:  # ����ļ��ۼ�����
                dict[word][1] += 1  # idf��������1
                dict[word][2] = 1  # ��ƪ�ĵ��Ѽ����ĵ��������ĵ�����������1
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


def subword(filename):
    '''��ָ���ļ��ִ�'''
    fd = codecs.open(filename, "r", "gbk", "ignore")
    text = fd.readlines()
    for line in text:
        _subword(line, filename)
    for val in dict.values():  # һƪ�ĵ��ִ���ɣ����ĵ��ۼ�������0
        val[2] = 0
    fd.close()


if __name__ == "__main__":
    begintime = time.time()
    dictfile = r"C:\Users\xiaoxiong\Desktop\test\dict.txt".decode("gbk")
    establish_dict(dictfile)
    rootdir = r"C:\Users\xiaoxiong\Desktop\test\��������ѵ���ĵ�".decode("gbk")
    findfiles(rootdir)
    # for file in filelist:
    #     print file, filelist[file]
    FileSum = 0  # �ִ��ĵ�����
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
        resultfile.write(math.log(FileSum / (dict[key2][1] + 1), 10) * (dict[key2][0] + 0.0) / WordSum) # �����ļ������idf*tfֵ
        resultfile.write("\r\n".decode("gbk"))
        newdict.write(key2)
        newdict.write(" ".decode("gbk"))
        newdict.write(math.log(FileSum / (dict[key2][1] + 1), 10)) # ����һ���µ��ֵ䣬��ʽ��word idf
        newdict.write("\r\n".decode("gbk"))
    resultfile.close()
    endtime = time.time()
    print "%d" % int(endtime - begintime)