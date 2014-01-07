from numpy import *

def loadDataSet():
    postingList = [['my', 'dog', 'has', 'flea', 'problems', 'help', 'please'],
                   ['maybe', 'not', 'take', 'him', 'to', 'dog', 'park', 'stupid'],
                   ['my', 'dalmation', 'is', 'so', 'cute', 'I', 'love', 'him'],
                   ['stop', 'posting', 'stupid', 'worthless', 'garbage'],
                   ['mr', 'licks', 'ate', 'my', 'steak', 'how', 'to', 'stop', 'him'],
                   ['quit', 'buying', 'worthless', 'dog', 'food', 'stupid']]
    classVec = [0,1,0,1,0,1]
    return postingList, classVec

def creatVocabList(dataSet):
    vocabaSet = set([])
    for document in dataSet:
        vocabaSet = vocabaSet | set(document)
    return list(vocabaSet)

def setOfWords2Vec(vocabList, inputSet):
    returnVec = [0]*len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] = 1
        else:
            print 'the word: %s is not in my vocabulary!' % word
    return returnVec

def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    pAbusive = sum(trainCategory)/float(numTrainDocs)
    p0Num = ones(numWords)
    p1Num = ones(numWords)
    p0Denom = numWords
    p1Denom = numWords
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Denom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    p1Vect = log(p1Num/p1Denom)
    p0Vect = log(p0Num/p0Denom)
    return p0Vect, p1Vect, pAbusive

def classifyNB(vec2Classify, p0Vec, p1Vec, pClass1):
    p1 = sum(vec2Classify * p1Vec) + log(pClass1)
    p0 = sum(vec2Classify * p0Vec) + log(1.0 - pClass1)
    if p1 > p0:
        return 1
    else:
        return 0

def testingNB():
    listOPosts, listClasses = loadDataSet()
    myVocablist = creatVocabList(listOPosts)
    trainMat = []
    for postinDoc in listOPosts:
        trainMat.append(bagOfWords2Vec(myVocablist, postinDoc))
    poV,p1V,pAb = trainNB0(array(trainMat), array(listClasses))
    testEntry = ['love', 'my', 'dalmation']
    thisDoc = array(bagOfWords2Vec(myVocablist, testEntry))
    print testEntry, 'classified as: ', classifyNB(thisDoc, poV, p1V, pAb)
    testEntry = ['stupid', 'garbage']
    thisDoc = array(bagOfWords2Vec(myVocablist, testEntry))
    print testEntry, 'classified as: ', classifyNB(thisDoc, poV, p1V, pAb)

def bagOfWords2Vec(vocabList, inputSet):
    returnVec = [0]*len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] += 1
##        else:
##            print 'the word: %s is not in my vocabulary!' % word
    return returnVec

def textParse(bigString):
    import re
    listOfTokens = re.split(r'\W*', bigString)
    return [tok.lower() for tok in listOfTokens if len(tok) > 2]

def spamTest():
    docList = []
    classList = []
    fullText = []
    for i in range(1,26):
        wordList = textParse(open('email/spam/%d/txt' % i).read())
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(1)
        wordList = textParse(open('email/ham/%d/txt' % i).read())
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)
    vocabList = creatVocabList(docList)
    trainingSet = range(50)
    testSet = []
    for i in range(10):
        randIndex = int(random.uniform(0, len(trainingSet)))
        testSet.append(trainingSet[randIndex])
        del(trainingSet[randIndex])
    trainMat = []
    trainClasses = []
    for docIndex in trainingSet:
        trainMat.append(bagOfWords2Vec(vocabList, docList[docIndex]))
        trainClasses.append(classList[docIndex])
    p0V,p1V,pSpam = trainNB0(array(trainMat), array(trainClasses))
    errorCount = 0
    for docIndex in testSet:
        wordVector = bagOfWords2Vec(vocabList, docList[docIndex])
        if classifyNB(array(wordVector), p0V,p1V,pSpam) != classList[docIndex]:
            errorCount += 1
    print 'the error rate is: ',float(errorCount)/len(testSet)

def calcMostFreq(vocabList, fullText):
    import operator
    freDict = {}
    for token in vocabList:
        freDict[token] = fullText.count(token)
    sortedFreq = sorted(freDict.items(), key = operator.itemgetter(1), reverse = True)
    return sortedFreq[:30]

def localWords(feed1, feed0):
    import feedparser
    docList = []
    classList = []
    fullText = []
    minLen = min(len(feed1['entries']), len(feed0['entries']))
    for i in range(minLen):
        wordList = textParse(feed1['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(1)
        wordList = textParse(feed0['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)
    vocabList = creatVocabList(docList)
    top30Words = calcMostFreq(vocabList, fullText)
    for pairW in top30Words:
        if pairW[0] in vocabList:
            vocabList.remove(pairW[0])
    trainingSet = range(2*minLen)
    testSet = []
    for i in range(20):
        randIndex = int(random.uniform(0, len(trainingSet)))
        testSet.append(trainingSet[randIndex])
        del(trainingSet[randIndex])
    trainMat = []
    trainClasses = []
    for docIndex in trainingSet:
        trainMat.append(bagOfWords2Vec(vocabList, docList[docIndex]))
        trainClasses.append(classList[docIndex])
    p0V,p1V,pSpam = trainNB0(array(trainMat), array(trainClasses))
    errorCount = 0
    for docIndex in testSet:
        wordVector = bagOfWords2Vec(vocabList, docList[docIndex])
        if classifyNB(array(wordVector), p0V,p1V,pSpam) != classList[docIndex]:
            errorCount += 1
    print 'the error rate is: ',float(errorCount)/len(testSet)
    return vocabList, p0V, p1V

def getTopWords(ny, sf):
    import operator
    vocabList, p0V, p1V = localWords(ny,sf)
    topNY = []
    topSF = []
    for i in range(len(p0V)):
        if p0V[i] > -6.0:
            topSF.append((vocabList[i], p0V[i]))
        if p1V[i] > -6.0:
            topNY.append((vocabList[i], p1V[i]))
    sortedSF = sorted(topSF, key = lambda pair: pair[1], reverse = True)
    print 'SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**'
    for item in sortedSF:
        print item[0]
    sortedNY = sorted(topNY, key = lambda pair: pair[1], reverse = True)
    print 'NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**'
    for item in sortedNY:
        print item[0]   
if __name__ == '__main__':
    testingNB()
    import feedparser
    ny = '''This XML file does not appear to have any style information associated with it. The document tree is shown below.
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:ev="http://purl.org/rss/1.0/modules/event/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:syn="http://purl.org/rss/1.0/modules/syndication/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:admin="http://webns.net/mvcb/">
<channel rdf:about="http://newyork.craigslist.org/stp/index.rss">
<title>craigslist | strictly platonic in new york city</title>
<link>http://newyork.craigslist.org/stp/</link>
<description/>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:publisher>robot@craigslist.org</dc:publisher>
<dc:creator>robot@craigslist.org</dc:creator>
<dc:source>http://newyork.craigslist.org/stp/index.rss</dc:source>
<dc:title>craigslist | strictly platonic in new york city</dc:title>
<dc:type>Collection</dc:type>
<syn:updateBase>2013-09-29T00:09:54-07:00</syn:updateBase>
<syn:updateFrequency>1</syn:updateFrequency>
<syn:updatePeriod>hourly</syn:updatePeriod>
<items>
<rdf:Seq>
<rdf:li rdf:resource="http://newyork.craigslist.org/brx/stp/4083238166.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097927028.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4097902727.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/lgi/stp/4097956181.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097942236.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4097951603.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097948980.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4097948892.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097935334.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/lgi/stp/4097943911.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4069938234.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4090832553.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4097926344.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4074378104.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4035424459.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4059123346.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4061957471.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4088069548.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4065282223.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4055385500.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4042257658.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4042259183.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4090618807.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097920683.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4051708249.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4042445199.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097912396.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4082521774.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097871553.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4068441305.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/lgi/stp/4097903254.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097896550.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097885310.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4097892425.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097887347.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097861650.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097775654.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097875340.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/wch/stp/4063711708.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4083802099.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097869871.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4076859453.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4081044938.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4097863816.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/lgi/stp/4097862819.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4044872381.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4073164759.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4049545194.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4078843288.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097838597.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brx/stp/4097830100.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4097831609.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/stn/stp/4097743615.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4054937717.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/jsy/stp/4078570011.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4097828730.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4048511085.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4079821205.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4061893789.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097814343.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4084583581.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brx/stp/4097805854.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097801172.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097798803.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4097798356.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097796939.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097782042.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4074861712.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4084577110.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097789807.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097767615.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097777566.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097766057.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4097769637.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4078679747.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/jsy/stp/4097623833.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097762249.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/lgi/stp/4097759245.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097745445.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4088696318.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4097728790.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/lgi/stp/4097729094.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4087074358.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097708945.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097672367.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4079253615.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097697732.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097711153.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brx/stp/4097709270.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/jsy/stp/4097708015.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4097706709.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097705196.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/que/stp/4097690389.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097647576.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097666073.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4075666006.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097560230.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4097688614.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/mnh/stp/4097634090.html"/>
<rdf:li rdf:resource="http://newyork.craigslist.org/brk/stp/4097681155.html"/>
</rdf:Seq>
</items>
</channel>
<item rdf:about="http://newyork.craigslist.org/brx/stp/4083238166.html">
<title>
<![CDATA[
Talk to the sad tipsy guy (AIM:nomnomnomieatcrayons) - m4w (Bronx/Westchester/Purgatory) 32yr
]]>
</title>
<link>
http://newyork.craigslist.org/brx/stp/4083238166.html
</link>
<description>
<![CDATA[
AIM:nomnomnomieatcrayons Well, there's Craigslist and there's sanity. They're parallel dimensions that never meet. I'm no exception. I'm also amazingly coherent and lucid with some rum in me. I'm a sad person, and I don't like what I've become. I'm l [...]
]]>
</description>
<dc:date>2013-09-21T23:27:35-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brx/stp/4083238166.html
</dc:source>
<dc:title>
<![CDATA[
Talk to the sad tipsy guy (AIM:nomnomnomieatcrayons) - m4w (Bronx/Westchester/Purgatory) 32yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-21T23:27:35-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097927028.html">
<title>
<![CDATA[
i just wanna feel u up, squeeze ur tits. finger u n smell ur pussy - m4w (Upper East Side) 28yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097927028.html
</link>
<description>
<![CDATA[
horny white spanish guy here for n e women who will give it up without being a bitch Im not gonna pay u or ask u to be my girlfriend Ill hit it with a condom if the pussy is good n if ur ass dont smell like shit Shave ur fuckin legs n armpits if u [...]
]]>
</description>
<dc:date>2013-09-28T22:34:24-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097927028.html
</dc:source>
<dc:title>
<![CDATA[
i just wanna feel u up, squeeze ur tits. finger u n smell ur pussy - m4w (Upper East Side) 28yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:34:24-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4097902727.html">
<title>
<![CDATA[
looking for a really good massage - w4m (brooklyn) 27yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4097902727.html
</link>
<description>
<![CDATA[
hi i'm looking for a black male who really likes to give massages i'm from Brooklyn i'm 420 friendly...so please be too I like a man who is sweet, funny, caring, can hold a conversation ages 22-38...and please be able to host I have some green a [...]
]]>
</description>
<dc:date>2013-09-28T21:58:45-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4097902727.html
</dc:source>
<dc:title>
<![CDATA[
looking for a really good massage - w4m (brooklyn) 27yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:58:45-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/lgi/stp/4097956181.html">
<title>
<![CDATA[
i want meet an older woman - m4w (hicksville, levittown, long island) 23yr
]]>
</title>
<link>
http://newyork.craigslist.org/lgi/stp/4097956181.html
</link>
<description>
<![CDATA[
i need to meet a older woman that knows what she wants... lets flirt around and get to kno each other, but at the end of the day we just want funn. if having a younger man around is just something you need, let me kno
]]>
</description>
<dc:date>2013-09-28T23:24:17-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/lgi/stp/4097956181.html
</dc:source>
<dc:title>
<![CDATA[
i want meet an older woman - m4w (hicksville, levittown, long island) 23yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:24:17-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097942236.html">
<title>
<![CDATA[ Plumbing Question/Assistance - w4m (Midtown East) ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097942236.html
</link>
<description>
<![CDATA[
Firstly, I should be clear that this ad was placed under platonic, because I'm seeking someone warm, respectable, considerate and kind to assist with a basic plumbing question/fix. I'm not exactly handy would be an understatement, but I've discov [...]
]]>
</description>
<dc:date>2013-09-28T22:59:19-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097942236.html
</dc:source>
<dc:title>
<![CDATA[ Plumbing Question/Assistance - w4m (Midtown East) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:59:19-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4097951603.html">
<title>
<![CDATA[ dont be good be great - m4w 29yr ]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4097951603.html
</link>
<description>
<![CDATA[
Just chillen at work looking for up coming basketball leagues. Hit me up u know of any.
]]>
</description>
<dc:date>2013-09-28T23:15:55-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4097951603.html
</dc:source>
<dc:title>
<![CDATA[ dont be good be great - m4w 29yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:15:55-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097948980.html">
<title>
<![CDATA[
I Love NYC Top Rated Zagat Restaurants and the Theater - w4w (Midtown) 64yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097948980.html
</link>
<description>
<![CDATA[
Young at heart, physically fit, middle-aged woman who is upbeat, happy, fun-loving, and fair-minded describes me well. I am a well-educated professional seeking a new platonic friendship with a female who can join me on a Saturday evening at a highly [...]
]]>
</description>
<dc:date>2013-09-28T23:11:02-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097948980.html
</dc:source>
<dc:title>
<![CDATA[
I Love NYC Top Rated Zagat Restaurants and the Theater - w4w (Midtown) 64yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:11:02-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4097948892.html">
<title>
<![CDATA[ looking to text - m4w (nyc) 40yr ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4097948892.html
</link>
<description>
<![CDATA[
Bored and can't sleep. Looking for somebody to text chat with. My number is 347 533 2034
]]>
</description>
<dc:date>2013-09-28T23:10:52-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4097948892.html
</dc:source>
<dc:title>
<![CDATA[ looking to text - m4w (nyc) 40yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:10:52-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097935334.html">
<title>
<![CDATA[
biker looking for a friend - m4w (Upper West Side) 24yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097935334.html
</link>
<description>
<![CDATA[
Im a chubby dude who loves metal tattoos piercings and motorcycles lol Just looking for a female friend who may share the same interest...
]]>
</description>
<dc:date>2013-09-28T22:47:34-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097935334.html
</dc:source>
<dc:title>
<![CDATA[
biker looking for a friend - m4w (Upper West Side) 24yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:47:34-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/lgi/stp/4097943911.html">
<title>
<![CDATA[
I Love NYC Top Rated Zagat Restaurants and the Theater - w4w (North Shore - Nassau County-Long Island ) 65yr
]]>
</title>
<link>
http://newyork.craigslist.org/lgi/stp/4097943911.html
</link>
<description>
<![CDATA[
Young at heart, physically fit, middle-aged woman who is upbeat, happy, fun-loving, and fair-minded describes me well. I am a well-educated professional seeking a new platonic friendship with a female who can join me on a Saturday evening at a highly [...]
]]>
</description>
<dc:date>2013-09-28T23:02:05-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/lgi/stp/4097943911.html
</dc:source>
<dc:title>
<![CDATA[
I Love NYC Top Rated Zagat Restaurants and the Theater - w4w (North Shore - Nassau County-Long Island ) 65yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:02:05-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4069938234.html">
<title>
<![CDATA[ Frum JUST chat with frum married - m4w ]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4069938234.html
</link>
<description>
<![CDATA[
I don't want to start talking about hooking up or anything of the sort. I just wanna chat with a frum married women about anything really maybe make a SECRET friend. Very good looking guy over here 6" clean shaven handsome. Don't email me any of yo [...]
]]>
</description>
<dc:date>2013-09-15T17:31:03-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4069938234.html
</dc:source>
<dc:title>
<![CDATA[ Frum JUST chat with frum married - m4w ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-15T17:31:03-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4090832553.html">
<title>
<![CDATA[
european american jewish guy. bi. looking for local Jews for friends - m4m (Astoria Queens) 28yr
]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4090832553.html
</link>
<description>
<![CDATA[
European American Jewish guy, bi, living in Astoria. I'm a high school teacher. Looking to meet other Jewish guys as friends. I have plenty of straight friends but am hoping to meet a good guy who isn't straight. Hoping that with time to grow to care [...]
]]>
</description>
<dc:date>2013-09-25T12:43:27-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4090832553.html
</dc:source>
<dc:title>
<![CDATA[
european american jewish guy. bi. looking for local Jews for friends - m4m (Astoria Queens) 28yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-25T12:43:27-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4097926344.html">
<title>
<![CDATA[
i like to share my 2 badroom apt with you for $149 - m4w 49yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4097926344.html
</link>
<description>
<![CDATA[
i have a 2 badroom apartment in south slope and i'm willing to share with any girl with open mind and will to make in the big city
]]>
</description>
<dc:date>2013-09-28T22:33:24-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4097926344.html
</dc:source>
<dc:title>
<![CDATA[
i like to share my 2 badroom apt with you for $149 - m4w 49yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:33:24-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4074378104.html">
<title>
<![CDATA[
Cool dude for cool friends - m4m (Bedstuy / Bedford) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4074378104.html
</link>
<description>
<![CDATA[
Cool guy looking for friends. Little shy on the edges. Just finished college and moved back to Brooklyn. Hopefully I can meet some really cool friends on here to hang out with, gym, play video games, maybe clubbing, and stuff like that. I am black, C [...]
]]>
</description>
<dc:date>2013-09-17T18:04:11-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4074378104.html
</dc:source>
<dc:title>
<![CDATA[
Cool dude for cool friends - m4m (Bedstuy / Bedford) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-17T18:04:11-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4035424459.html">
<title>
<![CDATA[
Looking for some cool friends - m4m (New York) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4035424459.html
</link>
<description>
<![CDATA[
Moved back to Brooklyn after I completed college and I don't have any friends in the area. I'm just looking to meet some really cool guy friends to chill with and do cool stuff together like playing games, watch tv, hang out in the neighborhood and i [...]
]]>
</description>
<dc:date>2013-08-30T08:11:01-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4035424459.html
</dc:source>
<dc:title>
<![CDATA[
Looking for some cool friends - m4m (New York) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-08-30T08:11:01-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4059123346.html">
<title>
<![CDATA[
Cool dude for cool friends - m4m (Bedstuy / Bedford) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4059123346.html
</link>
<description>
<![CDATA[
Cool guy looking for friends. Little shy on the edges. Just finished college and moved back to Brooklyn. Hopefully I can meet some really cool friends on here to hang out with, gym, play video games, maybe clubbing, and stuff like that. I am black, C [...]
]]>
</description>
<dc:date>2013-09-10T14:46:42-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4059123346.html
</dc:source>
<dc:title>
<![CDATA[
Cool dude for cool friends - m4m (Bedstuy / Bedford) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-10T14:46:42-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4061957471.html">
<title>
<![CDATA[
Cool dude for cool friends - m4m (Bedstuy / Bedford) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4061957471.html
</link>
<description>
<![CDATA[
Cool guy looking for friends. Little shy on the edges. Just finished college and moved back to Brooklyn. Hopefully I can meet some really cool friends on here to hang out with, gym, play video games, maybe clubbing, and stuff like that. I am black, C [...]
]]>
</description>
<dc:date>2013-09-11T21:05:11-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4061957471.html
</dc:source>
<dc:title>
<![CDATA[
Cool dude for cool friends - m4m (Bedstuy / Bedford) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-11T21:05:11-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4088069548.html">
<title>
<![CDATA[
Cool black Caribbean dude looking for friends - m4m (New York) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4088069548.html
</link>
<description>
<![CDATA[
Had a few fake friends in the past, but sometimes u have to deal with fake friends before real friends come along. I'm just looking for a loyal friend or 2 to hang with and stuff like that. If you're looking for sex, please don't hit me up. I basical [...]
]]>
</description>
<dc:date>2013-09-24T09:21:05-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4088069548.html
</dc:source>
<dc:title>
<![CDATA[
Cool black Caribbean dude looking for friends - m4m (New York) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-24T09:21:05-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4065282223.html">
<title>
<![CDATA[
Friends-4-lyfe - m4m (Bedstuy/Bedford/Crown Heights) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4065282223.html
</link>
<description>
<![CDATA[
I moved back to Brooklyn after completing college and I don't have any friends in the area. I'm just looking to meet some really cool guy friends to chill with and do cool stuff together like playing games, watch tv, hang out in the neighborhood and [...]
]]>
</description>
<dc:date>2013-09-13T11:47:33-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4065282223.html
</dc:source>
<dc:title>
<![CDATA[
Friends-4-lyfe - m4m (Bedstuy/Bedford/Crown Heights) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-13T11:47:33-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4055385500.html">
<title>
<![CDATA[
Cool black Caribbean dude looking for friends - m4m (New York) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4055385500.html
</link>
<description>
<![CDATA[
Had a few fake friends in the past, but sometimes u have to deal with fake friends before real friends come along. I'm just looking for a loyal friend or 2 to hang with and stuff like that. If you're looking for sex, please don't hit me up. I basical [...]
]]>
</description>
<dc:date>2013-09-08T22:02:23-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4055385500.html
</dc:source>
<dc:title>
<![CDATA[
Cool black Caribbean dude looking for friends - m4m (New York) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-08T22:02:23-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4042257658.html">
<title>
<![CDATA[
Cool black Caribbean dude looking for friends - m4m (New York) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4042257658.html
</link>
<description>
<![CDATA[
Had a few fake friends in the past, but sometimes u have to deal with fake friends before real friends come along. I'm just looking for a loyal friend or 2 to hang with and stuff like that. If you're looking for sex, please don't hit me up. I basical [...]
]]>
</description>
<dc:date>2013-09-02T17:06:14-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4042257658.html
</dc:source>
<dc:title>
<![CDATA[
Cool black Caribbean dude looking for friends - m4m (New York) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-02T17:06:14-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4042259183.html">
<title>
<![CDATA[ Looking to make new friends - m4m (New York) 25yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4042259183.html
</link>
<description>
<![CDATA[
My friend moved back to Atlanta Georgia so I'm just looking to make some new friends to hang with and stuff like that. I basically have no social life at the moment. I like going clubs, hanging in Manhattan, movies, video games, beach and stuff like [...]
]]>
</description>
<dc:date>2013-09-02T17:07:06-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4042259183.html
</dc:source>
<dc:title>
<![CDATA[ Looking to make new friends - m4m (New York) 25yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-02T17:07:06-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4090618807.html">
<title>
<![CDATA[ Oh, you wish. - w4m (Upper East Side) 24yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4090618807.html
</link>
<description>
<![CDATA[
A short disclaimer, I get bored easily. I'm a hard catch. I doubt you'll make any type of impression. I'm intelligent and have the looks to match. The type of girl you wish you'd run into on here.
]]>
</description>
<dc:date>2013-09-25T11:17:19-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4090618807.html
</dc:source>
<dc:title>
<![CDATA[ Oh, you wish. - w4m (Upper East Side) 24yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-25T11:17:19-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097920683.html">
<title>
<![CDATA[
Mentor for young professional or college student - m4w (Union Square) 56yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097920683.html
</link>
<description>
<![CDATA[
Older gentleman, executive, and someone that the college interns and young professionals in the office often seek out for advice. I am approachable, kind, easy to talk to, and have been called a Father Figure by some (and like a Professor by others). [...]
]]>
</description>
<dc:date>2013-09-28T22:24:56-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097920683.html
</dc:source>
<dc:title>
<![CDATA[
Mentor for young professional or college student - m4w (Union Square) 56yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:24:56-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4051708249.html">
<title>
<![CDATA[ Be the 1st - m4m ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4051708249.html
</link>
<description>
<![CDATA[
Hi I'm Latino , lean 190 .... I have curious tendency and would love to experiment with someone that makes me feel comfortable
]]>
</description>
<dc:date>2013-09-07T03:52:58-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4051708249.html
</dc:source>
<dc:title>
<![CDATA[ Be the 1st - m4m ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-07T03:52:58-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4042445199.html">
<title>
<![CDATA[ Nice guys still exist !!! - m4w ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4042445199.html
</link>
<description>
<![CDATA[
Who, me? Just wanting to get into your pants? No way! Im the nice guy that all the girls say they want, but never actually fuck! All you girls just want the "bad boys." Im so sick of having my hot friends cry on my shoulders about their asshole boyfr [...]
]]>
</description>
<dc:date>2013-09-02T18:59:58-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4042445199.html
</dc:source>
<dc:title>
<![CDATA[ Nice guys still exist !!! - m4w ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-02T18:59:58-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097912396.html">
<title>
<![CDATA[ Looking to meet new people - m4m (New York) 21yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097912396.html
</link>
<description>
<![CDATA[
Hey, just recently moved to the city and looking to meet new people for friends. I'm open to most, anyone that's lived here who can show me a good time or even someone who's new like me who'd like to explore would be cool too. I come with a care-free [...]
]]>
</description>
<dc:date>2013-09-28T22:12:26-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097912396.html
</dc:source>
<dc:title>
<![CDATA[ Looking to meet new people - m4m (New York) 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:12:26-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4082521774.html">
<title>
<![CDATA[ paradigm shift - m4w (ny) 37yr ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4082521774.html
</link>
<description>
<![CDATA[
I'm a single male mid 30's looking for an openminded gal to just chat about anything beyond the norm. Its tough to find a 100% true believer of the brainwashing d whole country, if not the world, is being subjected to. I am getting tired of being hea [...]
]]>
</description>
<dc:date>2013-09-21T14:05:56-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4082521774.html
</dc:source>
<dc:title>
<![CDATA[ paradigm shift - m4w (ny) 37yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-21T14:05:56-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097871553.html">
<title>
<![CDATA[ Hi ladies - m4w ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097871553.html
</link>
<description>
<![CDATA[
Hi ladies . Just looking for someone to get to know by email as A friend. I'm a southern man as in Nashville , Tennessee with A nice southern accent looking to talk to a nice NYC girl who likes conversation about all issues . Me : 5'10 , light bro [...]
]]>
</description>
<dc:date>2013-09-28T21:18:20-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097871553.html
</dc:source>
<dc:title>
<![CDATA[ Hi ladies - m4w ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:18:20-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4068441305.html">
<title>
<![CDATA[
Cheated On? Dumped? Empathy is Here With Open Arms :-) - m4w (Upper West Side) 35yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4068441305.html
</link>
<description>
<![CDATA[
Ive been in a few serious LTRs, and have been cheated on in every one. I know heartbreak, and all the wonderful (sarcasm) feelings that come with being deceived and betrayed. I have trust issues, but still think more highly of women than I do of men. [...]
]]>
</description>
<dc:date>2013-09-14T23:16:37-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4068441305.html
</dc:source>
<dc:title>
<![CDATA[
Cheated On? Dumped? Empathy is Here With Open Arms :-) - m4w (Upper West Side) 35yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-14T23:16:37-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/lgi/stp/4097903254.html">
<title>
<![CDATA[
any girls wanna make some $ for a massage - m4w (nassau) 23yr
]]>
</title>
<link>
http://newyork.craigslist.org/lgi/stp/4097903254.html
</link>
<description>
<![CDATA[
I'm lookin for a massage...had a long day...i am just looking to chill and relax and will pay u for your time
]]>
</description>
<dc:date>2013-09-28T21:59:28-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/lgi/stp/4097903254.html
</dc:source>
<dc:title>
<![CDATA[
any girls wanna make some $ for a massage - m4w (nassau) 23yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:59:28-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097896550.html">
<title>
<![CDATA[ Chill out in central park - m4w (Midtown) 21yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097896550.html
</link>
<description>
<![CDATA[
Hi, Craigslist. I'm just looking for someone to get some lunch with next Saturday. I wanna have a great conversation with whoever wants to come out (no age limits). I'm a total geek when it comes to things like metaphysics, Dr. Who, political philo [...]
]]>
</description>
<dc:date>2013-09-28T21:50:05-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097896550.html
</dc:source>
<dc:title>
<![CDATA[ Chill out in central park - m4w (Midtown) 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:50:05-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097885310.html">
<title>
<![CDATA[
Are we going to tell people that we met on Craigslist? - m4w 29yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097885310.html
</link>
<description>
<![CDATA[
Yeah, this place has a bad rap, but it's probably not soo bad, right? Let me just read some other ads in this section and see for myself... "He wants to do what?" "Really? I mean, REALLY!?" "Why would he write that if he could so easily get arrest [...]
]]>
</description>
<dc:date>2013-09-28T21:35:30-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097885310.html
</dc:source>
<dc:title>
<![CDATA[
Are we going to tell people that we met on Craigslist? - m4w 29yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:35:30-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4097892425.html">
<title>
<![CDATA[ decent conversation - m4w (Queens) 29yr ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4097892425.html
</link>
<description>
<![CDATA[
Hey im hoping to find someone to talk to, kill time. big plus if you like sports and open to playing them, no I wont force it. I like a girly Girl so if youd like to chat with a sane, athletic, smart hispanic guy let me know. Would like to be cautiou [...]
]]>
</description>
<dc:date>2013-09-28T21:44:39-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4097892425.html
</dc:source>
<dc:title>
<![CDATA[ decent conversation - m4w (Queens) 29yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:44:39-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097887347.html">
<title>
<![CDATA[
looking for a female 30 & over who is tall, - m4w (East Village) 100yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097887347.html
</link>
<description>
<![CDATA[
yet willing to go see the new 3D Metallica movie. I myself don't drink much but I would be willing to burn a 420 beforehand, not ness. hit me back & we can exchange pix's & #'s I am a tall 6'4", Slim S/W/M with no Games or Drama & Extremely Sharp [...]
]]>
</description>
<dc:date>2013-09-28T21:38:07-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097887347.html
</dc:source>
<dc:title>
<![CDATA[
looking for a female 30 & over who is tall, - m4w (East Village) 100yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:38:07-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097861650.html">
<title>
<![CDATA[ Any one here plays poker?? - w4m (Lower East Side) ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097861650.html
</link>
<description>
<![CDATA[
Im looking for a friend that plays poker. He's very important to me and i need him right now. it would help a lot of any one can tell me some poker rooms in the lower east side. I can't remember if he said the poker room was some ones house or at a c [...]
]]>
</description>
<dc:date>2013-09-28T21:06:28-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097861650.html
</dc:source>
<dc:title>
<![CDATA[ Any one here plays poker?? - w4m (Lower East Side) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:06:28-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097775654.html">
<title>
<![CDATA[
looking$4$pretty$and$fit$lady - m4w (Inwood / Wash Hts)
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097775654.html
</link>
<description>
<![CDATA[
Looking for a pretty lady to wrestle with, age or race are not important but you have to be cool, pretty and looking to wrestle. I am a man who is very light in weight and very short in height and I am very respectful. Please send clear photos of you [...]
]]>
</description>
<dc:date>2013-09-28T19:35:22-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097775654.html
</dc:source>
<dc:title>
<![CDATA[
looking$4$pretty$and$fit$lady - m4w (Inwood / Wash Hts)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:35:22-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097875340.html">
<title>
<![CDATA[ Email chat - m4w 30yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097875340.html
</link>
<description>
<![CDATA[
Anyone still up and want to email back and forth for a bit? If so, drop me a line.
]]>
</description>
<dc:date>2013-09-28T21:23:02-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097875340.html
</dc:source>
<dc:title>
<![CDATA[ Email chat - m4w 30yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:23:02-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/wch/stp/4063711708.html">
<title>
<![CDATA[
Out of Shape and needing motivation - m4w (New Rochelle) 40yr
]]>
</title>
<link>
http://newyork.craigslist.org/wch/stp/4063711708.html
</link>
<description>
<![CDATA[
So, I'm totally out of shape. I'm 40, married, I smoke and I look like hell. I'm not overweight but tall and have a belly I'd like to get rid of and arms that may indeed be toothpicks. Would like someone in shape and fairly attractive to inspire me t [...]
]]>
</description>
<dc:date>2013-09-12T16:20:23-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/wch/stp/4063711708.html
</dc:source>
<dc:title>
<![CDATA[
Out of Shape and needing motivation - m4w (New Rochelle) 40yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-12T16:20:23-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4083802099.html">
<title>
<![CDATA[ 420 and Drinks Anyone?? - m4w (Inwood / Wash Hts) ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4083802099.html
</link>
<description>
<![CDATA[
bored and nothing to do. Any interesting lady and real want to do something this evening?? maybe get a drink and get to know each other. I am 420 friendly and down for some and a drink or 2. I am 26 Latino have pic to send
]]>
</description>
<dc:date>2013-09-22T09:39:43-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4083802099.html
</dc:source>
<dc:title>
<![CDATA[ 420 and Drinks Anyone?? - m4w (Inwood / Wash Hts) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-22T09:39:43-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097869871.html">
<title>
<![CDATA[ Late night chat - m4w (NYC) ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097869871.html
</link>
<description>
<![CDATA[
I'm not going to bed anytime soon. If you're up too, send an email and let's chat.
]]>
</description>
<dc:date>2013-09-28T21:16:19-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097869871.html
</dc:source>
<dc:title>
<![CDATA[ Late night chat - m4w (NYC) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:16:19-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4076859453.html">
<title>
<![CDATA[
Versatile Talented Male for Networking, Investors, Upscale Friends - m4mw
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4076859453.html
</link>
<description>
<![CDATA[
I am a uniquely skilled, versatile gentleman in my 20s and live in NYC area. I am into business finance and money growing investments. in the entrepreneur field, along with a performing artist dance educational background from NYU and Cornell. I loo [...]
]]>
</description>
<dc:date>2013-09-18T21:31:48-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4076859453.html
</dc:source>
<dc:title>
<![CDATA[
Versatile Talented Male for Networking, Investors, Upscale Friends - m4mw
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-18T21:31:48-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4081044938.html">
<title>
<![CDATA[
Cool dude for cool friends - m4m (Bedstuy / Bedford) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4081044938.html
</link>
<description>
<![CDATA[
Cool guy looking for friends. Little shy on the edges. Just finished college and moved back to Brooklyn. Hopefully I can meet some really cool friends on here to hang out with, gym, play video games, maybe clubbing, and stuff like that. I am black, C [...]
]]>
</description>
<dc:date>2013-09-20T20:04:56-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4081044938.html
</dc:source>
<dc:title>
<![CDATA[
Cool dude for cool friends - m4m (Bedstuy / Bedford) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-20T20:04:56-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4097863816.html">
<title>
<![CDATA[ bored looking for some fun tonight - m4w 22yr ]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4097863816.html
</link>
<description>
<![CDATA[
i have an open house for tonight im bored anybody wanna come over make it more interesting
]]>
</description>
<dc:date>2013-09-28T21:09:02-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4097863816.html
</dc:source>
<dc:title>
<![CDATA[ bored looking for some fun tonight - m4w 22yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:09:02-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/lgi/stp/4097862819.html">
<title>
<![CDATA[ Bored - m4w (online) 30yr ]]>
</title>
<link>
http://newyork.craigslist.org/lgi/stp/4097862819.html
</link>
<description>
<![CDATA[
30/m. I am bored. Anyone else bored? Anyone want to chat online (msn/aim) about anything? I am married so no meeting. just online chatting. Just put in the title Bored+today's date so I know you are real.
]]>
</description>
<dc:date>2013-09-28T21:07:52-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/lgi/stp/4097862819.html
</dc:source>
<dc:title>
<![CDATA[ Bored - m4w (online) 30yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:07:52-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4044872381.html">
<title>
<![CDATA[
Can a Male Stripper Chat You Into Mental Orgasm? Yes He Can! - m4w (Union Square) 34yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4044872381.html
</link>
<description>
<![CDATA[
I spend alot of time confined to this computer prison. Anyone care to chat? Night, day, whenever this is posted...Im borrrrred and need someone who fits the description of: Interesting; witty; easy going; more intelligent than a Kardashian; NOT uptig [...]
]]>
</description>
<dc:date>2013-09-03T21:27:19-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4044872381.html
</dc:source>
<dc:title>
<![CDATA[
Can a Male Stripper Chat You Into Mental Orgasm? Yes He Can! - m4w (Union Square) 34yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-03T21:27:19-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4073164759.html">
<title>
<![CDATA[
True, Committed Long Lasting Friendship and maybe more - m4w (new york) 24yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4073164759.html
</link>
<description>
<![CDATA[
I am a SINGLE 6 foot, Athletically Muscular Built, and Greenish-Hazel eyes Male who works in business and teaches dance. I 'm looking for a friend and for a "TRUE" and "LONG LASTING" friend (that can also be something more) and I mean it cause it is [...]
]]>
</description>
<dc:date>2013-09-17T09:18:54-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4073164759.html
</dc:source>
<dc:title>
<![CDATA[
True, Committed Long Lasting Friendship and maybe more - m4w (new york) 24yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-17T09:18:54-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4049545194.html">
<title>
<![CDATA[ Forceful Spanker Sought ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4049545194.html
</link>
<description>
<![CDATA[
Attractive straight white male 30s seeking a forceful man to be hand spanked (rubber gloves) for a first time maybe leading into something ongoing if all seems right. I have been thinking about this for some time now but not sure this is the right ve [...]
]]>
</description>
<dc:date>2013-09-06T02:56:54-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4049545194.html
</dc:source>
<dc:title>
<![CDATA[ Forceful Spanker Sought ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-06T02:56:54-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4078843288.html">
<title>
<![CDATA[
Sexy/Cute/Fun SWM looking for a 3LATIONSHIP (SoHo) 27yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4078843288.html
</link>
<description>
<![CDATA[
Call me crazy, but I'm a 2 women at a time kind of guy. And it works, I've been in a threelationship before. We were together for about a year, no drama. There's definitely a lot of advantages to being in a fun, supportive and mutually respectful 3la [...]
]]>
</description>
<dc:date>2013-09-19T19:32:23-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4078843288.html
</dc:source>
<dc:title>
<![CDATA[
Sexy/Cute/Fun SWM looking for a 3LATIONSHIP (SoHo) 27yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-19T19:32:23-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097838597.html">
<title>
<![CDATA[
Seeking Platonic Film Friends - Lovers of Cinema, Classics etc - m4mw (NYC) 32yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097838597.html
</link>
<description>
<![CDATA[
32 male filmmaker seeking film buff friends, especially lovers of classic films. I prefer female friends, I just tend to get along with them better but all is welcomed. I work nights and basically sit and watch movies all night, and I've watched film [...]
]]>
</description>
<dc:date>2013-09-28T20:40:04-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097838597.html
</dc:source>
<dc:title>
<![CDATA[
Seeking Platonic Film Friends - Lovers of Cinema, Classics etc - m4mw (NYC) 32yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:40:04-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brx/stp/4097830100.html">
<title>
<![CDATA[ Black Women Only - m4w ]]>
</title>
<link>
http://newyork.craigslist.org/brx/stp/4097830100.html
</link>
<description>
<![CDATA[
Lately I have been drawn to black women. Never been with one, but I want to be or have a NSA type of thing. Idk what is it, but Spanish women aren't drawing my attention anymore compared to Black women. Well I'm 24 Dominican just looking to chat and [...]
]]>
</description>
<dc:date>2013-09-28T20:30:25-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brx/stp/4097830100.html
</dc:source>
<dc:title>
<![CDATA[ Black Women Only - m4w ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:30:25-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4097831609.html">
<title>
<![CDATA[
SBM looking for love from honest woman for LTR - m4w (Springfield Gardens Queens) 30yr
]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4097831609.html
</link>
<description>
<![CDATA[
I'm a 30 year old laid back person, im looking for a girl who is truly wanting to have a future with me. But first in order for that to happen we need to be friends and see where that take us. I'm willing to take it SLOW at whatever pace ur into, im [...]
]]>
</description>
<dc:date>2013-09-28T20:32:09-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4097831609.html
</dc:source>
<dc:title>
<![CDATA[
SBM looking for love from honest woman for LTR - m4w (Springfield Gardens Queens) 30yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:32:09-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/stn/stp/4097743615.html">
<title>
<![CDATA[ helping family - m4w 31yr ]]>
</title>
<link>
http://newyork.craigslist.org/stn/stp/4097743615.html
</link>
<description>
<![CDATA[
I have a brother that's locked up in the state of Wyoming and is seeking pen-pals. just trying to help him out and get him some pen-pals cause I know what its like to not have anyone to talk to when locked up. if your interested in some good conversa [...]
]]>
</description>
<dc:date>2013-09-28T19:06:24-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/stn/stp/4097743615.html
</dc:source>
<dc:title>
<![CDATA[ helping family - m4w 31yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:06:24-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4054937717.html">
<title>
<![CDATA[ Seeking NYSC Workout Partner - m4m (Downtown) 55yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4054937717.html
</link>
<description>
<![CDATA[
Looking to get back into a regular lifting routine 2 to 3 times a week. Be great to have a workout bud. I'm flexible on time and location, but prefer someone available during the day after 11am or early evening at either Mercer St or Irving Place. Go [...]
]]>
</description>
<dc:date>2013-09-08T16:29:41-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4054937717.html
</dc:source>
<dc:title>
<![CDATA[ Seeking NYSC Workout Partner - m4m (Downtown) 55yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-08T16:29:41-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/jsy/stp/4078570011.html">
<title>
<![CDATA[
Married for married confidante, co-conspirator - m4w (montclair) 55yr
]]>
</title>
<link>
http://newyork.craigslist.org/jsy/stp/4078570011.html
</link>
<description>
<![CDATA[
Hi--You know the story: married to a very good person but starving for intimacy and excitement. Won't leave because of the kids but need some outlet to stay. Never would "go there" but mind keeps wandering? Maybe we can wander together, safely. What [...]
]]>
</description>
<dc:date>2013-09-19T16:38:44-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/jsy/stp/4078570011.html
</dc:source>
<dc:title>
<![CDATA[
Married for married confidante, co-conspirator - m4w (montclair) 55yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-19T16:38:44-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4097828730.html">
<title>
<![CDATA[
On your Period? Think its Sexy? - m4w (Brooklyn) 39yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4097828730.html
</link>
<description>
<![CDATA[
Any women out there who are menstruating? See your period as something sexy? I'm a white male who is super turned on by a female on her period. Looking for a woman who feels that no man should be squimish about a regular and normal time of the month [...]
]]>
</description>
<dc:date>2013-09-28T20:28:46-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4097828730.html
</dc:source>
<dc:title>
<![CDATA[
On your Period? Think its Sexy? - m4w (Brooklyn) 39yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:28:46-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4048511085.html">
<title>
<![CDATA[ looking for a cuddle buddy - m4w (bk) 25yr ]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4048511085.html
</link>
<description>
<![CDATA[
in bk have my own place, looking for a cool friend to come cuddle with from time t time so if thats u send a pic
]]>
</description>
<dc:date>2013-09-05T13:23:14-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4048511085.html
</dc:source>
<dc:title>
<![CDATA[ looking for a cuddle buddy - m4w (bk) 25yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-05T13:23:14-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4079821205.html">
<title>
<![CDATA[
++fall buddy for exploring the city, cuddle buddy or just a nice girl? - m4w (east village) 31yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4079821205.html
</link>
<description>
<![CDATA[
i plan on moving to nyc sometime this fall/winter or in the next year right now im in philly but i plan on coming up every other weekend to see some of the awesome events of fall/winter. lots of new restaurants, drinks and just good times with good [...]
]]>
</description>
<dc:date>2013-09-20T09:51:53-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4079821205.html
</dc:source>
<dc:title>
<![CDATA[
++fall buddy for exploring the city, cuddle buddy or just a nice girl? - m4w (east village) 31yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-20T09:51:53-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4061893789.html">
<title>
<![CDATA[ COOL BUDY - m4w (NYC) 27yr ]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4061893789.html
</link>
<description>
<![CDATA[
HEY IM LOOKING FOR A COOL BUDDY, WE CAN HIT UP MOVIE NIGHTS TUESDAYS IN THE CITY I WOULD PREFER U TO BE CUTE,KNOW HOW TO HAVE FUN AND SINGLE SO IF THATS U SEND A PIC AND WE CAN MOVE ON FROM THERE
]]>
</description>
<dc:date>2013-09-11T20:11:01-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4061893789.html
</dc:source>
<dc:title>
<![CDATA[ COOL BUDY - m4w (NYC) 27yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-11T20:11:01-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097814343.html">
<title>
<![CDATA[
Bored to the point that I don't even wanna post this ad - w4m (Inwood / Wash Hts) 32yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097814343.html
</link>
<description>
<![CDATA[
Yes that's how close to "disinterest" I am. I should just call it an early night but maybe a witty man can entertain me with a few emails before bed. I'll judge you by your photo (if you send one and you'll judge me too based on my photo so...) and b [...]
]]>
</description>
<dc:date>2013-09-28T20:13:20-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097814343.html
</dc:source>
<dc:title>
<![CDATA[
Bored to the point that I don't even wanna post this ad - w4m (Inwood / Wash Hts) 32yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:13:20-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4084583581.html">
<title>
<![CDATA[ asian woman friend - m4w (Queens) ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4084583581.html
</link>
<description>
<![CDATA[
single white male very slim build 40's w/o kids seeking a nice asian female friend age from late 30's to early 50's to go out from time to time movies lunch dinners broadway shows my treat pic 4 pic.
]]>
</description>
<dc:date>2013-09-22T16:28:35-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4084583581.html
</dc:source>
<dc:title>
<![CDATA[ asian woman friend - m4w (Queens) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-22T16:28:35-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brx/stp/4097805854.html">
<title>
<![CDATA[
I want bbw, fat or thick lady to ride me anytime today - m4w (Bronx, Harlem ) 35yr
]]>
</title>
<link>
http://newyork.craigslist.org/brx/stp/4097805854.html
</link>
<description>
<![CDATA[
I''m looking for a bbw or thick or big woman who wants to get intimate now. I can host. I'm 35 and lives in the Bronx. If interested, hit me up. Please be at least 22yrs. Any race welcomed. I eat pussy real good and have a big cock. Come n ride on my [...]
]]>
</description>
<dc:date>2013-09-28T20:04:39-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brx/stp/4097805854.html
</dc:source>
<dc:title>
<![CDATA[
I want bbw, fat or thick lady to ride me anytime today - m4w (Bronx, Harlem ) 35yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:04:39-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097801172.html">
<title>
<![CDATA[ Football Sunday - w4m (Manh or Bklyn ) ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097801172.html
</link>
<description>
<![CDATA[
Posted before, but haven't found any replies that stuck. I am an Asian female, mid 20s, attractive, slim, intelligent, sweet, down to earth, witty and enjoys a good hearty laugh. Also a Giants fan (I'm not going to hate if you are not--just enjoy th [...]
]]>
</description>
<dc:date>2013-09-28T20:00:00-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097801172.html
</dc:source>
<dc:title>
<![CDATA[ Football Sunday - w4m (Manh or Bklyn ) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:00:00-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097798803.html">
<title>
<![CDATA[
Awkward turtle seeks an adventure buddy - m4w (Midtown West) 22yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097798803.html
</link>
<description>
<![CDATA[
I'm in the city several times a week and I'm hoping to do some cool things and see some cool sights while I'm there. problem is I'm a very awkward person (borderline aspergers to be exact) so it's very difficult for me to meet people and make friends [...]
]]>
</description>
<dc:date>2013-09-28T19:57:40-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097798803.html
</dc:source>
<dc:title>
<![CDATA[
Awkward turtle seeks an adventure buddy - m4w (Midtown West) 22yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:57:40-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4097798356.html">
<title>
<![CDATA[ New friends... - w4ww (Queens) 21yr ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4097798356.html
</link>
<description>
<![CDATA[
Hey Craigslist...looking to meet some new fun and exciting yougn women to become friends with i know that sounds like a cliche` but i believe all of us deserve to have that one circle of friends who you can enjoy life with and grow together About m [...]
]]>
</description>
<dc:date>2013-09-28T19:57:12-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4097798356.html
</dc:source>
<dc:title>
<![CDATA[ New friends... - w4ww (Queens) 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:57:12-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097796939.html">
<title>
<![CDATA[
Care to chat with an older man? - m4w (Union Square) 55yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097796939.html
</link>
<description>
<![CDATA[
I'd like to hear from you. Executive, early 50's, caucasian. I enjoy chatting with younger women, and quite frankly love your energy and vitality. Perhaps you would like to talk with an older gentleman. No preconceived notions, no judgements, and no [...]
]]>
</description>
<dc:date>2013-09-28T19:55:48-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097796939.html
</dc:source>
<dc:title>
<![CDATA[
Care to chat with an older man? - m4w (Union Square) 55yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:55:48-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097782042.html">
<title>
<![CDATA[
Petite women are really hard to find. :) - m4w (NYC) 33yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097782042.html
</link>
<description>
<![CDATA[
I think times have changed to the big & beautiful, full figure, BBW etc. If you might be on the other end of the scale please reply back. I'm also slim, white and not into any drugs or smoking. Please use the word slim in your subject when you reply [...]
]]>
</description>
<dc:date>2013-09-28T19:41:18-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097782042.html
</dc:source>
<dc:title>
<![CDATA[
Petite women are really hard to find. :) - m4w (NYC) 33yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:41:18-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4074861712.html">
<title>
<![CDATA[
hiring female,s to model? apply now - m4w (Midtown) 35yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4074861712.html
</link>
<description>
<![CDATA[
we are looking for female,s who never model before of all age,s and size,s and shape,s to model pantie,s and bra,s for catalog,s for top designer,s good pay, part time, to apply from your cell ph, send pic,s you in pantie,s and bra or thong,s front a [...]
]]>
</description>
<dc:date>2013-09-18T03:51:37-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4074861712.html
</dc:source>
<dc:title>
<![CDATA[
hiring female,s to model? apply now - m4w (Midtown) 35yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-18T03:51:37-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4084577110.html">
<title>
<![CDATA[ ACTIVETY PARTNER - m4w (BK) ]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4084577110.html
</link>
<description>
<![CDATA[
Im looking for someone to enjoy summer with doing all sorts of activities such as but not limited to bike riding, beach, kayaking, motorcycle ride etc Im open to suggestions too Im a nice down to earth for real outgoing fun funny guy with a wide var [...]
]]>
</description>
<dc:date>2013-09-22T16:24:44-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4084577110.html
</dc:source>
<dc:title>
<![CDATA[ ACTIVETY PARTNER - m4w (BK) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-22T16:24:44-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097789807.html">
<title>
<![CDATA[ Looking for conversation - m4w 30yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097789807.html
</link>
<description>
<![CDATA[
I'm having a quiet evening and just looking for some friendly conversation. We could talk about absolutely anything. Age or relationship status is not important.
]]>
</description>
<dc:date>2013-09-28T19:48:50-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097789807.html
</dc:source>
<dc:title>
<![CDATA[ Looking for conversation - m4w 30yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:48:50-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097767615.html">
<title>
<![CDATA[ Are you into cuddling? - m4w (NY) 32yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097767615.html
</link>
<description>
<![CDATA[
Do you miss being held? I love holding someone in my arms or being held. the way a person can gently touch another or just be next to each other knowing it's a good feeling. How about waking up next to them knowing that there's less stress because e [...]
]]>
</description>
<dc:date>2013-09-28T19:27:59-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097767615.html
</dc:source>
<dc:title>
<![CDATA[ Are you into cuddling? - m4w (NY) 32yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:27:59-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097777566.html">
<title>
<![CDATA[ Looking for a girl - w4w (Lower East Side) 20yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097777566.html
</link>
<description>
<![CDATA[
Any girls interested of doing a threesome with me and my boyfriend. You must be clean. You must be Latin, Asian or white You must have big titis And sent a picture of yourself Age: 20-26. Me: Latin, 20 years old, 5'2 My boyfriend is white, 24 year [...]
]]>
</description>
<dc:date>2013-09-28T19:37:07-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097777566.html
</dc:source>
<dc:title>
<![CDATA[ Looking for a girl - w4w (Lower East Side) 20yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:37:07-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097766057.html">
<title>
<![CDATA[
Dating in NYC. relationships. jaded. let's talk. - m4w (Financial District) 28yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097766057.html
</link>
<description>
<![CDATA[
I've come to be more and more jaded by dating in NYC. I am a relatively successful guy. I don't like to brag, so I will just list facts: Well educated, in a secure job making 100k+, own a condo, genuinely a "nice guy", all for equality, gay marriage, [...]
]]>
</description>
<dc:date>2013-09-28T19:26:33-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097766057.html
</dc:source>
<dc:title>
<![CDATA[
Dating in NYC. relationships. jaded. let's talk. - m4w (Financial District) 28yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:26:33-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4097769637.html">
<title>
<![CDATA[ Let me do this for YOU - m4w (Queens.Manha Brookl) ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4097769637.html
</link>
<description>
<![CDATA[
Good looking white male Who is looking for an adult Friend ! Would you like to be orally pleasured today... in the mood.. and NO one to take care of your needs.. Well I will !! I love to Be Oral . So are u Bored @ Home no one home..but horny.. House [...]
]]>
</description>
<dc:date>2013-09-28T19:29:54-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4097769637.html
</dc:source>
<dc:title>
<![CDATA[ Let me do this for YOU - m4w (Queens.Manha Brookl) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:29:54-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4078679747.html">
<title>
<![CDATA[ Fall romance? - m4w (Manhattan/Queens) 34yr ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4078679747.html
</link>
<description>
<![CDATA[
Yes, I know this is the platonic section, but maybe start out as friends and see if anything develops... what do you think?
]]>
</description>
<dc:date>2013-09-19T17:42:59-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4078679747.html
</dc:source>
<dc:title>
<![CDATA[ Fall romance? - m4w (Manhattan/Queens) 34yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-19T17:42:59-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/jsy/stp/4097623833.html">
<title>
<![CDATA[
sad BBW iso chat. recently broke up with my partner and I'm confused - w4m (jersey city) 32yr
]]>
</title>
<link>
http://newyork.craigslist.org/jsy/stp/4097623833.html
</link>
<description>
<![CDATA[
I am pretty sad and am just looking for someone to chat with to keep me from crying. Things were going well, but they ended recently; and abruptly. And I'm hurt, confused and upset. I was sexually assaulted in january, and I got HSV1 from it. He un [...]
]]>
</description>
<dc:date>2013-09-28T17:32:17-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/jsy/stp/4097623833.html
</dc:source>
<dc:title>
<![CDATA[
sad BBW iso chat. recently broke up with my partner and I'm confused - w4m (jersey city) 32yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:32:17-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097762249.html">
<title>
<![CDATA[ Instant Message Me... - m4w (NYC) ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097762249.html
</link>
<description>
<![CDATA[
Ladies that would like to chat I am on AIM im me at the_lonely_island. Or email me your handle if you are on another client. Let's keep it local please...You don't see me placing ads in Timbuktu do you?
]]>
</description>
<dc:date>2013-09-28T19:23:05-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097762249.html
</dc:source>
<dc:title>
<![CDATA[ Instant Message Me... - m4w (NYC) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:23:05-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/lgi/stp/4097759245.html">
<title>
<![CDATA[ Planet Fitness Glen Cove - m4m (GLEN COVE) 48yr ]]>
</title>
<link>
http://newyork.craigslist.org/lgi/stp/4097759245.html
</link>
<description>
<![CDATA[
Looking for a buddy to work out with at Planet Fitness Glen Cove. I usually work out Saturday and Sunday mornings around 930 am and during the week either 430 am or after work around 5. Pic is attached. I had a complete rotator cuff tear last Februar [...]
]]>
</description>
<dc:date>2013-09-28T19:20:19-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/lgi/stp/4097759245.html
</dc:source>
<dc:title>
<![CDATA[ Planet Fitness Glen Cove - m4m (GLEN COVE) 48yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:20:19-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097745445.html">
<title>
<![CDATA[ White guy for white girl here. - m4w (NY) 32yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097745445.html
</link>
<description>
<![CDATA[
I just want someone to talk about our day with. Keep the fire burning even after a few dates. I want to look forward to your call or that little Email that just says "thinking about you." I don't have that in my life. I would love for you to be that [...]
]]>
</description>
<dc:date>2013-09-28T19:07:59-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097745445.html
</dc:source>
<dc:title>
<![CDATA[ White guy for white girl here. - m4w (NY) 32yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:07:59-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4088696318.html">
<title>
<![CDATA[ swf w/ bipolar disorder seeking same - w4w 34yr ]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4088696318.html
</link>
<description>
<![CDATA[
Any other white females out there with bipolar disorder? Seems no one else can understand us except other mentally ill people. re: manic depression mental illness
]]>
</description>
<dc:date>2013-09-24T13:20:59-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4088696318.html
</dc:source>
<dc:title>
<![CDATA[ swf w/ bipolar disorder seeking same - w4w 34yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-24T13:20:59-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4097728790.html">
<title>
<![CDATA[ Let me tickle you for money? - m4w 19yr ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4097728790.html
</link>
<description>
<![CDATA[
Hey, I'm a 19 year old white male 5'7'' 140lbs toned athletic slim build, reddish/brown hair blue eyes. I'm looking for women who would let me tickle them for 100 dollars an hour. Any age race is fine.
]]>
</description>
<dc:date>2013-09-28T18:53:47-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4097728790.html
</dc:source>
<dc:title>
<![CDATA[ Let me tickle you for money? - m4w 19yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:53:47-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/lgi/stp/4097729094.html">
<title>
<![CDATA[
New friends. people who like like games (farmingdale) 29yr
]]>
</title>
<link>
http://newyork.craigslist.org/lgi/stp/4097729094.html
</link>
<description>
<![CDATA[
I HAVE HAVE OUT GROWN. sorry caps. I have out grown my friends. We just don't click like we use to. Im real bad at making new friends. I like to play board games, video games, and learn new dice adventure games. I HAVE A UNIQUE COLLECTION OF BOARD GA [...]
]]>
</description>
<dc:date>2013-09-28T18:54:02-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/lgi/stp/4097729094.html
</dc:source>
<dc:title>
<![CDATA[
New friends. people who like like games (farmingdale) 29yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:54:02-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4087074358.html">
<title>
<![CDATA[ looking for a mature woman - m4w (queens) ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4087074358.html
</link>
<description>
<![CDATA[
44Yo white attach male 5.9 195lbs looking to eat out a mature woman very horny let me get u Off
]]>
</description>
<dc:date>2013-09-23T18:44:16-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4087074358.html
</dc:source>
<dc:title>
<![CDATA[ looking for a mature woman - m4w (queens) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-23T18:44:16-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097708945.html">
<title>
<![CDATA[ 420 - w4m (East Harlem) 21yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097708945.html
</link>
<description>
<![CDATA[
Im lookin for a dime of loud or sour im new around here and i cant find anything lol ... We could match up... Not lookin to fuck.. Just lookin have a nice convo n smoke
]]>
</description>
<dc:date>2013-09-28T18:37:00-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097708945.html
</dc:source>
<dc:title>
<![CDATA[ 420 - w4m (East Harlem) 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:37:00-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097672367.html">
<title>
<![CDATA[
Free non-sexual massage for a female who wants to relax. - m4w (New York) 34yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097672367.html
</link>
<description>
<![CDATA[
Hi, if you'd like a completely free massage from a guy who was trained at a spa in Manhattan please reply with the word relax in the subject. I don't care about race but be under 40 and slim to average. I'm white, slim with dark hair and eyes.
]]>
</description>
<dc:date>2013-09-28T18:08:02-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097672367.html
</dc:source>
<dc:title>
<![CDATA[
Free non-sexual massage for a female who wants to relax. - m4w (New York) 34yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:08:02-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4079253615.html">
<title>
<![CDATA[
Searching for Messianic female - m4w (midtown) 45yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4079253615.html
</link>
<description>
<![CDATA[
Let's get to know each other: dinners, converation, coffee ... I love talking and researching Messianic and Old Test topics
]]>
</description>
<dc:date>2013-09-20T05:23:41-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4079253615.html
</dc:source>
<dc:title>
<![CDATA[
Searching for Messianic female - m4w (midtown) 45yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-20T05:23:41-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097697732.html">
<title>
<![CDATA[
Give me a call so we can talk on the phone. - m4w (NY) 32yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097697732.html
</link>
<description>
<![CDATA[
Talking on the phone is way quicker than all of the email stuff. If you're kind of shy or quiet that's cool with me. I love to talk so I think that we'd be good together. My description is 5'9, white, black hair, brown eyes and slim. Please also be s [...]
]]>
</description>
<dc:date>2013-09-28T18:28:01-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097697732.html
</dc:source>
<dc:title>
<![CDATA[
Give me a call so we can talk on the phone. - m4w (NY) 32yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:28:01-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097711153.html">
<title>
<![CDATA[
Helpful guy seeks room in exchange for P/T household service - m4w (Kensington or Park Slope, Brooklyn) 40yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097711153.html
</link>
<description>
<![CDATA[
Helpful guy seeks room in exchange for P/T household service. Friendly, responsible, college educated, thoughtful, well-groomed and fun guy would be delighted to assist you with household work in exchange for clean room or studio. I will cook, clea [...]
]]>
</description>
<dc:date>2013-09-28T18:38:52-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097711153.html
</dc:source>
<dc:title>
<![CDATA[
Helpful guy seeks room in exchange for P/T household service - m4w (Kensington or Park Slope, Brooklyn) 40yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:38:52-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brx/stp/4097709270.html">
<title>
<![CDATA[ are u a sexy TS/CD who like phone sex? - m4t 21yr ]]>
</title>
<link>
http://newyork.craigslist.org/brx/stp/4097709270.html
</link>
<description>
<![CDATA[
llooking for a passable sexy ts/cd for hot phone sex, 21 mixed very horny and freaky, so if u are interested reply with a pic and stats , and lets have some fun , i have pics i just dont wanna post on here
]]>
</description>
<dc:date>2013-09-28T18:37:16-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brx/stp/4097709270.html
</dc:source>
<dc:title>
<![CDATA[ are u a sexy TS/CD who like phone sex? - m4t 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:37:16-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/jsy/stp/4097708015.html">
<title>
<![CDATA[ seeking a sexy TS/CD for phone sex - m4t 21yr ]]>
</title>
<link>
http://newyork.craigslist.org/jsy/stp/4097708015.html
</link>
<description>
<![CDATA[
looking for a passable sexy ts/cd for hot phone sex, 21 mixed very horny and freaky, so if u are interested reply with a pic and stats , and lets have some fun , i have pics i just dont wanna post on here
]]>
</description>
<dc:date>2013-09-28T18:36:16-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/jsy/stp/4097708015.html
</dc:source>
<dc:title>
<![CDATA[ seeking a sexy TS/CD for phone sex - m4t 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:36:16-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4097706709.html">
<title>
<![CDATA[ i need a TS/CD for hot phone sex - m4t 21yr ]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4097706709.html
</link>
<description>
<![CDATA[
llooking for a passable sexy ts/cd for hot phone sex, 21 mixed very horny and freaky, so if u are interested reply with a pic and stats , and lets have some fun , i have pics i just dont wanna post on here
]]>
</description>
<dc:date>2013-09-28T18:35:12-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4097706709.html
</dc:source>
<dc:title>
<![CDATA[ i need a TS/CD for hot phone sex - m4t 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:35:12-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097705196.html">
<title>
<![CDATA[ Seeking TS/CD for phone sex - m4t 21yr ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097705196.html
</link>
<description>
<![CDATA[
llooking for a passable sexy ts/cd for hot phone sex, 21 mixed very horny and freaky, so if u are interested reply with a pic and stats , and lets have some fun , i have pics i just dont wanna post on here
]]>
</description>
<dc:date>2013-09-28T18:34:04-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097705196.html
</dc:source>
<dc:title>
<![CDATA[ Seeking TS/CD for phone sex - m4t 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:34:04-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/que/stp/4097690389.html">
<title>
<![CDATA[ leisurely stroll - w4m (Queens) ]]>
</title>
<link>
http://newyork.craigslist.org/que/stp/4097690389.html
</link>
<description>
<![CDATA[
Its a nice night to take a walk. I'm by the queens center mall maybe you live in the area and would like to join me did are also welcome, we can share some stories or just enjoy the night sky...any takers?!
]]>
</description>
<dc:date>2013-09-28T18:22:05-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/que/stp/4097690389.html
</dc:source>
<dc:title>
<![CDATA[ leisurely stroll - w4m (Queens) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:22:05-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097647576.html">
<title>
<![CDATA[
Seeking fellow do-gooder - m4w (Upper East Side) 29yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097647576.html
</link>
<description>
<![CDATA[
Good evening, I do good volunteer work with homeless organizations among other groups, so important for me to give back to the community! For me that is more important than most things, other important things for me are my family, and friends. Also [...]
]]>
</description>
<dc:date>2013-09-28T17:49:26-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097647576.html
</dc:source>
<dc:title>
<![CDATA[
Seeking fellow do-gooder - m4w (Upper East Side) 29yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:49:26-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097666073.html">
<title>
<![CDATA[ 420 hook up (Chelsea) ]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097666073.html
</link>
<description>
<![CDATA[
New to NY and need a hook up. Looking to purchase soon/some time early tomorrow. Hoping to find someone legit not far for future connection. Looking for an eighth, decent to nice quality.
]]>
</description>
<dc:date>2013-09-28T18:03:17-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097666073.html
</dc:source>
<dc:title>
<![CDATA[ 420 hook up (Chelsea) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:03:17-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4075666006.html">
<title>
<![CDATA[
hiring female,s to model? apply now - m4w (Midtown) 35yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4075666006.html
</link>
<description>
<![CDATA[
we are looking for female,s who never model before of all age,s and size,s and shape,s to model pantie,s and bra,s for catalog,s for top designer,s good pay, part time, to apply from your cell ph, send pic,s you in pantie,s and bra or thong,s front a [...]
]]>
</description>
<dc:date>2013-09-18T10:53:37-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4075666006.html
</dc:source>
<dc:title>
<![CDATA[
hiring female,s to model? apply now - m4w (Midtown) 35yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-18T10:53:37-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097560230.html">
<title>
<![CDATA[
Tough times. Make and save money every month. - m4mm (SoHo) 38yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097560230.html
</link>
<description>
<![CDATA[
Would you like to make money and save money at the same time with Energy. I can help you. I have a proven system that can help you save some money every month and also make you money every month. All I need is you for 15 minutes and then you can walk [...]
]]>
</description>
<dc:date>2013-09-28T16:48:36-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097560230.html
</dc:source>
<dc:title>
<![CDATA[
Tough times. Make and save money every month. - m4mm (SoHo) 38yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T16:48:36-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4097688614.html">
<title>
<![CDATA[
Italian male seeking a female friend - m4w (Bensonhurst ) 45yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4097688614.html
</link>
<description>
<![CDATA[
seeking a nice down to earth friend, female. My idea is to have a friend I can chat with, walk, converse about life etc. I am down to earth, I enjoy arts, music, films, history, cuddling -passion and romance. So much to list I guess... So drop me a [...]
]]>
</description>
<dc:date>2013-09-28T18:20:40-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4097688614.html
</dc:source>
<dc:title>
<![CDATA[
Italian male seeking a female friend - m4w (Bensonhurst ) 45yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:20:40-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/mnh/stp/4097634090.html">
<title>
<![CDATA[
Passionate artist seeking Patron - m4m (manhattan) 25yr
]]>
</title>
<link>
http://newyork.craigslist.org/mnh/stp/4097634090.html
</link>
<description>
<![CDATA[
I hope this message finds someone well. I am a new artist in the city. I am extremely passionate about what I do. I am extremely determined and ambitious. I love challenges in my career and personal life. I am seeking an arrangement that can not only [...]
]]>
</description>
<dc:date>2013-09-28T17:39:35-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/mnh/stp/4097634090.html
</dc:source>
<dc:title>
<![CDATA[
Passionate artist seeking Patron - m4m (manhattan) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:39:35-07:00</dcterms:issued>
</item>
<item rdf:about="http://newyork.craigslist.org/brk/stp/4097681155.html">
<title>
<![CDATA[
Let's practice some reflexology techniques this weekend. - m4w (Kensington/Ditmas Park) 40yr
]]>
</title>
<link>
http://newyork.craigslist.org/brk/stp/4097681155.html
</link>
<description>
<![CDATA[
Let's practice some reflexology techniques this weekend. Seeking someone friendly, well groomed and upbeat to be my subject to practice a basic foot rub/reflexology techniques. You will be the receiver and you will give me feedback on my work. If i [...]
]]>
</description>
<dc:date>2013-09-28T18:14:46-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://newyork.craigslist.org/brk/stp/4097681155.html
</dc:source>
<dc:title>
<![CDATA[
Let's practice some reflexology techniques this weekend. - m4w (Kensington/Ditmas Park) 40yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:14:46-07:00</dcterms:issued>
</item>
</rdf:RDF>'''#feedparser.parse('http://newyork.craigslist.org/stp/index.rss')
    sf = '''This XML file does not appear to have any style information associated with it. The document tree is shown below.
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:ev="http://purl.org/rss/1.0/modules/event/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:syn="http://purl.org/rss/1.0/modules/syndication/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:admin="http://webns.net/mvcb/">
<channel rdf:about="http://sfbay.craigslist.org/stp/index.rss">
<title>craigslist | strictly platonic in SF bay area</title>
<link>http://sfbay.craigslist.org/stp/</link>
<description/>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:publisher>robot@craigslist.org</dc:publisher>
<dc:creator>robot@craigslist.org</dc:creator>
<dc:source>http://sfbay.craigslist.org/stp/index.rss</dc:source>
<dc:title>craigslist | strictly platonic in SF bay area</dc:title>
<dc:type>Collection</dc:type>
<syn:updateBase>2013-09-29T00:26:02-07:00</syn:updateBase>
<syn:updateFrequency>1</syn:updateFrequency>
<syn:updatePeriod>hourly</syn:updatePeriod>
<items>
<rdf:Seq>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097973494.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097972103.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4086646353.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4048661313.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4097962821.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097962091.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4066191897.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097954041.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4097952330.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097937143.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097948556.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097936089.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4081125924.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097937458.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097920868.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4090826781.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097924396.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097924141.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4093094641.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097921659.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4097919200.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4068522449.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097901450.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4082313420.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4086118082.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097901315.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4078357438.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097895328.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4066347325.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097887224.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097886991.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097885978.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097881026.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097871967.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097878674.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/pen/stp/4075458649.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4079125938.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097866727.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097842842.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4070036403.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4073861412.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097829885.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097828111.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097825480.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4097767472.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097820964.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4097767876.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097819313.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097817604.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097813528.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4056603071.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4087839982.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4073358844.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4053439825.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097799867.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097792303.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4061009365.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097778968.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4073843303.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4097774076.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4038855071.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097749551.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097665109.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4068024309.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097741299.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097740383.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097735154.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097666363.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4097661861.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097660548.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4049857616.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097708773.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097707568.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097686064.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4059783792.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097683428.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4064022496.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097635226.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097648596.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097648148.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097645918.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097643235.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4091631323.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097612013.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097610438.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097605570.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4078414456.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097596329.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097572516.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097588076.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/nby/stp/4097581021.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4097576637.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4097563029.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/eby/stp/4097561751.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4084433968.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4080739662.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4087188314.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sby/stp/4083977246.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/pen/stp/4097537418.html"/>
<rdf:li rdf:resource="http://sfbay.craigslist.org/sfc/stp/4093323831.html"/>
</rdf:Seq>
</items>
</channel>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097973494.html">
<title>
<![CDATA[
Friendly email.... chat? - m4w (danville / san ramon)
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097973494.html
</link>
<description>
<![CDATA[
Good evening. I am stuck home and facing a mountain of laundry to fold. How's that for a riveting Saturday night! :-p Anyhow, just thought it would be nice to trade a few emails or possibly chat. Age not important, and pics are strictly optional. P [...]
]]>
</description>
<dc:date>2013-09-28T23:59:13-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097973494.html
</dc:source>
<dc:title>
<![CDATA[
Friendly email.... chat? - m4w (danville / san ramon)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:59:13-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097972103.html">
<title>
<![CDATA[
looking for laughs and a good conversation - w4m (lafayette / orinda / moraga) 42yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097972103.html
</link>
<description>
<![CDATA[
I can't sleep right now and it would be nice to just have a good conversation with someone. Nothing sexual please.
]]>
</description>
<dc:date>2013-09-28T23:56:14-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097972103.html
</dc:source>
<dc:title>
<![CDATA[
looking for laughs and a good conversation - w4m (lafayette / orinda / moraga) 42yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:56:14-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4086646353.html">
<title>
<![CDATA[
Seeking someone to go to the Oakland Art Murmur with - m4w (Oakland) 24yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4086646353.html
</link>
<description>
<![CDATA[
Hello, I've never been to the Oakland Art Murmur but have been recommended to check it out. Unfortunately, I do not have much friends to ask to go with. So if you'd like to check it out and accompany me next Friday 10/4, shoot me an email. I'm a re [...]
]]>
</description>
<dc:date>2013-09-23T15:06:43-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4086646353.html
</dc:source>
<dc:title>
<![CDATA[
Seeking someone to go to the Oakland Art Murmur with - m4w (Oakland) 24yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-23T15:06:43-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4048661313.html">
<title>
<![CDATA[
Asian seeking friend/lover/activity partner, soul-mate type of girl - m4w (Oakland) 24yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4048661313.html
</link>
<description>
<![CDATA[
Hello I am Chinese, 5''9, 175 lbs, quite fit and work out once in a while. I am often mistaken for something I am not, until they get to know me, they'll find me quite the opposite, because I don't really show how I really am sometimes. People usual [...]
]]>
</description>
<dc:date>2013-09-05T14:27:28-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4048661313.html
</dc:source>
<dc:title>
<![CDATA[
Asian seeking friend/lover/activity partner, soul-mate type of girl - m4w (Oakland) 24yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-05T14:27:28-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4097962821.html">
<title>
<![CDATA[
Older WM seeks younger WM friendship - m4m (santa rosa)
]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4097962821.html
</link>
<description>
<![CDATA[
Older WM (60 - bottom) seeks younger man (20-45 ) for Saturday nights only for the guys in transition, or questioning to have a big brother/friend for an ongoing basis, for friendship to come over to watch movies, talk, or go to a movie, have a dinne [...]
]]>
</description>
<dc:date>2013-09-28T23:37:10-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4097962821.html
</dc:source>
<dc:title>
<![CDATA[
Older WM seeks younger WM friendship - m4m (santa rosa)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:37:10-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097962091.html">
<title>
<![CDATA[ Magic The Gathering - m4w (East Bay plz) 23yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097962091.html
</link>
<description>
<![CDATA[
Here it is. I am a nerd. You are too and hopefully even more so than I. We don't know much about one another, but first we'll just play cards together. Awkward? Timid? Shy? Good. I'm probably even worse socially. We are around the same age. Give or [...]
]]>
</description>
<dc:date>2013-09-28T23:35:45-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097962091.html
</dc:source>
<dc:title>
<![CDATA[ Magic The Gathering - m4w (East Bay plz) 23yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:35:45-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4066191897.html">
<title>
<![CDATA[
looking for a girl to hold/cuddle - m4w (san jose east) 27yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4066191897.html
</link>
<description>
<![CDATA[
Hello I'm looking for a nice girl to cuddle which could lead to more based on attraction. I'm 27, white, 6'5 green eyes brown hair, somewhat thin but athletic. I look younger. I have a good job that is why I moved here. Id like a girl between 18-30 p [...]
]]>
</description>
<dc:date>2013-09-13T19:28:56-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4066191897.html
</dc:source>
<dc:title>
<![CDATA[
looking for a girl to hold/cuddle - m4w (san jose east) 27yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-13T19:28:56-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097954041.html">
<title>
<![CDATA[ chill chat buddies - w4m (tenderloin) 23yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097954041.html
</link>
<description>
<![CDATA[
Wassups! I am looking for a chat buddy to help me pass some time. I am not usually free due to work and school but when I can chat haha ill be really on it. Im looking for someone who is preferably 21 - early 30s and asian. I have no intention of tr [...]
]]>
</description>
<dc:date>2013-09-28T23:20:14-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097954041.html
</dc:source>
<dc:title>
<![CDATA[ chill chat buddies - w4m (tenderloin) 23yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:20:14-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4097952330.html">
<title>
<![CDATA[
Want to come over and chill - m4w (santa rosa) 31yr
]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4097952330.html
</link>
<description>
<![CDATA[
Hello, i'm bored it'd be nice to have some company. I'm 5'8", 160lbs, college educated, asian, single. 31years old. I live in santa rosa. We can talk, watch tv/movies, look at videos on the internet, drink/smoke, play guitar for you. Please be cute. [...]
]]>
</description>
<dc:date>2013-09-28T23:17:10-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4097952330.html
</dc:source>
<dc:title>
<![CDATA[
Want to come over and chill - m4w (santa rosa) 31yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:17:10-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097937143.html">
<title>
<![CDATA[ Couple Looking.... - w4mw ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097937143.html
</link>
<description>
<![CDATA[
Hey were a couple, Im 23 tatted up student and hes a 28 yr old Train conductor.. Were from Sacramento originally but we live in Vallejo for now.. We love country music and beer lol.. and a damn good time. Were responsible and very honest people. We [...]
]]>
</description>
<dc:date>2013-09-28T22:50:46-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097937143.html
</dc:source>
<dc:title>
<![CDATA[ Couple Looking.... - w4mw ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:50:46-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097948556.html">
<title>
<![CDATA[
BEWARE: finally 18 looking for friendship that will last a life time - w4m (san jose south) 18yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097948556.html
</link>
<description>
<![CDATA[
Watch out for this posting. They ask for money right away when you respond to them. Don't respond to their post, it's a scam.
]]>
</description>
<dc:date>2013-09-28T23:10:12-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097948556.html
</dc:source>
<dc:title>
<![CDATA[
BEWARE: finally 18 looking for friendship that will last a life time - w4m (san jose south) 18yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T23:10:12-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097936089.html">
<title>
<![CDATA[
SUB MALE SEEKING DOMINANT ASSERTIVE WOMAN - m4w (sf)
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097936089.html
</link>
<description>
<![CDATA[
I am a experienced submissive swm in San Francisco seeking a dominant attractive woman in excellent shape, intelligent, educated, to make me her slave. I can be disciplined and punished by you, grovel at your feet, worship your body, be on your leash [...]
]]>
</description>
<dc:date>2013-09-28T22:48:55-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097936089.html
</dc:source>
<dc:title>
<![CDATA[
SUB MALE SEEKING DOMINANT ASSERTIVE WOMAN - m4w (sf)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:48:55-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4081125924.html">
<title>
<![CDATA[ Male Companion (Non-sexual) - m4w ]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4081125924.html
</link>
<description>
<![CDATA[
I am a gentleman, very nice, friendly, respectful, outgoing and witty for dates throughout the bay area. (non sexual) Male. Attractive fit man, 44 years old, 5'7" tall, short brown hair and hazel eyes. I will make you feel appreciated, special and [...]
]]>
</description>
<dc:date>2013-09-20T21:22:36-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4081125924.html
</dc:source>
<dc:title>
<![CDATA[ Male Companion (Non-sexual) - m4w ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-20T21:22:36-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097937458.html">
<title>
<![CDATA[
Making dinner and watching House Of Cards - m4w (san jose downtown) 22yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097937458.html
</link>
<description>
<![CDATA[
That's whats on my roster tonight. Fun. Anyone wanna do something tonight (unlikely) or tomorrow (more likely)? I like doing social things yet I have no friends. Kind of a sh***y predicament. Platonic only please.
]]>
</description>
<dc:date>2013-09-28T22:51:14-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097937458.html
</dc:source>
<dc:title>
<![CDATA[
Making dinner and watching House Of Cards - m4w (san jose downtown) 22yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:51:14-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097920868.html">
<title>
<![CDATA[ Cuddle now! - m4w (brentwood / oakley) 36yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097920868.html
</link>
<description>
<![CDATA[
I am here to find a cuddle friend. Spend the Morning with. We talk get to know each other a little then watch some Netflix. Hopefully we can play a little mess around. Touchy. Just safe and clean. I'm very lonely. My kids are away this week. Lookin [...]
]]>
</description>
<dc:date>2013-09-28T22:25:11-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097920868.html
</dc:source>
<dc:title>
<![CDATA[ Cuddle now! - m4w (brentwood / oakley) 36yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:25:11-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4090826781.html">
<title>
<![CDATA[ Looking for New Friends - m4w (berkeley) 43yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4090826781.html
</link>
<description>
<![CDATA[
Hi. I am looking to expand my circle of friends, most of my friends are either married or flakey. Please respond with a picture and I will too. Tell me some of your interests also. Age race not important, but a friendly fun attitude is important. I [...]
]]>
</description>
<dc:date>2013-09-25T12:41:05-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4090826781.html
</dc:source>
<dc:title>
<![CDATA[ Looking for New Friends - m4w (berkeley) 43yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-25T12:41:05-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097924396.html">
<title>
<![CDATA[ Looking for an email buddy! - m4w 26yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097924396.html
</link>
<description>
<![CDATA[
I'm hella bored and far from tired haha. 26 SWM only interested in platonic friendship 4 tattoos, no piercings, I like most kinds of music I enjoy staying active and having a good time. Gym, hike, run, explore, tennis, drink beer lol Email me and [...]
]]>
</description>
<dc:date>2013-09-28T22:30:33-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097924396.html
</dc:source>
<dc:title>
<![CDATA[ Looking for an email buddy! - m4w 26yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:30:33-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097924141.html">
<title>
<![CDATA[ Looking for New Friends - w4m (walnut creek) 34yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097924141.html
</link>
<description>
<![CDATA[
I'm looking to make some new friends. I'm NOT looking to hook up I'm just looking for friendship! I'm looking for someone who can hold a regular conversation, but can also joke around. If you're someone who likes to catch a movie, try new restaurant [...]
]]>
</description>
<dc:date>2013-09-28T22:30:10-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097924141.html
</dc:source>
<dc:title>
<![CDATA[ Looking for New Friends - w4m (walnut creek) 34yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:30:10-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4093094641.html">
<title>
<![CDATA[
New to the area.... - w4m (concord / pleasant hill / martinez) 37yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4093094641.html
</link>
<description>
<![CDATA[
Hello, Pretty Latina here, funny, optimistic, down to earth, enjoys the little things, loves to laugh, and smart. There's so much more to me, so email me and get to know me. Seeking a new friend...tell me about yourself and share a pic with me (face [...]
]]>
</description>
<dc:date>2013-09-26T13:41:04-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4093094641.html
</dc:source>
<dc:title>
<![CDATA[
New to the area.... - w4m (concord / pleasant hill / martinez) 37yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-26T13:41:04-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097921659.html">
<title>
<![CDATA[ just chill - w4w (under a bridge) 23yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097921659.html
</link>
<description>
<![CDATA[
Yo lets hang And tell some joked And throw eggs at people And spray paint a black dick on a cop car Mabe get a bite to eat
]]>
</description>
<dc:date>2013-09-28T22:26:22-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097921659.html
</dc:source>
<dc:title>
<![CDATA[ just chill - w4w (under a bridge) 23yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:26:22-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4097919200.html">
<title>
<![CDATA[ Social butterfly - w4mw (santa rosa) ]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4097919200.html
</link>
<description>
<![CDATA[
I am looking for someone with amazing people skills. Preferably someone that utilizes their skills professionally. I am a female in my mid 20s looking to improve my interpersonal skills through social outings to help affect my personal and profession [...]
]]>
</description>
<dc:date>2013-09-28T22:22:32-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4097919200.html
</dc:source>
<dc:title>
<![CDATA[ Social butterfly - w4mw (santa rosa) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T22:22:32-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4068522449.html">
<title>
<![CDATA[
can I find a friend with a big butt - m4w (fairfield / vacaville)
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4068522449.html
</link>
<description>
<![CDATA[
Hey whats going on with craigslist I am just looking for a coo woman who will start out as a very good friend and then see where it goes. But, I am looking for a woman who is flirtatious and playful and somebody who wouldn't mind play fighting or pla [...]
]]>
</description>
<dc:date>2013-09-15T02:30:56-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4068522449.html
</dc:source>
<dc:title>
<![CDATA[
can I find a friend with a big butt - m4w (fairfield / vacaville)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-15T02:30:56-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097901450.html">
<title>
<![CDATA[
BORED LOOKING TO GET OUT TONIGHT - m4w (hayward / castro valley) 34yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097901450.html
</link>
<description>
<![CDATA[
Bored outta my mind nothing else to do so phuck it here I am. If your bored and wanna get out smoke,take a walk, talk I dont know humor me It's 9:50 Saturday nite. Chances are if your reading this your bored as well . Stop contemplating and reply . [...]
]]>
</description>
<dc:date>2013-09-28T21:56:59-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097901450.html
</dc:source>
<dc:title>
<![CDATA[
BORED LOOKING TO GET OUT TONIGHT - m4w (hayward / castro valley) 34yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:56:59-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4082313420.html">
<title>
<![CDATA[
lets enjoy the interwebs! - m4w (financial district) 28yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4082313420.html
</link>
<description>
<![CDATA[
ok, here goes: I have just come to terms with the fact I am an exhibitionist... pretty harmless. This is where you come in: I want you to watch me strip and JO / climax over Skype. I don't want to meet you, don't want to sell you anything, i only wan [...]
]]>
</description>
<dc:date>2013-09-21T12:28:25-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4082313420.html
</dc:source>
<dc:title>
<![CDATA[
lets enjoy the interwebs! - m4w (financial district) 28yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-21T12:28:25-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4086118082.html">
<title>
<![CDATA[
lets enjoy the interwebs! - m4w (financial district) 28yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4086118082.html
</link>
<description>
<![CDATA[
ok, here goes: I have just come to terms with the fact I am an exhibitionist... pretty harmless. This is where you come in: I want you to watch me strip and JO / climax over Skype. I don't want to meet you, don't want to sell you anything, i only wan [...]
]]>
</description>
<dc:date>2013-09-23T11:35:10-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4086118082.html
</dc:source>
<dc:title>
<![CDATA[
lets enjoy the interwebs! - m4w (financial district) 28yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-23T11:35:10-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097901315.html">
<title>
<![CDATA[
32 yo molecular biologist/chemist loves music - m4w (mission district) 32yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097901315.html
</link>
<description>
<![CDATA[
Hey, i'm originally from MN. Live in Daly City now, work in the South bay in R&D as a molecular biologist and chemist in Genomics. Just looking for a cool friend to hang out with. Just got out of a relationship and want to be single for awhile. love [...]
]]>
</description>
<dc:date>2013-09-28T21:56:47-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097901315.html
</dc:source>
<dc:title>
<![CDATA[
32 yo molecular biologist/chemist loves music - m4w (mission district) 32yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:56:47-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4078357438.html">
<title>
<![CDATA[
European Massage Without Guilt - m4w (@ your place) 38yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4078357438.html
</link>
<description>
<![CDATA[
I'm a European man recently moved to the bay area and getting acclimated to my new home. As an accomplished masseur, I am, for a short time, offering massages for no fee whatsoever. I have my own table, oils, towels, etc. to bring you the best possib [...]
]]>
</description>
<dc:date>2013-09-19T14:47:51-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4078357438.html
</dc:source>
<dc:title>
<![CDATA[
European Massage Without Guilt - m4w (@ your place) 38yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-19T14:47:51-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097895328.html">
<title>
<![CDATA[
If you are in Cl why not instead text with a cool dude :p - m4w (oakland east) 20yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097895328.html
</link>
<description>
<![CDATA[
Hi so if you are browsing through cl bored why not stop and text with a cool dude instead. I am bored too and would like to text with a real female just talk about anything and you never know hopefully a friendship happens. Javier Real pics :) I am s [...]
]]>
</description>
<dc:date>2013-09-28T21:48:33-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097895328.html
</dc:source>
<dc:title>
<![CDATA[
If you are in Cl why not instead text with a cool dude :p - m4w (oakland east) 20yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:48:33-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4066347325.html">
<title>
<![CDATA[
looking for a girl to hold/cuddle - m4w (san jose east) 27yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4066347325.html
</link>
<description>
<![CDATA[
Hello I'm looking for a nice girl to cuddle which could lead to more based on attraction. I'm 27, white, 6'5 green eyes brown hair, somewhat thin but athletic. I look younger. I have a good job that is why I moved here. Id like a girl between 18-30 p [...]
]]>
</description>
<dc:date>2013-09-13T21:53:46-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4066347325.html
</dc:source>
<dc:title>
<![CDATA[
looking for a girl to hold/cuddle - m4w (san jose east) 27yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-13T21:53:46-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097887224.html">
<title>
<![CDATA[ Insidious Chapter 2 anyone? - m4w (cupertino) 33yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097887224.html
</link>
<description>
<![CDATA[
Hi, I do love to watch the Horror movies not the blood and gory kind, but the ones that try to scare the hell out of you. I did watch Insidious and was interesting though it could have been more scary. Now I am thinking of going to the sequel so I t [...]
]]>
</description>
<dc:date>2013-09-28T21:37:59-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097887224.html
</dc:source>
<dc:title>
<![CDATA[ Insidious Chapter 2 anyone? - m4w (cupertino) 33yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:37:59-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097886991.html">
<title>
<![CDATA[ A Window to the World! - m4w (san jose north) 51yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097886991.html
</link>
<description>
<![CDATA[
How nice would it be to know you are reading my note, here and now! Pondering, as you continue to read my little missive, should you reply and take the chance on a wonderful quest of discovery. I am currently in search of one special person to conne [...]
]]>
</description>
<dc:date>2013-09-28T21:37:40-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097886991.html
</dc:source>
<dc:title>
<![CDATA[ A Window to the World! - m4w (san jose north) 51yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:37:40-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097885978.html">
<title>
<![CDATA[
Looking for my gay-male-bestie! - w4m (East Bay) 40yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097885978.html
</link>
<description>
<![CDATA[
Hello! I'm looking to meet as many great people as possible. I am ready to meet my new GAY, MALE BFF! YOU: Intentional creator, happy, positive, open minded, cultured or well traveled, fun loving GAY MALE friend. PLEASE do not feel that you need to [...]
]]>
</description>
<dc:date>2013-09-28T21:36:25-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097885978.html
</dc:source>
<dc:title>
<![CDATA[
Looking for my gay-male-bestie! - w4m (East Bay) 40yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:36:25-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097881026.html">
<title>
<![CDATA[
Grown-ass woman looking to befriend SAME - w4w (oakland lake merritt / grand) 40yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097881026.html
</link>
<description>
<![CDATA[
Hello Ladies! I'm looking to meet as many great people as possible. I am, ready to meet my new BFF! YOU: Intentional creator, happy, positive, open minded, cultured or well traveled, fun loving female friend. PLEASE do not feel that you need to be [...]
]]>
</description>
<dc:date>2013-09-28T21:30:16-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097881026.html
</dc:source>
<dc:title>
<![CDATA[
Grown-ass woman looking to befriend SAME - w4w (oakland lake merritt / grand) 40yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:30:16-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097871967.html">
<title>
<![CDATA[
Looking for Dinner Partner and Good Conversation - m4w (financial district) 38yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097871967.html
</link>
<description>
<![CDATA[
I'm in town for a few days on business, starting Sunday, and looking for someone interesting to go out for drinks or dinner and to show me some of SF's neighborhoods. Someone who is not shy and enjoys good conversation and a good time. Ideally you ar [...]
]]>
</description>
<dc:date>2013-09-28T21:18:47-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097871967.html
</dc:source>
<dc:title>
<![CDATA[
Looking for Dinner Partner and Good Conversation - m4w (financial district) 38yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:18:47-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097878674.html">
<title>
<![CDATA[ Bored! - m4w (san jose south) 21yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097878674.html
</link>
<description>
<![CDATA[
I am so so bored right now, I really want to do something tonight. I don't really care what, just want someone to go do something with - I can't stand being in my house. Just go out and talk, do something active, whatever. I shouldn't have to say, bu [...]
]]>
</description>
<dc:date>2013-09-28T21:27:17-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097878674.html
</dc:source>
<dc:title>
<![CDATA[ Bored! - m4w (san jose south) 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:27:17-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/pen/stp/4075458649.html">
<title>
<![CDATA[
Stay at home dad, seeking stay at home mom - m4w 38yr
]]>
</title>
<link>
http://sfbay.craigslist.org/pen/stp/4075458649.html
</link>
<description>
<![CDATA[
Just a busy married stay at home dad here, looking for a married stay at home mom for adult conversation and flirty texting and maybe meeting for coffee in the daytime. I'm a normal guy I am and looking for a normal woman, I am a good listener so you [...]
]]>
</description>
<dc:date>2013-09-18T09:34:48-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/pen/stp/4075458649.html
</dc:source>
<dc:title>
<![CDATA[
Stay at home dad, seeking stay at home mom - m4w 38yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-18T09:34:48-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4079125938.html">
<title>
<![CDATA[ Seeking Friend - m4m (albany / el cerrito) 26yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4079125938.html
</link>
<description>
<![CDATA[
I am a 26 year old straight guy that although not a stranger to the bay area I recently moved back to the East Bay after close to 8 years so fairly new here now. I only honestly hangout with a total of three people with two people being friends I've [...]
]]>
</description>
<dc:date>2013-09-20T01:51:06-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4079125938.html
</dc:source>
<dc:title>
<![CDATA[ Seeking Friend - m4m (albany / el cerrito) 26yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-20T01:51:06-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097866727.html">
<title>
<![CDATA[ Seeking Work-Out Friend - m4m (walnut creek) 42yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097866727.html
</link>
<description>
<![CDATA[
I am a biWM seeking a work-out friend at the WC 24-Hr. Fitness. Not seeking a hook-up - repeat, not seeking a hook-up. Would like to get to know a few friends that work-out at this location. I typically do a tread-mill run and light upper body work-o [...]
]]>
</description>
<dc:date>2013-09-28T21:12:27-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097866727.html
</dc:source>
<dc:title>
<![CDATA[ Seeking Work-Out Friend - m4m (walnut creek) 42yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T21:12:27-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097842842.html">
<title>
<![CDATA[
If You Need Someone to Talk with--Text Me--w4w, w4t - w4w (Bay Area) 44yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097842842.html
</link>
<description>
<![CDATA[
Hi, everyone. I'm seeking gal (f & m2f) pals. No men right now, as, I've had plenty of responses from you gentlemen. This is for friends only. We all need someone we feel we can be ourselves with. Someone who is open minded, accepting, understanding [...]
]]>
</description>
<dc:date>2013-09-28T20:44:42-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097842842.html
</dc:source>
<dc:title>
<![CDATA[
If You Need Someone to Talk with--Text Me--w4w, w4t - w4w (Bay Area) 44yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:44:42-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4070036403.html">
<title>
<![CDATA[
Motorcycle riding partner - m4w (nearby Tracy) 50yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4070036403.html
</link>
<description>
<![CDATA[
Looking for motorcycle partner for day rides,and or weekend runs.Safety first, cruising at the speed limit. Meet for coffee first(u name the place), maybe plan ride. About me, easygoing. in subject box put in (coffee first)
]]>
</description>
<dc:date>2013-09-15T18:32:50-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4070036403.html
</dc:source>
<dc:title>
<![CDATA[
Motorcycle riding partner - m4w (nearby Tracy) 50yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-15T18:32:50-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4073861412.html">
<title>
<![CDATA[
looking for a woman who likes to play fight and play wrestle - m4w (concord / pleasant hill / martinez)
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4073861412.html
</link>
<description>
<![CDATA[
Where are the women who I can play fight with and play wrestle with? A woman who is not scared to get a little rough but still acts like a lady in many ways. I am looking for a woman who doesn't get offended by us playing around and I end up grabbing [...]
]]>
</description>
<dc:date>2013-09-17T13:50:13-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4073861412.html
</dc:source>
<dc:title>
<![CDATA[
looking for a woman who likes to play fight and play wrestle - m4w (concord / pleasant hill / martinez)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-17T13:50:13-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097829885.html">
<title>
<![CDATA[ Late Night Fun ;) - w4m (san jose east) 20yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097829885.html
</link>
<description>
<![CDATA[
Hello! Im looking for some late night fun.. maybe if we click it can be like a fwb/ cuddle buddy kinda thing. I'm young, 5'5, asian, disease free, extra in size- 190lbs, single.. Looking for somebody similar between 21-30 years, single, disease fr [...]
]]>
</description>
<dc:date>2013-09-28T20:30:10-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097829885.html
</dc:source>
<dc:title>
<![CDATA[ Late Night Fun ;) - w4m (san jose east) 20yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:30:10-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097828111.html">
<title>
<![CDATA[
2 friends in town looking for 420 friends for the night. - mm4w - mm4ww (lower nob hill) 2020yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097828111.html
</link>
<description>
<![CDATA[
We are staying the night in town and have nowhere to go so we thought we could hang out with some people and smoke some 420. Two good looking young athletes looking to kick back and get medicated. Unfortunately not old enough for the bar scenes yet. [...]
]]>
</description>
<dc:date>2013-09-28T20:28:04-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097828111.html
</dc:source>
<dc:title>
<![CDATA[
2 friends in town looking for 420 friends for the night. - mm4w - mm4ww (lower nob hill) 2020yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:28:04-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097825480.html">
<title>
<![CDATA[
Can I wear my black jeans tonight? - m4w (hayes valley)
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097825480.html
</link>
<description>
<![CDATA[
I'm down to go out but don't feel like getting dressed up. I hope that's ok! You can wear what you've got on too! (I'm so generous!) You'd like me if you like guys who -have a sense of humor -will pick up the check -are drama free -keep their [...]
]]>
</description>
<dc:date>2013-09-28T20:25:04-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097825480.html
</dc:source>
<dc:title>
<![CDATA[
Can I wear my black jeans tonight? - m4w (hayes valley)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:25:04-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4097767472.html">
<title>
<![CDATA[ couch potatoe - w4m (san rafael) 50yr ]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4097767472.html
</link>
<description>
<![CDATA[
looking for someone to: talk to watch a little tv home cooked meal. simple things
]]>
</description>
<dc:date>2013-09-28T19:27:51-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4097767472.html
</dc:source>
<dc:title>
<![CDATA[ couch potatoe - w4m (san rafael) 50yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:27:51-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097820964.html">
<title>
<![CDATA[
Anyone interested in Softball? - m4m (castro / upper market) 33yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097820964.html
</link>
<description>
<![CDATA[
San Francisco (SFGSL) has a gay softball league that is made up of hundreds of guys. The majority of players are gay. If you are interested in starting to play softball, let me know and we can get you on a team. There are different divisions (four o [...]
]]>
</description>
<dc:date>2013-09-28T20:20:17-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097820964.html
</dc:source>
<dc:title>
<![CDATA[
Anyone interested in Softball? - m4m (castro / upper market) 33yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:20:17-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4097767876.html">
<title>
<![CDATA[ friends only! - w4w (santa rosa) 27yr ]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4097767876.html
</link>
<description>
<![CDATA[
i need friends (not sex) to hang out with please come over lets be happy! im goin thru a divorce and need you. all my friends live out of town.
]]>
</description>
<dc:date>2013-09-28T19:28:14-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4097767876.html
</dc:source>
<dc:title>
<![CDATA[ friends only! - w4w (santa rosa) 27yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:28:14-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097819313.html">
<title>
<![CDATA[
Folsom street fair? lets go incognito, I have masks - m4w (excelsior / outer mission) 31yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097819313.html
</link>
<description>
<![CDATA[
I feel much more comfortable going while hiding our identities ;) I've never gone but lived here my whole 31 years ;)
]]>
</description>
<dc:date>2013-09-28T20:18:36-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097819313.html
</dc:source>
<dc:title>
<![CDATA[
Folsom street fair? lets go incognito, I have masks - m4w (excelsior / outer mission) 31yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:18:36-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097817604.html">
<title>
<![CDATA[
New to Oakland ready to Party - w4w (oakland north / temescal) 34yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097817604.html
</link>
<description>
<![CDATA[
Hi I am 34 black female from los angeles BBW. Moved out here 3 months ago. My homeboy came up to visit we on this Breaking Bad Marathon. Looking for a cool female who wants to come hang out. Must be able to bring the liqour and some party supplies. I [...]
]]>
</description>
<dc:date>2013-09-28T20:16:47-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097817604.html
</dc:source>
<dc:title>
<![CDATA[
New to Oakland ready to Party - w4w (oakland north / temescal) 34yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:16:47-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097813528.html">
<title>
<![CDATA[ Evening talk - m4w 30yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097813528.html
</link>
<description>
<![CDATA[
I'm dealing with a jet lag, intelligent conversation would be nice. You'd be talking to a 30 year old guy who is well read, well traveled and cultured. I have stories to tell and you can interest me in most things lot of people might consider boring [...]
]]>
</description>
<dc:date>2013-09-28T20:12:26-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097813528.html
</dc:source>
<dc:title>
<![CDATA[ Evening talk - m4w 30yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T20:12:26-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4056603071.html">
<title>
<![CDATA[
MATURE GAY GUY SEEKS YOUNGER COMPANION/FRIEND - m4m (EAST BAY/tri-valley) 59yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4056603071.html
</link>
<description>
<![CDATA[
MATURE, GOOD LOOKING, DISCREET GUY SEEKES A COMPANION/FRIEND TO DO THINGS WITH: road trips, movies, dinners and just hanging out and getting to know each other. I am NOT interested in a sexual relationship at this time. I am easy on the eyes, h/w/p, [...]
]]>
</description>
<dc:date>2013-09-09T12:18:39-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4056603071.html
</dc:source>
<dc:title>
<![CDATA[
MATURE GAY GUY SEEKS YOUNGER COMPANION/FRIEND - m4m (EAST BAY/tri-valley) 59yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-09T12:18:39-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4087839982.html">
<title>
<![CDATA[ To respect a woman. - m4w (berkeley) 48yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4087839982.html
</link>
<description>
<![CDATA[
First look in a woman eyes not her body when talking to her. Do not ever size a woman up as in what her breast size or is she easy to get in to bed, she will see that in you eyes. Show her strength but don't show her your pathetic attempts of contr [...]
]]>
</description>
<dc:date>2013-09-24T07:49:08-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4087839982.html
</dc:source>
<dc:title>
<![CDATA[ To respect a woman. - m4w (berkeley) 48yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-24T07:49:08-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4073358844.html">
<title>
<![CDATA[ Looking to connect 25yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4073358844.html
</link>
<description>
<![CDATA[
Hello there. I'm a 25 year old guy that makes a living doing stagehand work in the bay area. I had a sudden interest in posting to find people who are like me. Have you ever felt that you had a hard time meeting people who share similar interests as [...]
]]>
</description>
<dc:date>2013-09-17T10:33:20-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4073358844.html
</dc:source>
<dc:title>
<![CDATA[ Looking to connect 25yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-17T10:33:20-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4053439825.html">
<title>
<![CDATA[
Any Asian women want to chat? - m4w (san jose downtown) 37yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4053439825.html
</link>
<description>
<![CDATA[
Hi, I'm 37/white in San Jose -- I'd be interested in chatting with an Asian or Filipina women out there. I'll be online for a few hours more tonight, so if you might be interested in chatting a bit, send me an email :-)
]]>
</description>
<dc:date>2013-09-07T20:10:51-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4053439825.html
</dc:source>
<dc:title>
<![CDATA[
Any Asian women want to chat? - m4w (san jose downtown) 37yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-07T20:10:51-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097799867.html">
<title>
<![CDATA[ Nude Running Buddy (berkeley) 21yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097799867.html
</link>
<description>
<![CDATA[
Looking for someone to run naked with me tonight. HMU if you are interested. This is NOT a sexual activity so I would love for any interested men or women to join me in the fun! If we hit it off, then we can make it a regular occurrence
]]>
</description>
<dc:date>2013-09-28T19:58:44-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097799867.html
</dc:source>
<dc:title>
<![CDATA[ Nude Running Buddy (berkeley) 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:58:44-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097792303.html">
<title>
<![CDATA[
Looking for a workout buddy - East Bay Area Tall Single Father - m4w (concord / pleasant hill / martinez) 33yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097792303.html
</link>
<description>
<![CDATA[
I'm looking for someone to workout with In the area and do outdoor activities. I'm a single father, however, it doesn't matter if your single, married, have children or not. I'm only mentioning because I have time constrains. I'm happy to share a pi [...]
]]>
</description>
<dc:date>2013-09-28T19:51:17-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097792303.html
</dc:source>
<dc:title>
<![CDATA[
Looking for a workout buddy - East Bay Area Tall Single Father - m4w (concord / pleasant hill / martinez) 33yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:51:17-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4061009365.html">
<title>
<![CDATA[
Why aren't women fun anymore? - m4w (vallejo / benicia)
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4061009365.html
</link>
<description>
<![CDATA[
I am looking for a woman who is hella coo and is fun and playful and goofy. I am looking for a woman who loves to most of these following activities and but you don't have to do all: 1.Bowling 2.Pool 3.Videogames 4.Sex 5.Sports 6.Movies 7.Dancing 8.M [...]
]]>
</description>
<dc:date>2013-09-11T12:33:25-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4061009365.html
</dc:source>
<dc:title>
<![CDATA[
Why aren't women fun anymore? - m4w (vallejo / benicia)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-11T12:33:25-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097778968.html">
<title>
<![CDATA[
Does this come off wrong? - m4w (oakland lake merritt / grand)
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097778968.html
</link>
<description>
<![CDATA[
Iam sexually very repressed and have not had any in a while. Im not looking for any ol person. id like us to be able to trust each other and feel safe. especially since im not looking to have sex with a condom. I have my test results to prove im saf [...]
]]>
</description>
<dc:date>2013-09-28T19:38:27-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097778968.html
</dc:source>
<dc:title>
<![CDATA[
Does this come off wrong? - m4w (oakland lake merritt / grand)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:38:27-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4073843303.html">
<title>
<![CDATA[
Sorry skinny women but I like my women curvy and not in the stomach - m4w (hercules, pinole, san pablo, el sob)
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4073843303.html
</link>
<description>
<![CDATA[
Hey whats going on I am looking for a woman who can be basically my best friend somebody who I can go places with and do things with and somebody who I can talk to about anything. I am an openminded person so I am looking for a woman who is openminde [...]
]]>
</description>
<dc:date>2013-09-17T13:42:37-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4073843303.html
</dc:source>
<dc:title>
<![CDATA[
Sorry skinny women but I like my women curvy and not in the stomach - m4w (hercules, pinole, san pablo, el sob)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-17T13:42:37-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4097774076.html">
<title>
<![CDATA[
Late 50's fit, looking for same fit attractive woman 39-49 for workout - m4w (Santa Rosa) 59yr
]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4097774076.html
</link>
<description>
<![CDATA[
What I am really looking for is an attractive buffed female who wants to work out most mornings, 5 - 9, time is optional of course, to get in the best shape and condition you have ever been in.Most grocery stores are promoting products that are full [...]
]]>
</description>
<dc:date>2013-09-28T19:33:54-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4097774076.html
</dc:source>
<dc:title>
<![CDATA[
Late 50's fit, looking for same fit attractive woman 39-49 for workout - m4w (Santa Rosa) 59yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:33:54-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4038855071.html">
<title>
<![CDATA[
Lookin for a new female friend! - m4w (san jose south) 27yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4038855071.html
</link>
<description>
<![CDATA[
Hey Im lookin for a new buddy who's down to hang out,go to the movies,beaches,etc.I am 27 year old black guy who is studying occupational therapy at SJSU. Im simply lookin for a new female friend. Nothing more than that and if your interested hit me [...]
]]>
</description>
<dc:date>2013-08-31T21:28:22-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4038855071.html
</dc:source>
<dc:title>
<![CDATA[
Lookin for a new female friend! - m4w (san jose south) 27yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-08-31T21:28:22-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097749551.html">
<title>
<![CDATA[ Female Insight - m4w ]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097749551.html
</link>
<description>
<![CDATA[
Hi. I just want to ask a question and get a woman's perspective on something. If you are interested in helping me out please respond. It is sort of sexual in nature so don't respond if you don't want to get into that. Thanks.
]]>
</description>
<dc:date>2013-09-28T19:11:36-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097749551.html
</dc:source>
<dc:title>
<![CDATA[ Female Insight - m4w ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:11:36-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097665109.html">
<title>
<![CDATA[
Friends WOMEN ONLY PLEASE - w4w (concord / pleasant hill / martinez)
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097665109.html
</link>
<description>
<![CDATA[
I'm looking for some friends to hang out with I am a lot of fun and I'm a great person just need to get out and have fun if your down to make a new friend let me know
]]>
</description>
<dc:date>2013-09-28T18:02:35-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097665109.html
</dc:source>
<dc:title>
<![CDATA[
Friends WOMEN ONLY PLEASE - w4w (concord / pleasant hill / martinez)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:02:35-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4068024309.html">
<title>
<![CDATA[
Looking For A Text/Email Buddy - m4w (pittsburg / antioch) 43yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4068024309.html
</link>
<description>
<![CDATA[
Hello there. I am a fun loving, keep you laughing kind of guy. I am looking for a text/email friend, and would love to hear from you. I am looking for someone who can take a joke, and give the same rash of shit back. I am married, but I also love to [...]
]]>
</description>
<dc:date>2013-09-14T16:49:30-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4068024309.html
</dc:source>
<dc:title>
<![CDATA[
Looking For A Text/Email Buddy - m4w (pittsburg / antioch) 43yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-14T16:49:30-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097741299.html">
<title>
<![CDATA[
____Yes its a sex ad but not really____no replies yet :( - m4w (oakland hills / mills) 420yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097741299.html
</link>
<description>
<![CDATA[
in all due honesty im looking to just hang out with physical contact.Maybe i just kiss your neck or we hold hands while watching tv. And at the end of the night we sleep next to each other and cuddle.If you want more thats fine if not so is that. It [...]
]]>
</description>
<dc:date>2013-09-28T19:04:22-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097741299.html
</dc:source>
<dc:title>
<![CDATA[
____Yes its a sex ad but not really____no replies yet :( - m4w (oakland hills / mills) 420yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:04:22-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097740383.html">
<title>
<![CDATA[ 11pm curfew tonight - m4w (haight street) ]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097740383.html
</link>
<description>
<![CDATA[
I'm thinking of getting up really early tomorrow -- for a lot of reasons, but mostly because there is so much going on in the City. It would be fun to meet someone new tonight, have a drink and see if there's a connection. I'm interested in an early [...]
]]>
</description>
<dc:date>2013-09-28T19:03:37-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097740383.html
</dc:source>
<dc:title>
<![CDATA[ 11pm curfew tonight - m4w (haight street) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T19:03:37-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097735154.html">
<title>
<![CDATA[
Depressed, anxious, and needing a stoner friend - m4mw (mountain view) 24yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097735154.html
</link>
<description>
<![CDATA[
I'm a recent transplant that doesn't have the ability to get Prop 215 card yet. I really need a night to relax and am open to doing anything or just chilling and watching some tv or movies. I'm mobile and not looking to mooch so I can help with whate [...]
]]>
</description>
<dc:date>2013-09-28T18:59:05-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097735154.html
</dc:source>
<dc:title>
<![CDATA[
Depressed, anxious, and needing a stoner friend - m4mw (mountain view) 24yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:59:05-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097666363.html">
<title>
<![CDATA[ Massage trade - w4mw (berkeley) ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097666363.html
</link>
<description>
<![CDATA[
What a better way to spend the evening than to trade massages. I have a table and oils at my house. Who's game? Another day works too, as it's getting pretty late now.
]]>
</description>
<dc:date>2013-09-28T18:03:30-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097666363.html
</dc:source>
<dc:title>
<![CDATA[ Massage trade - w4mw (berkeley) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:03:30-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4097661861.html">
<title>
<![CDATA[ you, me, India - m4m ]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4097661861.html
</link>
<description>
<![CDATA[
Looking for someone who can afford to go to India for 4, 5 6 months, someone to adventure around with. Someone financially not troubled. Wouldn't hurt if you're easy ta be around and easy ta look at too :)
]]>
</description>
<dc:date>2013-09-28T18:00:09-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4097661861.html
</dc:source>
<dc:title>
<![CDATA[ you, me, India - m4m ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:00:09-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097660548.html">
<title>
<![CDATA[
Would you enjoy being naked for a disabled person - m4w (oakland rockridge / claremont) 29yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097660548.html
</link>
<description>
<![CDATA[
Hey I am Jake a , 29 year old nice normal guy , with a keen interest in Social Justice , the Beetles , the Simpson, Family Guy , Indian food bad 80's movies etc. Anyway , I am hoping to find someone who wouldn't mind getting naked in my company for [...]
]]>
</description>
<dc:date>2013-09-28T17:59:09-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097660548.html
</dc:source>
<dc:title>
<![CDATA[
Would you enjoy being naked for a disabled person - m4w (oakland rockridge / claremont) 29yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:59:09-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4049857616.html">
<title>
<![CDATA[ Your basic smart, normal guy - m4w (CA) ]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4049857616.html
</link>
<description>
<![CDATA[
No, I will not be making some elaborate (and wildly inaccurate) sales pitch about be awesome, brilliant, wealthy, or massively endowed. Instead, I will speak the truth -- which is that I'm a regular guy who would like to trade some email/IM with some [...]
]]>
</description>
<dc:date>2013-09-06T07:29:48-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4049857616.html
</dc:source>
<dc:title>
<![CDATA[ Your basic smart, normal guy - m4w (CA) ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-06T07:29:48-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097708773.html">
<title>
<![CDATA[
discreet 420 friend - m4w (fremont / union city / newark) 49yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097708773.html
</link>
<description>
<![CDATA[
Average married guy looking for discreet married woman. Friends first, add some 420, maybe more will happen then. Not happy at home need something new. If you feel the same way, then write back!!
]]>
</description>
<dc:date>2013-09-28T18:36:51-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097708773.html
</dc:source>
<dc:title>
<![CDATA[
discreet 420 friend - m4w (fremont / union city / newark) 49yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:36:51-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097707568.html">
<title>
<![CDATA[ Sad & Alone - w4m 24yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097707568.html
</link>
<description>
<![CDATA[
I recently got out of a serious relationship. Unfortunately, we both had trust issues and it lead to our break up. It's taken a toll on me and I hope I can find someone to talk to through this. Nothing hurts more than going through a break up alone. [...]
]]>
</description>
<dc:date>2013-09-28T18:35:54-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097707568.html
</dc:source>
<dc:title>
<![CDATA[ Sad & Alone - w4m 24yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:35:54-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097686064.html">
<title>
<![CDATA[
skinny dipping? - m4w (fremont / union city / newark) 25yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097686064.html
</link>
<description>
<![CDATA[
I want to go skinny dipping. Plain and simple. I don't know any women who I would feel comfortable with skinny dipping (I feel like it would make our friendships awkward) so here I am. I promise this isn't a scam to try and get you out of your clothe [...]
]]>
</description>
<dc:date>2013-09-28T18:18:39-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097686064.html
</dc:source>
<dc:title>
<![CDATA[
skinny dipping? - m4w (fremont / union city / newark) 25yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:18:39-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4059783792.html">
<title>
<![CDATA[
Acupressure - Amma/Reflexology trade (berkeley) 62yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4059783792.html
</link>
<description>
<![CDATA[
I am a certified acupressurist with 12 years of experience looking for a regular trade with someone certified in amma or reflexology. To ensure a response, please describe your training and experience as an amma or reflexology practitioner. If you [...]
]]>
</description>
<dc:date>2013-09-10T21:49:40-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4059783792.html
</dc:source>
<dc:title>
<![CDATA[
Acupressure - Amma/Reflexology trade (berkeley) 62yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-10T21:49:40-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097683428.html">
<title>
<![CDATA[
Seeking woman who'd like to learn how to shoot - m4w (Shooting Range in Richmond) 38yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097683428.html
</link>
<description>
<![CDATA[
Good afternoon...strange post...? perhaps... I'm a SF man, in my late thirties, and I enjoy the sport / hobby of shooting targets. I've shot trap before which is really a hard sport but mostly doing static targets and moving onto more shooting gam [...]
]]>
</description>
<dc:date>2013-09-28T18:16:31-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097683428.html
</dc:source>
<dc:title>
<![CDATA[
Seeking woman who'd like to learn how to shoot - m4w (Shooting Range in Richmond) 38yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T18:16:31-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4064022496.html">
<title>
<![CDATA[
Get dominated by a black man - m4w (concord / pleasant hill / martinez)
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4064022496.html
</link>
<description>
<![CDATA[
I want to find a woman who is submissive in the bedroom and I don't mean submissive to the point where they are a turn off to me because they can't act worth a damn lol. I mean it's true when I say submissive I mean a woman who gets turned on by ever [...]
]]>
</description>
<dc:date>2013-09-12T19:27:57-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4064022496.html
</dc:source>
<dc:title>
<![CDATA[
Get dominated by a black man - m4w (concord / pleasant hill / martinez)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-12T19:27:57-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097635226.html">
<title>
<![CDATA[
Slim white seeks foreign born friends - m4m (san jose downtown) 49yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097635226.html
</link>
<description>
<![CDATA[
Easygoing masculine slim guy would like to meet someone born in another country who might be a little lonely and needs someone to talk to on a regular basis. I like hiking and being outdoors, films, and getting to know new friends. Leave me your name [...]
]]>
</description>
<dc:date>2013-09-28T17:40:26-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097635226.html
</dc:source>
<dc:title>
<![CDATA[
Slim white seeks foreign born friends - m4m (san jose downtown) 49yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:40:26-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097648596.html">
<title>
<![CDATA[
Are you comfortable enough in your own skin... - m4w (santa clara) 52yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097648596.html
</link>
<description>
<![CDATA[
to go out without having to wear any make-up? Then I'd like to meet you for coffee, smoothie or a frozen yougart. I'm a responsible, working professional who enjoys movies, cooking, boating and a good conversation.
]]>
</description>
<dc:date>2013-09-28T17:50:13-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097648596.html
</dc:source>
<dc:title>
<![CDATA[
Are you comfortable enough in your own skin... - m4w (santa clara) 52yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:50:13-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097648148.html">
<title>
<![CDATA[
lets talk friends - m4w (fremont / union city / newark) 33yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097648148.html
</link>
<description>
<![CDATA[
hello wanna text and see what happen? life is full of adventures lets start today well establish guy here hope hear from you soon please put your favorite activities in subject line Thanks
]]>
</description>
<dc:date>2013-09-28T17:49:53-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097648148.html
</dc:source>
<dc:title>
<![CDATA[
lets talk friends - m4w (fremont / union city / newark) 33yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:49:53-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097645918.html">
<title>
<![CDATA[ Text ? - m4w (san jose south) 29yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097645918.html
</link>
<description>
<![CDATA[
Hello How are you doing? lets text im good guy please reply with subject of "todays date" so i know you are real Thanks
]]>
</description>
<dc:date>2013-09-28T17:48:10-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097645918.html
</dc:source>
<dc:title>
<![CDATA[ Text ? - m4w (san jose south) 29yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:48:10-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097643235.html">
<title>
<![CDATA[ Great activity partner - m4w (santa clara) 35yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097643235.html
</link>
<description>
<![CDATA[
Most my friends have moved away or got married. Just looking for someone who would like to do outdoor activities together, tennis, hiking, movies...etc. I make a great company.
]]>
</description>
<dc:date>2013-09-28T17:46:15-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097643235.html
</dc:source>
<dc:title>
<![CDATA[ Great activity partner - m4w (santa clara) 35yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:46:15-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4091631323.html">
<title>
<![CDATA[
looking for a female friend - m4w (hercules, pinole, san pablo, el sob)
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4091631323.html
</link>
<description>
<![CDATA[
im a shy guy looking for someone to text with and maybe hang out with once in a while. i am 5'6 160lbs average build and mexican. i got pics if ya want one of mine send me one of you. if ya just want to text and never meet up thats cool too. im down [...]
]]>
</description>
<dc:date>2013-09-25T20:06:10-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4091631323.html
</dc:source>
<dc:title>
<![CDATA[
looking for a female friend - m4w (hercules, pinole, san pablo, el sob)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-25T20:06:10-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097612013.html">
<title>
<![CDATA[
visiting for the first time. - m4m (castro / upper market)
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097612013.html
</link>
<description>
<![CDATA[
Hi, I am visiting SFO for the first time I will be in town Oct 17-19th I am a nice, reg type guy. I'm hoping I can get some advice and direction on an inexpensive but not too sketchy place to stay while in town. I work construction and therefore no [...]
]]>
</description>
<dc:date>2013-09-28T17:23:57-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097612013.html
</dc:source>
<dc:title>
<![CDATA[
visiting for the first time. - m4m (castro / upper market)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:23:57-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097610438.html">
<title>
<![CDATA[
Looking for a new friend - m4w (alamo square / nopa) 39yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097610438.html
</link>
<description>
<![CDATA[
Ladies of SF How are things going? So, i just thought it would be fun to find a new friend... Someone to explore the city with, go grab lunch on the weekends, check out some movies, art openings, etc... Im a 39 year old guy, i live in the city and [...]
]]>
</description>
<dc:date>2013-09-28T17:22:47-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097610438.html
</dc:source>
<dc:title>
<![CDATA[
Looking for a new friend - m4w (alamo square / nopa) 39yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:22:47-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097605570.html">
<title>
<![CDATA[
Stoner looking for friends (laurel hts / presidio) 19yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097605570.html
</link>
<description>
<![CDATA[
I moved to San Francisco about a month ago and Im still low in the friends department. I am a teen mom so I stay quite busy but I still love to have fun. Im 420 friendly :) of course and I love the arts. Im very talkative and like to sometimes sit do [...]
]]>
</description>
<dc:date>2013-09-28T17:19:19-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097605570.html
</dc:source>
<dc:title>
<![CDATA[
Stoner looking for friends (laurel hts / presidio) 19yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:19:19-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4078414456.html">
<title>
<![CDATA[ Movie/Hiking Friend - m4w (mill valley) 49yr ]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4078414456.html
</link>
<description>
<![CDATA[
Hi. I love going to the movies and hiking on nice days and would like to find someone to join me. I'm OK with holding hand so its really not "strictly" platonic lol. Drop me a line!
]]>
</description>
<dc:date>2013-09-19T15:15:56-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4078414456.html
</dc:source>
<dc:title>
<![CDATA[ Movie/Hiking Friend - m4w (mill valley) 49yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-19T15:15:56-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097596329.html">
<title>
<![CDATA[ Tamil movie Raja Rani - m4w (san jose south) 32yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097596329.html
</link>
<description>
<![CDATA[
There is a Indian desi tamil movie playing now which deals with failed relationship and love failures. Anyone intrerested in watching this movie today evening or late night shows please reply back.
]]>
</description>
<dc:date>2013-09-28T17:13:01-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097596329.html
</dc:source>
<dc:title>
<![CDATA[ Tamil movie Raja Rani - m4w (san jose south) 32yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:13:01-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097572516.html">
<title>
<![CDATA[
Single Dad Looking for Friend - m4w (concord / pleasant hill / martinez) 54yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097572516.html
</link>
<description>
<![CDATA[
I'm a single father of a darling 11 year old son who is the light of my life. Yeah, I got started late on parenthood. Though I technically share joint custody of him, he spends the majority of his time with me. Though I wouldn't trade the experience [...]
]]>
</description>
<dc:date>2013-09-28T16:56:48-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097572516.html
</dc:source>
<dc:title>
<![CDATA[
Single Dad Looking for Friend - m4w (concord / pleasant hill / martinez) 54yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T16:56:48-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097588076.html">
<title>
<![CDATA[ friends..!! - w4w (brentwood / oakley) 21yr ]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097588076.html
</link>
<description>
<![CDATA[
Hello! I'm writing on here because I need new friends. I moved here 2 years ago and still don't really know anyone, except the people i have worked with.... I need someone that I can hang out with, talk to, go to the bar occasionally with and have a [...]
]]>
</description>
<dc:date>2013-09-28T17:07:29-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097588076.html
</dc:source>
<dc:title>
<![CDATA[ friends..!! - w4w (brentwood / oakley) 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:07:29-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/nby/stp/4097581021.html">
<title>
<![CDATA[
Still out here in Ukiah and 58yrs - w4m (santa rosa) 58yr
]]>
</title>
<link>
http://sfbay.craigslist.org/nby/stp/4097581021.html
</link>
<description>
<![CDATA[
Any nice men out there to converse and possibly meet...I am 58yrs...5' 2" and 150lb...like anything outdoors...country and oldies music...bike riding, bowling and cheap wine...non smoker....let us talk and see where it goes....I live in Ukiah
]]>
</description>
<dc:date>2013-09-28T17:02:36-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/nby/stp/4097581021.html
</dc:source>
<dc:title>
<![CDATA[
Still out here in Ukiah and 58yrs - w4m (santa rosa) 58yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T17:02:36-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4097576637.html">
<title>
<![CDATA[
looking for a foodie on Tues Oct 1st - w4m (SPQR restaurant) 38yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4097576637.html
</link>
<description>
<![CDATA[
The reservation is for 10pm. SPQR is celebrating their 5th anniversary with a pasta tasting menu. The dinner cost is $54.00 and with wine pairing it will be $38.00 approximately more. Please let me know if you are interested. I can meet you at 9:45p [...]
]]>
</description>
<dc:date>2013-09-28T16:59:37-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4097576637.html
</dc:source>
<dc:title>
<![CDATA[
looking for a foodie on Tues Oct 1st - w4m (SPQR restaurant) 38yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T16:59:37-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4097563029.html">
<title>
<![CDATA[ I am married and confused - m4w 29yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4097563029.html
</link>
<description>
<![CDATA[
I am actually normally happily married and love my wife. But I do not really have that attraction for my wife, chemistry is missing. I am, for lack of a better word, bored, missing the passion and spark. I am well-educated, professional, athletic and [...]
]]>
</description>
<dc:date>2013-09-28T16:50:27-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4097563029.html
</dc:source>
<dc:title>
<![CDATA[ I am married and confused - m4w 29yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T16:50:27-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/eby/stp/4097561751.html">
<title>
<![CDATA[
Seriously Just Friends no Strings Attached - m4w (concord / pleasant hill / martinez) 45yr
]]>
</title>
<link>
http://sfbay.craigslist.org/eby/stp/4097561751.html
</link>
<description>
<![CDATA[
Hi. I am a MWM. Not looking for a hook up or Fwb. I am however hoping to find a woman who can accept me being in a relationship or vice versa. I find conversations from the heart most appealing. I enjoy laughter, sarcasm and someone with a good sense [...]
]]>
</description>
<dc:date>2013-09-28T16:49:37-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/eby/stp/4097561751.html
</dc:source>
<dc:title>
<![CDATA[
Seriously Just Friends no Strings Attached - m4w (concord / pleasant hill / martinez) 45yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T16:49:37-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4084433968.html">
<title>
<![CDATA[
Camping trip on 1-3 of October - mm4mw (west portal / forest hill) 21yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4084433968.html
</link>
<description>
<![CDATA[
Hello everybody! My friend and I need to find someone that would like to join us on a little camping trip at pills berry lake up north. We paid for 3 people already, but one of our buddies has to stay behind for school work We are both 21 and will [...]
]]>
</description>
<dc:date>2013-09-22T15:02:10-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4084433968.html
</dc:source>
<dc:title>
<![CDATA[
Camping trip on 1-3 of October - mm4mw (west portal / forest hill) 21yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-22T15:02:10-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4080739662.html">
<title>
<![CDATA[ queer scuba buddy needed! 29yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4080739662.html
</link>
<description>
<![CDATA[
hi! i'm an avid scuba diver (PADI certified Divemaster). i'd love to find another queer (male/female/cis/trans/gq welcome) that would like to explore our beautiful California waters. i'm a good diver with good skills that puts saftey first and i'm l [...]
]]>
</description>
<dc:date>2013-09-20T16:36:45-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4080739662.html
</dc:source>
<dc:title>
<![CDATA[ queer scuba buddy needed! 29yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-20T16:36:45-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4087188314.html">
<title>
<![CDATA[ New friends - m4m (san jose east) 21yr ]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4087188314.html
</link>
<description>
<![CDATA[
Looking for new friends and gaming buddies. I'm a laid back guy. Sarcastic, respectful, friendly, and honest. I enjoy traveling, dining, going on long hikes, kayaking, fishing, watching anime, playing video games, and lots of other things. Send me an [...]
]]>
</description>
<dc:date>2013-09-23T19:57:45-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4087188314.html
</dc:source>
<dc:title>
<![CDATA[ New friends - m4m (san jose east) 21yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-23T19:57:45-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sby/stp/4083977246.html">
<title>
<![CDATA[
LATINO LOOKIN FOR FRIENDs bLAZE XBOX TATTOOS CHILL . HMU IM DWNTwNsj - m4mw (san jose downtown) 27yr
]]>
</title>
<link>
http://sfbay.craigslist.org/sby/stp/4083977246.html
</link>
<description>
<![CDATA[
hey what's going on I am 27 Latino 5'7 with a few tattoos im chill just got the new gta on xbox looking to make friends on there too to do fun crazy mission. I do have a camera phone and I can also send pictures pictures. Send me a pic n a lil about [...]
]]>
</description>
<dc:date>2013-09-22T11:05:40-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sby/stp/4083977246.html
</dc:source>
<dc:title>
<![CDATA[
LATINO LOOKIN FOR FRIENDs bLAZE XBOX TATTOOS CHILL . HMU IM DWNTwNsj - m4mw (san jose downtown) 27yr
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-22T11:05:40-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/pen/stp/4097537418.html">
<title>
<![CDATA[ Workout Buddy - m4w (pacifica) 27yr ]]>
</title>
<link>
http://sfbay.craigslist.org/pen/stp/4097537418.html
</link>
<description>
<![CDATA[
I've been doing really well with keeping up on my diet and exercise for the past few months, I'm 20 or 30 pounds down, but I still have a long way to go. I had a workout buddy and it was very motivating, but they've sort of stopped caring (they have [...]
]]>
</description>
<dc:date>2013-09-28T16:33:51-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/pen/stp/4097537418.html
</dc:source>
<dc:title>
<![CDATA[ Workout Buddy - m4w (pacifica) 27yr ]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-28T16:33:51-07:00</dcterms:issued>
</item>
<item rdf:about="http://sfbay.craigslist.org/sfc/stp/4093323831.html">
<title>
<![CDATA[
artist seeks physique models. inexperienced is o.k. - m4m (mission district)
]]>
</title>
<link>
http://sfbay.craigslist.org/sfc/stp/4093323831.html
</link>
<description>
<![CDATA[
Although I am untrained as an artist, people often tell me how much they like my work. And I enjoy drawing the male body, from life. My work, though erotic, is not pornographic. Because I draw quickly you do not have to hold a pose for long, I do [...]
]]>
</description>
<dc:date>2013-09-26T15:37:19-07:00</dc:date>
<dc:language>en-us</dc:language>
<dc:rights>&copy; 2013 craigslist</dc:rights>
<dc:source>
http://sfbay.craigslist.org/sfc/stp/4093323831.html
</dc:source>
<dc:title>
<![CDATA[
artist seeks physique models. inexperienced is o.k. - m4m (mission district)
]]>
</dc:title>
<dc:type>text</dc:type>
<dcterms:issued>2013-09-26T15:37:19-07:00</dcterms:issued>
</item>
</rdf:RDF>'''#feedparser.parse('http://sfbay.craigslist.org/stp/index.rss')
    ny = feedparser.parse(ny)
    sf = feedparser.parse(sf)
##    print len(ny['entries'])
##    print len(sf['entries'])
##    localWords(ny,sf)
    getTopWords(ny,sf)



