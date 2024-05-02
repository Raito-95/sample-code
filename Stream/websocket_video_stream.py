import asyncio
import websockets
import cv2
import logging
import base64

logging.basicConfig(level=logging.INFO)

async def capture_and_stream(websocket, path):
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to capture frame")
            break

        _, buffer = cv2.imencode('.jpeg', frame)
        base64_str = base64.b64encode(buffer).decode('utf-8')

        try:
            await websocket.send(base64_str)
            logging.info("Frame sent to client")
        except Exception as e:
            logging.error("Failed to send frame: %s", e)
            break

    cap.release()

async def serve():
    async with websockets.serve(capture_and_stream, "localhost", 8765):
        logging.info("WebSocket server started")
        await asyncio.Future()

asyncio.run(serve())
