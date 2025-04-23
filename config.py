import os
from dotenv import load_dotenv
from redis import Redis


load_dotenv()

RD_HOST = os.getenv("RD_HOST")
RD_PORT = os.getenv("RD_PORT")
RD_DB = os.getenv("RD_DB")

rd = Redis(host=RD_HOST, port=RD_PORT, db=RD_DB, decode_responses=True)