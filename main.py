import os
import json
import requests
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage

def getWeatherData():
    cityName = "Yashio"
    ApiKey = os.environ.get("WEATHER_API_KEY")
    api = "http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"

    url = api.format(city=cityName, key=ApiKey)

    apiResponse = requests.get(url)
    
    return apiResponse.json()


def ConvertWeatherName(weatherInfo):
    # print("▼ OpenWeatherMapからの応答データ ▼")
    # print(weatherInfo)
    # print("--------------------------------")

    # APIエラー時など、"weather" キーが存在しない場合の安全対策
    if "weather" not in weatherInfo:
        print("❌ エラー: 天気データが取得できませんでした（APIキーが無効、またはURLに誤りがあります）。")
        return "取得エラー"

    weather = weatherInfo["weather"][0]["icon"]

    icon_num = weather[:2]
    
    if icon_num in ("01", "02"):
        text = "晴れ"
    elif icon_num in ("03", "04"):
        text = "くもり"
    elif icon_num in ("09", "10"):
        text = "雨"
    elif icon_num == "11":
        text = "雷雨"
    elif icon_num == "13":
        text = "雪"
    elif icon_num == "50":
        text = "霧"
    else:
        text = "謎の天気"
        
    return text


def CreateWeatherMessage():
    weatherInfo = getWeatherData()
    
    # 修正1: ConvertWeatherName関数を呼び出して天気テキストを取得します
    weatherText = ConvertWeatherName(weatherInfo)

    # 天気テキストが「取得エラー」だった場合は、気温などの処理をスキップしてそのままエラーを返します
    if weatherText == "取得エラー":
        return "天気の取得に失敗しました。APIキーを確認してください。"
    
    tempMax = round(weatherInfo["main"]["temp_max"])
    tempMin = round(weatherInfo["main"]["temp_min"])
    humidity = weatherInfo["main"]["humidity"]
    pressure = weatherInfo["main"]["pressure"]
    
    if weatherText == "雨" or weatherText == "雷雨":
        greeting = "雨が降っているよ。洗濯物を取り込もう！☔️"
    elif weatherText == "雪":
        greeting = "雪が降っているよ。雪だるまを作ろう！⛄️"
    else:
        greeting = "今の天気をお知らせするよ！☀️"
    
    message = [
        f"{greeting}\n\n天気：{weatherText}\n最高気温：{tempMax}℃\n最低気温：{tempMin}℃\n湿度：{humidity}%\n気圧：{pressure}hpa\nだよ！"
    ]
    return message


def main():
    # 環境変数から値を取得
    CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
    USER_ID = os.environ.get("USER_ID")

    # 【重要】環境変数が正しくセットされているかチェック
    if not CHANNEL_ACCESS_TOKEN:
        raise ValueError("❌ エラー: CHANNEL_ACCESS_TOKEN が環境変数から取得できません。GitHub Secretsの設定を確認してください。")
    if not USER_ID:
        raise ValueError("❌ エラー: USER_ID が環境変数から取得できません。GitHub Secretsの設定を確認してください。")

    message_text = CreateWeatherMessage()
    
    # LINE SDK v3 を使ったメッセージ送信
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        push_message_request = PushMessageRequest(
            to=USER_ID,
            messages=[TextMessage(text=message_text)]
        )
        line_bot_api.push_message(push_message_request)
    
    print("✅ LINEにメッセージを送信しました！")


if __name__ == "__main__":
    main()