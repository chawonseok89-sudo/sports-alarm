import os
import asyncio
import telegram
from datetime import datetime

async def send_news():
    # 저장해둔 비밀 정보를 가져옵니다
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=token)

    # 메시지 내용 (여기에 뉴스 추출 로직이 들어가면 더 좋습니다)
    text = f"📅 {datetime.now().strftime('%Y-%m-%d')} 알림\n\n" \
           f"🐯 기아 타이거즈 & ⚽ 전북 현대 소식\n" \
           f"오늘의 하이라이트를 확인해보세요!\n\n" \
           f"🔗 유튜브: https://www.youtube.com/results?search_query=기아타이거즈+하이라이트"
    
    await bot.send_message(chat_id=chat_id, text=text)

if __name__ == "__main__":
    asyncio.run(send_news())
