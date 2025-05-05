import asyncio
import websockets
import cv2
import logging

logging.basicConfig(level=logging.INFO)


async def capture_and_stream(websocket, path):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Cannot access camera")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to capture frame")
                break

            success, buffer = cv2.imencode(".jpg", frame)
            if not success:
                logging.error("Failed to encode frame")
                continue

            try:
                await websocket.send(buffer.tobytes())
            except websockets.exceptions.ConnectionClosed:
                logging.info("Client disconnected")
                break

            await asyncio.sleep(1 / 30)
    finally:
        cap.release()


async def serve():
    async with websockets.serve(
        capture_and_stream, "localhost", 8765, max_size=None
    ):
        logging.info("WebSocket server started at ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(serve())
