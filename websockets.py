import websocket
import json

def on_message(ws, message):
    print(f"Received: {message}")

ws = websocket.WebSocketApp("wss://stream.data.alpaca.markets/v2/sip",
                             on_message=on_message)
ws.run_forever()
