import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_sports_details(team_name, category_path):
    # 아이폰 모바일 브라우저인 척 하여 접근성을 높입니다.
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'}
    
    rank, last_game, next_game = "확인 불가", "기록 없음", "일정 없음"
    
    try:
        # 1. 순위 가져오기 (통합 검색)
        rank_url = f"https://m.search.naver.com/search.naver?query={team_name}+순위"
        r_res = requests.get(rank_url, headers=headers)
        r_soup = BeautifulSoup(r_res.text, 'html.parser')
        rank_tag = r_soup.select_one(".rank_num, .num, .item_rank")
        if rank_tag: rank = rank_tag.text.strip() + "위"

        # 2. 최근 결과 및 다음 일정 (네이버 스포츠 팀별 일정 페이지)
        # category_path 예: kbaseball, kfootball
        schedule_url = f"https://m.sports.naver.com/{category_path}/schedule/index"
        s_res = requests.get(schedule_url, headers=headers)
        s_soup = BeautifulSoup(s_res.text, 'html.parser')
        
        # 경기 목록(리스트)을 다 긁어옵니다.
        matches = s_soup.select(".ScheduleAllType_match_list_group__3Tafm, .MatchBox_match_item__2Wp9o")
        
        past = []
        future = []
        
        for m in s_soup.select(".ScheduleAllType_match_list_item__3n08h, .match_item"):
            m_text = m.get_text(separator=" ").strip()
            if team_name[:2] in m_text: # 팀명이 포함된 경기만
                if "종료" in m_text or "취소" in m_text:
                    past.append(m_text)
                else:
                    future.append(m_text)
        
        if past: last_game = past[-1].replace("종료", "[종료]").strip()
        if future: next_game = future[0].strip()

    except:
        pass
        
    return rank, last_game, next_game

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 데이터 수집 (기아는 kbaseball, 전북은 kfootball)
    k_rank, k_last, k_next = get_sports_details("기아타이거즈", "kbaseball")
    j_rank, j_last, j_next = get_sports_details("전북현대", "kfootball")
    
    # 하이라이트 링크 (최근 경기 팀들 이름으로 검색)
    k_vid_query = k_last.replace("[종료]", "").strip() if "기록" not in k_last else "기아타이거즈"
    j_vid_query = j_last.replace("[종료]", "").strip() if "기록" not in j_last else "전북현대"
    
    k_vid = f"https://www.youtube.com/results?search_query={k_vid_query.replace(' ', '+')}+하이라이트"
    j_vid = f"https://www.youtube.com/results?search_query={j_vid_query.replace(' ', '+')}+하이라이트"
    
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
        f"오늘 밤 10시에 자동으로 배달됩니다! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
