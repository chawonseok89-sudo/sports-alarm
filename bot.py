import os
import asyncio
import telegram
import requests
from datetime import datetime

def get_kbo_data():
    try:
        # KBO 순위 및 오늘 경기 데이터 (네이버 스포츠 API)
        url = "https://sports-api.naver.com/kbaseball/record/team?year=2026"
        res = requests.get(url).json()
        rank_data = ""
        for team in res['teamRecordList']:
            if "KIA" in team['name']:
                rank_data = f"{team['rank']}위 ({team['won']}승 {team['drawn']}무 {team['lost']}패)"
                break
        
        # 오늘 경기 결과
        today = datetime.now().strftime('%Y%m%d')
        m_url = f"https://sports-api.naver.com/kbaseball/schedule?date={today}"
        m_res = requests.get(m_url).json()
        match_data = "오늘 예정된 경기 없음"
        for game in m_res.get('todayScheduleList', []):
            if "KIA" in [game['homeTeamName'], game['awayTeamName']]:
                match_data = f"[{game['state']}] {game['homeTeamName']} {game['homeTeamScore']} : {game['awayTeamScore']} {game['awayTeamName']}"
                break
        return rank_data, match_data
    except:
        return "순위 확인 중", "경기 정보 없음"

def get_kleague_data():
    try:
        # K리그1 순위 데이터
        url = "https://sports-api.naver.com/kfootball/record/team?year=2026&leagueId=K1"
        res = requests.get(url).json()
        rank_data = ""
        for team in res['teamRecordList']:
            if "전북" in team['name']:
                rank_data = f"{team['rank']}위 (승점 {team['point']}점 / {team['won']}승 {team['drawn']}무 {team['lost']}패)"
                break
        
        # 오늘 경기 결과
        today = datetime.now().strftime('%Y%m%d')
        m_url = f"https://sports-api.naver.com/kfootball/schedule?date={today}&leagueId=K1"
        m_res = requests.get(m_url).json()
        match_data = "오늘 예정된 경기 없음"
        for game in m_res.get('todayScheduleList', []):
            if "전북" in [game['homeTeamName'], game['awayTeamName']]:
                match_data = f"[{game['state']}] {game['homeTeamName']} {game['homeTeamScore']} : {game['awayTeamScore']} {game['awayTeamName']}"
                break
        return rank_data, match_data
    except:
        return "순위 확인 중", "경기 정보 없음"

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    kia_rank, kia_match = get_kbo_data()
    jb_rank, jb_match = get_kleague_data()
    
    today_str = datetime.now().strftime('%m%d')
    kia_yt = f"https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}"
    jb_yt = f"https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}"

    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n🏆 현재순위: {kia_rank}\n📊 경기결과: {kia_match}\n📺 영상: {kia_yt}\n\n"
        f"⚽ [전북 현대]\n🏆 현재순위: {jb_rank}\n📊 경기결과: {jb_match}\n📺 영상: {jb_yt}\n\n"
        f"가장 정확한 데이터 서버에서 가져왔습니다! 밤 10시에 만나요. 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
