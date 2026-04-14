import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_sports_data(category, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        # 검색어 최적화 (축구는 리그명을 넣어야 엉뚱한 팀이 안 나옵니다)
        query = "2026 KBO 순위" if category == "base" else "2026 K리그1 순위"
        url = f"https://search.naver.com/search.naver?query={query}"
        
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 순위 정보 추출: 테이블 내에서 팀명을 직접 찾음
        rank = "순위 확인 불가"
        rows = soup.select("table tbody tr")
        for row in rows:
            if team_name in row.text:
                rank = row.select_one("th, td.rank, .num").text.strip() + "위"
                break

        # 경기 정보 추출: 이번에는 팀명을 포함해서 다시 검색 (정확도 향상)
        match_url = f"https://search.naver.com/search.naver?query={team_name}+경기결과"
        m_res = requests.get(match_url, headers=headers)
        m_soup = BeautifulSoup(m_res.text, 'html.parser')
        
        status = "경기 없음"
        score = ""
        status_tag = m_soup.select_one(".status_area, .state")
        score_tag = m_soup.select_one(".score_area, .score")
        
        if status_tag:
            # 타 팀 정보가 섞이지 않도록 체크
            if team_name in m_soup.select_one(".lst_team, .vs_area").text:
                status = status_tag.text.strip()
                score = score_tag.text.strip() if score_tag else ""
            
        return rank, f"[{status}] {score}"
    except:
        return "확인 불가", "정보 없음"

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 데이터 수집 (KIA는 'KIA', 전북은 '전북'으로 검색)
    kia_rank, kia_match = get_sports_data("base", "KIA")
    jb_rank, jb_match = get_sports_data("foot", "전북")
    
    today_str = datetime.now().strftime('%m%d')
    kia_yt = f"https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}"
    jb_yt = f"https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}"

    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n🏆 현재순위: {kia_rank}\n📊 경기결과: {kia_match}\n📺 영상: {kia_yt}\n\n"
        f"⚽ [전북 현대]\n🏆 현재순위: {jb_rank}\n📊 경기결과: {jb_match}\n📺 영상: {jb_yt}\n\n"
        f"정확한 정보로 업데이트했습니다! 오늘 밤 10시에 만나요. 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
