import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_sports_all_in_one(query, team_keyword):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    # 1. 순위 찾기
    rank = "확인 불가"
    try:
        r_res = requests.get(f"https://search.naver.com/search.naver?query={query}+순위", headers=headers)
        r_soup = BeautifulSoup(r_res.text, 'html.parser')
        rows = r_soup.select("table tbody tr")
        for row in rows:
            if team_keyword in row.text:
                rank_tag = row.select_one("th, td")
                if rank_tag:
                    rank = rank_tag.text.strip() + "위"
                break
    except:
        rank = "확인 불가"

    # 2. 최근 결과 및 다음 일정 찾기
    last_game = "기록 없음"
    next_game = "일정 없음"
    video_link = f"https://www.youtube.com/results?search_query={team_keyword}+하이라이트"
    
    try:
        m_res = requests.get(f"https://search.naver.com/search.naver?query={team_keyword}+경기일정", headers=headers)
        m_soup = BeautifulSoup(m_res.text, 'html.parser')
        
        past_matches = []
        future_matches = []
        
        # 경기 목록에서 종료 여부 확인
        for m in m_soup.select(".inner, .schedule_item"):
            m_text = m.get_text(separator=" ").strip()
            if "종료" in m_text:
                past_matches.append(m_text)
            elif "vs" in m_text or ":" in m_text:
                future_matches.append(m_text)
        
        if past_matches:
            last_game = past_matches[-1].split("종료")[0].strip()
            # 하이라이트 링크를 최근 경기 팀명 조합으로 생성
            video_link = f"https://www.youtube.com/results?search_query={last_game.replace(' ', '+')}+하이라이트"
            
        if future_matches:
            next_game = future_matches[0].strip()
    except:
        pass

    return rank, last_game, next_game, video_link

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 데이터 수집
    k_rank, k_last, k_next, k_vid = get_sports_all_in_one("KBO", "기아타이거즈")
    j_rank, j_last, j_next, j_vid = get_sports_all_in_one("K리그1", "전북현대")
    
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n"
        f"🏆 현재순위: {k_rank}\n"
        f"✅ 최근결과: {k_last}\n"
        f"📅 다음일정: {k_next}\n"
        f"🎬 하이라이트: {k_vid}\n\n"
        f"⚽ [전북 현대]\n"
        f"🏆 현재순위: {j_rank}\n"
        f"✅ 최근결과: {j_last}\n"
        f"📅 다음일정: {j_next}\n"
        f"🎬 하이라이트: {j_vid}\n\n"
        f"밤 10시 알림에서 뵙겠습니다! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
