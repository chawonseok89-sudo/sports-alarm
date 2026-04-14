import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_sports_data(team_name, category_id):
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'}
    
    rank, last_game, next_game = "확인 불가", "기록 없음", "일정 없음"
    
    try:
        # 네이버 모바일 검색 활용 (데이터가 더 깔끔함)
        url = f"https://m.search.naver.com/search.naver?query={team_name}+순위+일정"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 1. 순위 추출
        rank_tag = soup.select_one(".rank_num, .num, .item_rank")
        if rank_tag:
            rank = rank_tag.text.strip() + "위"
        elif team_name in res.text:
            # 텍스트에서 강제로 순위 찾기
            import re
            match = re.search(r'(\d+)위', res.text)
            if match: rank = match.group(0)

        # 2. 최근 경기 및 다음 일정 추출
        matches = soup.select(".item_list li, .schedule_item")
        for m in matches:
            m_text = m.get_text(separator=" ").strip()
            if "종료" in m_text:
                last_game = m_text.split("종료")[0].strip()
            elif "전" in m_text or ":" in m_text or "vs" in m_text:
                if next_game == "일정 없음":
                    next_game = m_text.strip()
                    
    except Exception as e:
        print(f"Error: {e}")
        
    return rank, last_game, next_game

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 기아와 전북 데이터 가져오기
    k_rank, k_last, k_next = get_sports_data("기아타이거즈", "kbaseball")
    j_rank, j_last, j_next = get_sports_data("전북현대", "kfootball")
    
    # 하이라이트 링크는 최근 경기가 있으면 해당 팀들로, 없으면 기본 팀명으로 생성
    k_vid = f"https://www.youtube.com/results?search_query={k_last.replace(' ', '+') if '기록 없음' not in k_last else '기아타이거즈'}+하이라이트"
    j_vid = f"https://www.youtube.com/results?search_query={j_last.replace(' ', '+') if '기록 없음' not in j_last else '전북현대'}+하이라이트"
    
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
        f"밤 10시 정각에 자동으로 배달됩니다! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
