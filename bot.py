import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 스코어 및 경기 정보 추출 함수
def get_match_details(category, team_name):
    try:
        # 카테고리별 네이버 스포츠 일정/결과 페이지 (야구: kbaseball, 축구: kfootball)
        url = f"https://sports.news.naver.com/{category}/schedule/index"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 오늘 날짜의 경기 목록 찾기
        # 네이버 스포츠 페이지 구조상 실시간 데이터는 스크립트 내에 존재할 수 있어 
        # 가장 확실한 '뉴스 검색 결과 내 스코어 보드'를 활용하는 방식으로 제안드립니다.
        search_url = f"https://search.naver.com/search.naver?query={team_name}+경기결과"
        res = requests.get(search_url, headers=headers)
        s = BeautifulSoup(res.text, 'html.parser')
        
        # 스코어보드 영역 추출 (네이버 검색 결과 기준)
        score_box = s.select_one(".status_area")
        if score_box:
            status = score_box.text.strip() # 종료, 경기전, 진행중 등
            score = s.select_one(".score_area").text.strip() if s.select_one(".score_area") else "정보 없음"
            return f"[{status}] {score}"
        else:
            return "오늘 예정된 경기가 없거나 정보를 찾을 수 없습니다."
    except Exception as e:
        return "스코어를 불러오는 중 오류가 발생했습니다."

async def send_sports_report():
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=token)

    # 1. 스코어 정보 가져오기
    kia_score = get_match_details("kbaseball", "기아타이거즈")
    jb_score = get_match_details("kfootball", "전북현대")
    
    # 2. 유튜브 하이라이트 링크 생성
    today_str = datetime.now().strftime('%m%d')
    kia_yt = f"https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}"
    jb_yt = f"https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}"

    # 3. 메시지 구성
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 경기 레포트\n\n"
        f"🐯 [기아 타이거즈]\n📊 스코어: {kia_score}\n📺 영상: {kia_yt}\n\n"
        f"⚽ [전북 현대]\n📊 스코어: {jb_score}\n📺 영상: {jb_yt}\n\n"
        f"밤 10시 기준 최신 정보입니다! 🔥"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
