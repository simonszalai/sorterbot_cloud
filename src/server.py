"""
WebSockets server that listens to messages from the Raspberry Pis and calls the appropriate functions.

"""

import os
# import ssl
import json
import asyncio
import websockets
from pathlib import Path
from fnmatch import fnmatch
import multiprocessing as mp

from main import Main
from utils.logger import logger


class WebSockets:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.main = Main(base_img_path=Path(__file__).resolve().parents[1].joinpath("images"))
        self.img_meta = {}
        self.port = 6000

        # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # localhost_pem = Path(__file__).parent.parent.joinpath("ssl", "cert.pem")
        # ssl_context.load_cert_chain(localhost_pem)

        start_server = websockets.serve(self.listen, "0.0.0.0", self.port, max_size=2048576, max_queue=None)
        print(f"SorterBot Cloud WebSocket server starting on port {self.port}.")
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    async def listen(self, websocket, path):
        """
        Function that listens to new WebSocket messages. It can handle bytes and JSON messages.
        Supported message types: recv_img_proc, recv_img_after, get_commands_of_session, stitch_after_image.

        Parameters
        ----------
        websocket : WebSocket
            WebSocket instance provided by websockets.serve
        path : str
            Unused.
        """

        async for message in websocket:
            if isinstance(message, bytes):
                # Split headers from the image
                split_msg = message.split(b"___SPLIT___")
                headers = json.loads(split_msg[0])
                content = split_msg[1]
                # Handle case when message contains bytes asspended to JSON headers
                if headers["command"] == "recv_img_proc":
                    # Detect objects on image and save bounding boxes to the database
                    success = self.main.process_image(
                        arm_id=headers["arm_id"],
                        session_id=headers["session_id"],
                        image_name=headers["image_name"],
                        img_bytes=content
                    )
                    # Send back to Raspberry if processing was successful
                    await websocket.send(json.dumps(success))
                elif headers["command"] == "recv_img_after":
                    img_disk_path = Path(self.main.base_img_path).joinpath(headers["session_id"], "after", headers["image_name"])
                    img_s3_path = f'{headers["arm_id"]}/{headers["session_id"]}/after_{headers["image_name"]}'
                    success = self.main.save_and_upload_image(img_disk_path, img_s3_path, content, {})
                    # Send back to Raspberry if processing was successful
                    await websocket.send(json.dumps(success))

            else:
                # Handle case with only JSON data
                message = json.loads(message)

                if message["command"] == "get_commands_of_session":
                    # Process session images to get commands
                    commands, _, stitching_process = self.main.vectorize_session_images(message["arm_constants"], message["session_id"])

                    # Send back to calculated commands
                    await websocket.send(json.dumps(commands))

                    # Join to process used for stitching here to avoid unneccesary waiting
                    # stitching_process.join()
                elif message["command"] == "stitch_after_image":
                    try:
                        img_disk_path = Path(self.main.base_img_path).joinpath(message["session_id"], "after")
                        after_images = []
                        for path, subdirs, files in os.walk(img_disk_path):
                            for name in files:
                                if fnmatch(name, "*.jpg"):
                                    after_images.append(name)

                        # stitching_process = mp.Process(target=self.main.stitch_images, args=(message["arm_id"], message["session_id"], "after", after_images))
                        # stitching_process.start()
                        # stitching_process.join()
                        self.main.stitch_images(message["arm_id"], message["session_id"], "after", after_images)
                    except Exception as e:
                        print("stitch_after_image", e)
                else:
                    print("A message arrived with a payload that was not JSON parsable and there was no handler for it.")


if __name__ == "__main__":
    WebSockets()
