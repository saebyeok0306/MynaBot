import discord
import asyncio
import requests
import json
import time

pageFirstArticleId2 = 0 #First id
pageLastArticleId2 = 0 #last id

async def searchEdac(g, t):
    global pageFirstArticleId2
    global pageLastArticleId2
    list_url = 'https://apis.naver.com/cafe-web/cafe2/ArticleList.json'
    page=1
    
    if(pageFirstArticleId2 == 0):
        try:
            print("pageFirst값이 없습니다.")
            f = open("database2.txt",'r', encoding='utf-8')
            data = f.readline()
            if data:
                pageFirstArticleId2 = int(data[10:])
            f.close()
        except:
            print("database2.txt가 없습니다.")

    while True:
        params = {
            'search.clubid' : '17046257', # 카페id
            'search.queryType' : 'lastArticle',
            'search.menuid': '23', # 게시판id
            'search.replylistorder': '', # 정렬기준
            'search.firstArticleInReply': 'false',
            'search.page': page, #페이지번호
            #'search.pageLastArticleId2': pageLastArticleId2 #더보기 버튼 눌렀을 때 마지막 article의 id
        }
        try:
            headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
            html = requests.get(list_url, params=params, verify=False, headers = headers).text
            jsonObj = json.loads(html)

            # urllib3
            #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            # requests
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            message = jsonObj.get("message")

            articleList = message["result"]["articleList"]
            articleSize = len(articleList)
            articleSeq = len(articleList)

            #page START
            #print("page : " + str(page) + " (" + str(articleSize) + ") START")

            while articleSeq > 0 :
                articleSeq = articleSeq - 1
                article = articleList[articleSeq]
                if(article["articleId"] <= pageFirstArticleId2):
                    #print("이전 게시글을 만남")
                    continue
            #제목
                subject = article["subject"] #제목
                writeDate = time.localtime(int(article["writeDateTimestamp"]) // 1000) #작성시간
                nickName = article["writerNickname"]

                
                await g.get_channel(873898727167914045).send("{} 《 {}-{:02d}-{:02d} 》\n제작자 {} │ 링크 {}".format(subject, writeDate.tm_year, writeDate.tm_mon, writeDate.tm_mday, nickName, "https://cafe.naver.com/edac/"+str(article["articleId"])))
                print("{} 《{}-{:02d}-{:02d} 》\n제작자 {} │ 링크 {}".format(subject, writeDate.tm_year, writeDate.tm_mon, writeDate.tm_mday, nickName, "https://cafe.naver.com/edac/"+str(article["articleId"])))

                #마지막 게시글ID
                if articleSeq == 0:
                    pageFirstArticleId2 = article["articleId"]
                    f = open("database2.txt",'w', encoding='utf-8')
                    f.write("firstID : " + str(pageFirstArticleId2))
                    f.close()

                if articleSeq == articleSize-1 :
                    pageLastArticleId2 = article["articleId"]


            #page END
            #print("page : " + str(page) + " END    LastId" + str(pageLastArticleId2))

            break
        except:
            print("에닥크롤링 실패")
            break