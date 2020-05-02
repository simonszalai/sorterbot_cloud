import json
import asyncio
import websockets
from pathlib import Path

from main import Main
from utils.logger import logger


class WebSockets:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.main = Main(base_img_path=Path(__file__).parent.parent.joinpath("images"))
        self.img_meta = {}

        start_server = websockets.serve(self.listen, "0.0.0.0", 7000, max_size=2048576)
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    async def listen(self, websocket, path):
        async for message in websocket:
            if isinstance(message, bytes):
                if websocket.request_headers["command"] == "recv_img":
                    # Detect objects on image and save bounding boxes to the database
                    success = self.main.process_image(
                        arm_id=websocket.request_headers["arm_id"],
                        session_id=websocket.request_headers["session_id"],
                        image_name=websocket.request_headers["image_name"],
                        img_bytes=message
                    )
                    # Send back to Raspberry if processing was successful
                    await websocket.send(json.dumps(success))
                else:
                    print("A message arrived with a payload that was not JSON parsable and there was no handler for it.")
            else:
                message = json.loads(message)
                if message["command"] == "get_commands_of_session":
                    print("get_commands_of_session")
                    commands, _ = self.main.vectorize_session_images(arm_constants=message["arm_constants"], session_id=message["session_id"])
                    await websocket.send(json.dumps(commands))


if __name__ == "__main__":
    WebSockets()
