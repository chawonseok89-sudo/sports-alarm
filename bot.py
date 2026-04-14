import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 경기 정보 및 순위 통합 추출 (네이버 검색 활용)
def get_sports_data(team_query, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # 네이버에 '팀명 순위'로 검색
        url = f"https://search.naver.com/search.naver?query={team_query}+순위"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 순위 정보 찾기 (검색 결과 상단 스코어보드/순위표 타겟)
        rank_area = soup.select_one(".rank_num, .num, .item_rank")
        if not rank_area: # 대체 경로
            rank_area = soup.select_one(".table_group.type_rank")
            
        # 경기 정보 찾기
        status_area = soup.select_one(".status_area")
        score_area = soup.select_one(".score_area")

        # 데이터 정리
        status = status_area.text.strip() if status_area else "경기 없음"
        score = score_area.text.strip() if score_area else ""
        
        # 순위 텍스트 정리 (예: 1위)
        rank = "순위 정보 확인 중"
        if rank_area:
            rank_text = rank_area.text.strip().split('\n')[0]
            rank = f"{rank_text}"
        
        return f"{rank}", f"[{status}] {score}"
    except:
        return "순위 확인 중", "정보 업데이트 중"

async def send_sports_report():
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=token)

    # 데이터 수집
    kia_rank, kia_match = get_sports_data("기아타이거즈", "KIA")
    jb_rank, jb_match = get_sports_data("전북현대", "전북")
    
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
        f"밤 10시 알림 설정 완료! 오늘도 고생하셨습니다. 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
