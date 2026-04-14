import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 경기 정보 추출 (진행중/종료/예정 표시)
def get_match_info(team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        search_url = f"https://search.naver.com/search.naver?query={team_name}+경기결과"
        res = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 경기 상태 및 스코어
        status_area = soup.select_one(".status_area")
        score_area = soup.select_one(".score_area")
        
        if status_area:
            status = status_area.text.strip()
            score = score_area.text.strip() if score_area else ""
            return f"[{status}] {score}"
        return "오늘 예정된 경기가 없습니다."
    except:
        return "경기 정보를 불러오는 중입니다."

# 2. 리그 순위 추출 (경기 유무와 상관없이 작동)
def get_league_ranking(category, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # 네이버 스포츠 순위 페이지 (직접 접근)
        url = f"https://sports.news.naver.com/{category}/record/index"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        rows = soup.select("table tbody tr")
        for row in rows:
            # 팀 이름이 포함된 행 찾기 (예: KIA, 전북)
            if team_name in row.text:
                rank = row.select_one("th").text.strip() # 순위
                tds = row.select("td")
                
                if category == "kbaseball": # 야구: 경기수, 승, 패, 무, 승률, 게임차
                    win_draw_loss = f"{tds[1].text}승 {tds[3].text}무 {正式_loss := tds[2].text}패"
                    gap = f" / 게임차: {tds[5].text}"
                    return f"{rank}위 ({win_draw_loss}){gap}"
                else: # 축구: 경기수, 승점, 승, 무, 패, 득점, 실점
                    points = f"{tds[0].text}점"
                    wdl = f"{tds[1].text}승 {tds[2].text}무 {tds[3].text}패"
                    return f"{rank}위 (승점 {points} / {wdl})"
        return "순위 데이터를 찾을 수 없습니다."
    except:
        return "순위 정보를 불러오는 중 오류가 발생했습니다."

async def send_sports_report():
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=token)

    # 데이터 수집 (경기 정보와 순위 정보를 독립적으로 가져옴)
    kia_match = get_match_info("기아타이거즈")
    kia_rank = get_league_ranking("kbaseball", "KIA")
    
    jb_match = get_match_info("전북현대")
    jb_rank = get_league_ranking("kfootball", "전북")
    
    today_str = datetime.now().strftime('%m%d')
    kia_yt = f"https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}"
    jb_yt = f"https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}"

    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n"
        f"🏆 현재순위: {kia_rank}\n"
        f"📊 경기결과: {kia_match}\n"
        f"📺 영상: {kia_yt}\n\n"
        f"⚽ [전북 현대]\n"
        f"🏆 현재순위: {jb_rank}\n"
        f"📊 경기결과: {jb_match}\n"
        f"📺 영상: {jb_yt}\n\n"
        f"내일도 승리하길 응원합니다! 🙌"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
