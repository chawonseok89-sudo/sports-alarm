import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_sports_data(query, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        url = f"https://search.naver.com/search.naver?query={query}+순위"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 순위 정보 추출 (여러 패턴 시도)
        rank = "순위 확인 불가"
        # 패턴 A: 검색 결과 상단 큰 글씨
        rank_tag = soup.select_one(".rank_num, .num, .item_rank, ._total_rank")
        if rank_tag:
            rank = rank_tag.text.strip()
        # 패턴 B: 테이블 내 텍스트 검색
        elif team_name in res.text:
            rank_idx = res.text.find(team_name)
            # 팀명 주변에서 '위'라는 글자 찾기
            snippet = res.text[max(0, rank_idx-20):rank_idx+20]
            if "위" in snippet:
                rank = snippet.split("위")[0].split()[-1] + "위"

        # 2. 경기 정보 추출
        status = "경기 없음"
        score = ""
        status_tag = soup.select_one(".status_area, .state")
        score_tag = soup.select_one(".score_area, .score")
        
        if status_tag:
            status = status_tag.text.strip()
        if score_tag:
            score = score_tag.text.strip()
            
        return rank, f"[{status}] {score}"
    except:
        return "데이터 오류", "업데이트 중"

async def send_sports_report():
    # GitHub Secrets 설정 확인
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id:
        print("설정 오류: TOKEN이나 CHAT_ID를 확인하세요.")
        return

    bot = telegram.Bot(token=token)

    # 데이터 수집 (쿼리를 더 명확하게 수정)
    kia_rank, kia_match = get_sports_data("2026 KBO 순위", "KIA")
    jb_rank, jb_match = get_sports_data("2026 K리그 순위", "전북")
    
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
        f"오늘도 고생하셨습니다! 밤 10시에 만나요. 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
