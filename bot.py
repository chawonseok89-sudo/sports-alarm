import os
import asyncio
import telegram
import requests
from datetime import datetime

# 1. 경기 정보 추출 (네이버 검색 활용)
def get_match_info(team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://search.naver.com/search.naver?query={team_name}+경기결과"
        res = requests.get(url, headers=headers)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'html.parser')
        
        status_area = soup.select_one(".status_area")
        score_area = soup.select_one(".score_area")
        
        if status_area:
            status = status_area.text.strip()
            score = score_area.text.strip() if score_area else ""
            return f"[{status}] {score}"
        return "오늘 예정된 경기가 없습니다."
    except:
        return "경기 정보 업데이트 중"

# 2. 리그 순위 추출 (네이버 내부 데이터 주소 직접 접근)
def get_rank(category):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # 야구와 축구의 순위 데이터 서버 주소 (API)
        if category == "kbaseball":
            url = "https://sports-api.naver.com/kbaseball/record/team?year=2026"
            target_team = "KIA"
        else:
            url = "https://sports-api.naver.com/kfootball/record/team?year=2026&leagueId=K1"
            target_team = "전북"

        data = requests.get(url, headers=headers).json()
        
        # 데이터 리스트에서 우리 팀 찾기
        for item in data.get('regularTeamRecordList', data.get('teamRecordList', [])):
            team_name = item.get('teamName', item.get('name', ''))
            if target_team in team_name:
                rank = item['rank']
                if category == "kbaseball":
                    return f"{rank}위 ({item['won']}승 {item['drawn']}무 {item['lost']}패 / 게임차: {item['gameDiff']})"
                else:
                    return f"{rank}위 (승점 {item['point']}점 / {item['won']}승 {item['drawn']}무 {item['lost']}패)"
        return "순위 정보 검색 실패"
    except Exception as e:
        return f"순위 로딩 실패"

async def send_sports_report():
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=token)

    # 데이터 수집
    kia_match = get_match_info("기아타이거즈")
    kia_rank = get_rank("kbaseball")
    
    jb_match = get_match_info("전북현대")
    jb_rank = get_rank("kfootball")
    
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
        f"오늘도 수고하셨습니다! 내일도 응원해요! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
