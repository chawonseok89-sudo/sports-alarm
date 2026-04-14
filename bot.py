import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 경기 정보 및 스코어 가져오기
def get_match_info(team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://search.naver.com/search.naver?query={team_name}+경기결과"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 경기 상태 (종료, 진행중, 경기전 등)
        status = soup.select_one(".status_area").text.strip() if soup.select_one(".status_area") else "정보 없음"
        
        # 스코어 정보
        score = ""
        score_area = soup.select_one(".score_area")
        if score_area:
            score = score_area.text.strip()
        
        return f"{status} {score}"
    except:
        return "경기 정보를 가져올 수 없습니다."

# 2. 리그 순위 가져오기
def get_league_ranking(category, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # 네이버 스포츠 순위 페이지
        url = f"https://sports.news.naver.com/{category}/record/index"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 순위 테이블에서 해당 팀 찾기
        rows = soup.select("table tbody tr")
        for row in rows:
            if team_name in row.text:
                rank = row.select_one("th").text.strip() # 순위
                details = row.select("td")
                # 야구와 축구의 테이블 구조가 다르므로 공통적인 부분만 추출
                win_draw_loss = f"{details[1].text}승 {details[2].text}패" if category == "kbaseball" else f"{details[1].text}승 {details[2].text}무 {details[3].text}패"
                return f"{rank}위 ({win_draw_loss})"
        return "순위 정보 없음"
    except:
        return "순위를 불러오지 못했습니다."

async def send_sports_report():
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=token)

    # 데이터 수집
    kia_match = get_match_info("기아타이거즈")
    kia_rank = get_league_ranking("kbaseball", "KIA")
    
    jb_match = get_match_info("전북현대")
    jb_rank = get_league_ranking("kfootball", "전북")
    
    today_str = datetime.now().strftime('%m%d')
    kia_yt = f"https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}"
    jb_yt = f"https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}"

    # 메시지 구성
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 리포트\n\n"
        f"🐯 [기아 타이거즈]\n"
        f"📊 경기: {kia_match}\n"
        f"🏆 순위: {kia_rank}\n"
        f"📺 영상: {kia_yt}\n\n"
        f"⚽ [전북 현대]\n"
        f"📊 경기: {jb_match}\n"
        f"🏆 순위: {jb_rank}\n"
        f"📺 영상: {jb_yt}\n\n"
        f"발송 시간 기준 최신 데이터입니다! 🔥"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
