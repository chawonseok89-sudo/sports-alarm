import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 정보를 긁어오는 함수
def get_naver_news(query):
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 가장 상단의 뉴스 제목 하나를 가져옴
        title = soup.select_one(".news_tit").text
        link = soup.select_one(".news_tit")['href']
        return f"📰 {title}\n🔗 {link}"
    except:
        return "뉴스를 불러오지 못했습니다."

async def send_sports_report():
    # GitHub Secrets에서 정보 가져오기
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=token)

    # 1. 데이터 수집
    kia_news = get_naver_news("기아타이거즈")
    jb_news = get_naver_news("전북현대")
    
    # 2. 유튜브 링크 생성 (날짜 포함)
    today_str = datetime.now().strftime('%m%d')
    kia_yt = f"https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}"
    jb_yt = f"https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}"

    # 3. 메시지 구성
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 알림\n\n"
        f"🐯 [기아 타이거즈 소식]\n{kia_news}\n"
        f"📺 하이라이트: {kia_yt}\n\n"
        f"⚽ [전북 현대 소식]\n{jb_news}\n"
        f"📺 하이라이트: {jb_yt}"
    )

    # 4. 전송
    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
