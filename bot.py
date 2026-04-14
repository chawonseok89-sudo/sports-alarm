import os
import asyncio
import telegram
import requests
from datetime import datetime

def get_kbo_rank():
    try:
        # KBO 팀순위 페이지의 원본 데이터 주소
        url = "https://sports-api.naver.com/kbaseball/record/team?year=2026"
        res = requests.get(url).json()
        for team in res['teamRecordList']:
            if "KIA" in team['name']:
                return f"{team['rank']}위 ({team['won']}승 {team['drawn']}무 {team['lost']}패 / 게임차: {team['gameDiff']})"
        return "순위 정보 없음"
    except:
        return "데이터 수집 중"

def get_kleague_rank():
    try:
        # K리그1 팀순위 페이지의 원본 데이터 주소
        url = "https://sports-api.naver.com/kfootball/record/team?year=2026&leagueId=K1"
        res = requests.get(url).json()
        for team in res['teamRecordList']:
            if "전북" in team['name']:
                return f"{team['rank']}위 (승점 {team['point']}점 / {team['won']}승 {team['drawn']}무 {team['lost']}패)"
        return "순위 정보 없음"
    except:
        return "데이터 수집 중"

def get_match_status(team_name, category):
    try:
        today = datetime.now().strftime('%Y%m%d')
        # 야구/축구 일정 데이터 주소
        url = f"https://sports-api.naver.com/{category}/schedule?date={today}"
        res = requests.get(url).json()
        
        # 오늘 경기 목록에서 우리 팀 찾기
        for game in res.get('todayScheduleList', []):
            if team_name in [game['homeTeamName'], game['awayTeamName']]:
                state = game['state'] # 종료, 진행중, 예정 등
                h_team = game['homeTeamName']
                a_team = game['awayTeamName']
                h_score = game['homeTeamScore']
                a_score = game['awayTeamScore']
                return f"[{state}] {h_team} {h_score} : {a_score} {a_team}"
        return "오늘 예정된 경기 없음"
    except:
        return "경기 정보 업데이트 중"

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 각각의 순위와 경기 정보를 가져옴
    kia_rank = get_kbo_rank()
    kia_match = get_match_status("KIA", "kbaseball")
    
    jb_rank = get_kleague_rank()
    jb_match = get_match_status("전북", "kfootball")
    
    today_str = datetime.now().strftime('%m%d')
    kia_yt = f"https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}"
    jb_yt = f"https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}"

    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n🏆 현재순위: {kia_rank}\n📊 경기결과: {kia_match}\n📺 영상: {kia_yt}\n\n"
        f"⚽ [전북 현대]\n🏆 현재순위: {jb_rank}\n📊 경기결과: {jb_match}\n📺 영상: {jb_yt}\n\n"
        f"말씀하신 순위표 데이터를 직접 가져왔습니다! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
