import hashlib
import datetime
import json
import os

FILE_NAME = "blockchain.json"

class Block:
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.create_hash()

    def create_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.data}{self.prev_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "prev_hash": self.prev_hash,
            "hash": self.hash
        }


class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_chain()

    def create_genesis_block(self):
        return Block(0, str(datetime.datetime.now()), "Genesis Block", "0")

    def load_chain(self):
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r") as f:
                data = json.load(f)
                for block in data:
                    self.chain.append(
                        Block(
                            block["index"],
                            block["timestamp"],
                            block["data"],
                            block["prev_hash"]
                        )
                    )
        else:
            genesis = self.create_genesis_block()
            self.chain.append(genesis)
            self.save_chain()

    def save_chain(self):
        with open(FILE_NAME, "w") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=4)

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data):
        prev_block = self.get_last_block()
        new_block = Block(
            len(self.chain),
            str(datetime.datetime.now()),
            data,
            prev_block.hash
        )
        self.chain.append(new_block)
        self.save_chain()   # 🔥 SAVE TO FILE