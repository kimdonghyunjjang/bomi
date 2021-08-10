import pyupbit
import time
import datetime
import requests


access = ""
secret = ""
myToken = ""

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )


def cal_target(ticker):
  df = pyupbit.get_ohlcv(ticker, "day")
  yesterday = df.iloc[-2]
  today = df.iloc[-1]
  yesterday_range = yesterday['high']-yesterday['low']
  target = today['open'] + yesterday_range * 0.5
  return target

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#bitbomi", "autotrade start")

#변수 설정
target = cal_target("KRW-BTC")
op_mode = False
hold = False

while True:
   now = datetime.datetime.now()
   
   # 매도 시도
   if now.hour == 8 and now.minute ==59 and 50 <= now.second <= 59: 
       if op_mode is True and hold is True:
          btc_balance = upbit.get_balance("KRW-BTC")
          sell_result = upbit.sell_market_order("KRW-BTC", btc_balance)
          hold = False
          post_message(myToken,"#bitbomi", "BTC sell : " +str(sell_result))
       op_mode = False
       time.sleep(10)

   # 09:00:00 목표가 갱신
   if now.hour == 9 and now.minute == 0 and 20 <= now.second <= 30:   
       target = cal_target("KRW-BTC")
       op_mode = True
       time.sleep(10)  #09:00:20 ~ 31
   
   price = pyupbit.get_current_price("KRW-BTC")
   
   # 매초마다 조건을 확인한 후 매수 시도
   if op_mode is True and price is not None and price >= target and hold is False:
      # 매수
      krw_balance = upbit.get_balance("KRW")
      buy_result = upbit.buy_market_order("KRW-BTC", krw_balance)
      hold = True   
      post_message(myToken,"#bitbomi", "BTC buy : " +str(buy_result))
  
   #상태 출력
   print(f"현재시간: {now} 목표가: {target} 현재가: {price} 보유상태: {hold} 동작상태: {op_mode}")
  
   time.sleep(3600)
