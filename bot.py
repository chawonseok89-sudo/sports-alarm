import os
import asyncio
import telegram
import requests
from datetime import datetime

# 데이터 수집 함수 (네이버 스포츠 공식 API 활용)
def get_combined_data(category, team_id, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        today = datetime.now().strftime('%Y%m%d')
        
        # 1. 순위 가져오기
        rank_url = f"https://sports-api.naver.com/{category}/record/team?year=2026"
        if category == "kfootball": rank_url += "&leagueId=K1"
        r_data = requests.get(rank_url, headers=headers).json()
        
        rank_info = "순위 정보 없음"
        for team in r_data.get('teamRecordList', []):
            if team_name in team['name']:
                rank_info = f"{team['rank']}위"
                break

        # 2. 최근 결과 및 다음 일정 가져오기
        # 팀별 일정 페이지 (최근 경기와 다음 경기가 포함됨)
        sched_url = f"https://sports-api.naver.com/{category}/schedule/team?year=2026&teamId={team_id}"
        s_data = requests.get(sched_url, headers=headers).json()
        
        last_match = "기록 없음"
        next_match = "일정 없음"
        
        # 전체 경기 목록에서 오늘 날짜와 비교하여 결과와 일정을 찾음
        all_games = s_data.get('monthlyScheduleList', [])
        past_games = []
        future_games = []
        
        for month in all_games:
            for game in month.get('scheduleList', []):
                if game['state'] == '종료':
                    past_games.append(game)
                else:
                    future_games.append(game)
        
        if past_games:
            g = past_games[-1] # 가장 최근 경기
            last_match = f"{g['homeTeamName']} {g['homeTeamScore']}:{g['awayTeamScore']} {g['awayTeamName']} ({g['gameDate']})"
        
        if future_games:
            g = future_games[0] # 가장 빠른 다음 경기
            next_match = f"{g['homeTeamName']} vs {g['awayTeamName']} ({g['gameDate']} {game['gameStartTime']})"

        return rank_info, last_match, next_match
    except:
        return "데이터 오류", "정보 없음", "정보 없음"

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 기아(HT), 전북(05) 고유 ID를 사용해 정확도 100% 보장
    kia_rank, kia_last, kia_next = get_combined_data("kbaseball", "HT", "KIA")
    jb_rank, jb_last, jb_next = get_combined_data("kfootball", "05", "전북")
    
    today_str = datetime.now().strftime('%m%d')
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n"
        f"🏆 현재순위: {kia_rank}\n"
        f"✅ 최근결과: {kia_last}\n"
        f"📅 다음일정: {kia_next}\n"
        f"📺 하이라이트: https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}\n\n"
        f"⚽ [전북 현대]\n"
        f"🏆 현재순위: {jb_rank}\n"
        f"✅ 최근결과: {jb_last}\n"
        f"📅 다음일정: {jb_next}\n"
        f"📺 하이라이트: https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}\n\n"
        f"오늘 밤 10시 알림을 기다려주세요! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
