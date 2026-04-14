import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_sports_data(category, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        # 1. 순위 정보 추출 (리그 명시로 정확도 향상)
        query = "2026 KBO 순위" if category == "base" else "2026 K리그1 순위"
        url = f"https://search.naver.com/search.naver?query={query}"
        
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        rank = "순위 확인 불가"
        # 테이블 행(tr)을 돌며 팀 이름을 찾습니다.
        rows = soup.select("table tbody tr")
        for row in rows:
            if team_name in row.text:
                # 순위가 적힌 칸(th 또는 특정 td)을 찾아 텍스트를 가져옵니다.
                rank_num = row.select_one("th, td.rank, .num").text.strip()
                rank = f"{rank_num}위"
                break

        # 2. 경기 정보 추출 (팀명을 포함해 재검색)
        match_url = f"https://search.naver.com/search.naver?query={team_name}+경기결과"
        m_res = requests.get(match_url, headers=headers)
        m_soup = BeautifulSoup(m_res.text, 'html.parser')
        
        status = "경기 없음"
        score = ""
        
        # 경기 상태와 스코어 영역 탐색
        status_tag = m_soup.select_one(".status_area, .state")
        score_tag = m_soup.select_one(".score_area, .score")
        vs_area = m_soup.select_one(".lst_team, .vs_area, .score_board")

        if status_tag and vs_area:
            # 검색 결과에 '진짜' 우리 팀 이름이 있는지 한 번 더 확인 (타 팀 방지)
            if team_name in vs_area.text:
                status = status_tag.text.strip()
                score = score_area.text.strip() if score_tag else ""
            
        return rank, f"[{status}] {score}"
    except:
        return "확인 불가", "정보 없음"

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 데이터 수집 (기아는 'KIA', 전북은 '전북' 키워드 사용)
    kia_rank, kia_match = get_sports_data("base", "KIA")
    jb_rank, jb_match = get_sports_data("foot", "전북")
    
    today_str = datetime.now().strftime('%m%d')
    kia_yt = f"https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}"
    jb_yt = f"https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}"

    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n🏆 현재순위: {kia_rank}\n📊 경기결과: {kia_match}\n📺 영상: {kia_yt}\n\n"
        f"⚽ [전북 현대]\n🏆 현재순위: {jb_rank}\n📊 경기결과: {jb_match}\n📺 영상: {jb_yt}\n\n"
        f"이제 전북 현대 소식도 정확히 배달될 거예요! 오늘 밤 10시에 확인해 보세요. 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
