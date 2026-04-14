import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def get_sports_rank(query, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
        # 검색 결과 페이지 접속
        url = f"https://search.naver.com/search.naver?query={query}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 테이블 형태의 데이터 먼저 탐색
        rows = soup.find_all('tr')
        for row in rows:
            if team_name in row.text:
                # 팀 이름이 포함된 행에서 '위'라는 글자가 포함된 텍스트 추출
                cells = row.find_all(['th', 'td'])
                for cell in cells:
                    cell_text = cell.text.strip()
                    if '위' in cell_text or cell_text.isdigit():
                        return f"{cell_text if '위' in cell_text else cell_text + '위'}"
        
        # 2. 텍스트 패턴 매칭 (최후의 수단)
        # "기아 1위" 또는 "1위 KIA" 같은 패턴을 찾음
        pattern = re.compile(rf"{team_name}.*?(\d+위)|(\d+위).*?{team_name}")
        match = pattern.search(res.text)
        if match:
            return match.group(1) or match.group(2)

        return "순위 확인 중"
    except:
        return "데이터 확인 불가"

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 검색어를 더 정확하게 입력 (리그 전체 순위표를 불러오도록)
    kia_rank = get_sports_rank("KBO 순위", "기아")
    jb_rank = get_sports_rank("K리그1 순위", "전북")
    
    # 경기 결과는 기존 방식 유지
    url_base = "https://search.naver.com/search.naver?query="
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    k_res = requests.get(url_base + "기아타이거즈+경기결과", headers=headers)
    j_res = requests.get(url_base + "전북현대+경기결과", headers=headers)
    
    k_soup = BeautifulSoup(k_res.text, 'html.parser')
    j_soup = BeautifulSoup(j_res.text, 'html.parser')
    
    k_status = k_soup.select_one(".status_area").text.strip() if k_soup.select_one(".status_area") else "경기 없음"
    k_score = k_soup.select_one(".score_area").text.strip() if k_soup.select_one(".score_area") else ""
    
    j_status = j_soup.select_one(".status_area").text.strip() if j_soup.select_one(".status_area") else "경기 없음"
    j_score = j_soup.select_one(".score_area").text.strip() if j_soup.select_one(".score_area") else ""

    today_str = datetime.now().strftime('%m%d')
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n🏆 현재순위: {kia_rank}\n📊 경기결과: [{k_status}] {k_score}\n"
        f"📺 영상: https://www.youtube.com/results?search_query=기아타이거즈+하이라이트+{today_str}\n\n"
        f"⚽ [전북 현대]\n🏆 현재순위: {jb_rank}\n📊 경기결과: [{j_status}] {j_score}\n"
        f"📺 영상: https://www.youtube.com/results?search_query=전북현대+하이라이트+{today_str}\n\n"
        f"검색 요약 정보를 활용해 정확도를 높였습니다! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
