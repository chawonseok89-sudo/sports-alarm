import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_rank_from_page(url, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 순위표 테이블의 모든 행(tr)을 가져옵니다.
        rows = soup.find_all('tr')
        for row in rows:
            row_text = row.get_text()
            if team_name in row_text:
                # 팀명이 포함된 줄에서 숫자(순위)를 뽑아냅니다.
                # 보통 첫 번째 칸(td 또는 th)에 순위가 있습니다.
                rank = row.find(['th', 'td']).get_text().strip()
                return f"{rank}위"
        return "순위 확인 불가"
    except:
        return "데이터 읽기 실패"

def get_match_result(query):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://search.naver.com/search.naver?query={query}+경기결과"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        status = soup.select_one(".status_area").get_text().strip() if soup.select_one(".status_area") else "경기 없음"
        score = soup.select_one(".score_area").get_text().strip() if soup.select_one(".score_area") else ""
        return f"[{status}] {score}"
    except:
        return "정보 없음"

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 사용자님이 말씀하신 그 순위 페이지 주소들
    kia_rank = get_rank_from_page("https://sports.news.naver.com/kbaseball/record/index", "KIA")
    jb_rank = get_rank_from_page("https://sports.news.naver.com/kfootball/record/index", "전북")
    
    kia_match = get_match_result("기아타이거즈")
    jb_match = get_match_result("전북현대")
    
    today_str = datetime.now().strftime('%m%d')
    kia_yt = f"https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}"
    jb_yt = f"https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}"

    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n🏆 현재순위: {kia_rank}\n📊 경기결과: {kia_match}\n📺 영상: {kia_yt}\n\n"
        f"⚽ [전북 현대]\n🏆 현재순위: {jb_rank}\n📊 경기결과: {jb_match}\n📺 영상: {jb_yt}\n\n"
        f"순위표 페이지를 직접 읽어서 가져왔습니다! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
