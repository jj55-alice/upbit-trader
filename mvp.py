import os
from dotenv import load_dotenv
import json
load_dotenv()

def ai_trading():
    # 업비트 차트 데이터 가져오기
    import pyupbit
    df = pyupbit.get_ohlcv("KRW-XRP", count=30, interval="day")

    # 오픈 AI에게 데이터 제공하고 판단 받기
    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are an expert in Bitcoin investing.
    Tell me whether to buy, sell, or hold based on the chart data.

    Respond ONLY in valid JSON format like this:
    {"decision": "buy", "reason": "some technical reason"}
    """
            },
            {
                "role": "user",
                "content": df.to_json()
            }
        ],
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content
    result = json.loads(result)

    access = os.getenv("UPBIT_ACCESS_KEY")
    secret = os.getenv("UPBIT_SECRET_KEY")
    upbit = pyupbit.Upbit(access, secret)

    print("### AI Decision: ", result['decision'].upper(), "###")
    print("### Reason: ", result['reason'], "###")


    if result['decision'] == "buy":
        # 매수
        print(upbit.buy_market_order("KRW-XRP", 10000))
        print("### Buy Excuted ###")
    elif result['decision'] == "sell":
        # 매도
        my_xrp = upbit.get_balance("KRW-XRP")
        current_price = pyupbit.get_orderbook(ticket="KRW-XRP")['orderbook_units'][0]['ask_price']

        if(my_xrp * current_price > 5000) :
            print(upbit.sell_market_order("KRW-XRP", my_xrp))
            print("### Sell Excuted ###")
        else :
            print("### Sell Order Failed ###")
    elif result['decision'] == "hold":
        print("hold:", result["reason"])

while True:
    import time
    time.sleep(10)
    ai_trading()