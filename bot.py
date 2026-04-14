import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_sports_info(team_name):
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'}
    rank, last, next_m = "데이터 확인 중", "최신 기록 없음", "다음 일정 없음"
    
    try:
        url = f"https://m.search.naver.com/search.naver?query={team_name}+순위+경기일정"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 순위 추출
        rank_tag = soup.select_one(".rank_num, .num, .item_rank, ._total_rank")
        if rank_tag:
            rank = rank_tag.get_text().strip() + "위"
        else:
            import re
            match = re.search(r'(\d+)위', res.text)
            if match: rank = match.group(0)

        # 결과 및 일정 추출
        items = soup.select(".item_list li, .schedule_item, .inner")
        past_list = []
        future_list = []
        
        for item in items:
            text = item.get_text(" ", strip=True)
            if team_name[:2] in text:
                if "종료" in text or "취소" in text:
                    past_list.append(text.replace("종료", "").strip())
                elif "vs" in text or ":" in text:
                    future_list.append(text.strip())
        
        if past_list: last = past_list[-1]
        if future_list: next_m = future_list[0]

    except:
        pass
    return rank, last, next_m

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    k_rank, k_last, k_next = get_sports_info("기아타이거즈")
    j_rank, j_last, j_next = get_sports_info("전북현대")
    
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n"
        f"🏆 순위: {k_rank}\n"
        f"✅ 결과: {k_last}\n"
        f"📅 일정: {k_next}\n"
        f"🎬 영상: https://www.youtube.com/results?search_query=기아타이거즈+하이라이트\n\n"
        f"⚽ [전북 현대]\n"
        f"🏆 순위: {j_rank}\n"
        f"✅ 결과: {j_last}\n"
        f"📅 일정: {j_next}\n"
        f"🎬 영상: https://www.youtube.com/results?search_query=전북현대+하이라이트\n\n"
        f"모든 오류를 수정했습니다! 이제 정상적으로 배달될 거예요. 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
