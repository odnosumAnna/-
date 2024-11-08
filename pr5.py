import hashlib
import time
import json
import random
import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from threading import Thread
import matplotlib.pyplot as plt

class Transaction:
    def __init__(self, sender: str, receivers: list, amount: float):
        self.input = sender
        self.output = receivers
        self.amount = amount
        self.txTimestamp = time.time()
        self.txHash = self.calculate_hash()
        self.signature = None

    def calculate_hash(self):
        tx_string = f"{self.input}{'|'.join(self.output)}{self.amount}{self.txTimestamp}"
        return hashlib.sha256(tx_string.encode()).hexdigest()

    def sign_transaction(self, private_key: SigningKey):
        if self.signature is not None:
            raise Exception("Transaction has already been signed.")
        self.signature = private_key.sign(self.txHash.encode())

    def verify_signature(self, public_key: VerifyingKey):
        return self.signature and public_key.verify(self.signature, self.txHash.encode())

    def verify_hash(self):
        return self.txHash == self.calculate_hash()

    def to_dict(self):
        return {
            "input": self.input,
            "output": self.output,
            "amount": self.amount,
            "txTimestamp": self.txTimestamp,
            "txHash": self.txHash,
            "signature": base64.b64encode(self.signature).decode() if self.signature else None
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

class Block:
    def __init__(self, version: str, prev_hash: str, transactions: list, difficulty_target: int, nonce: int = 0):
        self.version = version
        self.prevHash = prev_hash
        self.timestamp = time.time()
        self.difficulty_target = difficulty_target
        self.nonce = nonce
        self.transactions = transactions
        self.MerkleRoot = self.calculate_merkle_root()
        self.block_hash = self.calculate_hash()
        self.signature = None

    def calculate_merkle_root(self):
        transaction_hashes = [tx.txHash for tx in self.transactions]
        if not transaction_hashes:
            return ""
        while len(transaction_hashes) > 1:
            temp_hashes = []
            for i in range(0, len(transaction_hashes), 2):
                if i + 1 < len(transaction_hashes):
                    combined_hash = transaction_hashes[i] + transaction_hashes[i + 1]
                else:
                    combined_hash = transaction_hashes[i]
                temp_hashes.append(hashlib.sha256(combined_hash.encode()).hexdigest())
            transaction_hashes = temp_hashes
        return transaction_hashes[0]

    def calculate_hash(self):
        block_string = f"{self.version}{self.prevHash}{self.timestamp}{self.difficulty_target}{self.nonce}{self.MerkleRoot}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def sign_block(self, private_key: SigningKey):
        if self.signature is not None:
            raise Exception("Block has already been signed.")
        self.signature = private_key.sign(self.block_hash.encode())

    def verify_block(self, public_key: VerifyingKey):
        return self.signature and public_key.verify(self.signature, self.block_hash.encode())

    def verify_merkle_root(self):
        return self.MerkleRoot == self.calculate_merkle_root()

    def to_dict(self):
        return {
            "version": self.version,
            "prevHash": self.prevHash,
            "timestamp": self.timestamp,
            "difficulty_target": self.difficulty_target,
            "nonce": self.nonce,
            "MerkleRoot": self.MerkleRoot,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "block_hash": self.block_hash,
            "signature": base64.b64encode(self.signature).decode() if self.signature else None
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block("1.0", "0", [], 1)
        self.chain.append(genesis_block)

    def add_block(self, new_block: Block):
        if any(block.block_hash == new_block.block_hash for block in self.chain):
            return False
        self.chain.append(new_block)
        return True

    def get_latest_block(self):
        return self.chain[-1]

    def __str__(self):
        return "\n".join(str(block) for block in self.chain)


class Node:
    def __init__(self, blockchain: Blockchain, node_id: int):
        self.blockchain = blockchain
        self.node_id = node_id
        self.valid_votes = 0
        self.received_valid_msgs = 0

    def mine_block(self, transactions, difficulty_target):
        nonce = 0
        while True:
            new_block = Block("1.0", self.blockchain.chain[-1].block_hash, transactions, difficulty_target, nonce)
            if new_block.block_hash.startswith("0000"):  # Перевірка складності
                return new_block
            nonce += 1

    def receive_block(self, block: Block, nodes):
        if self.validate_block(block):
            for node in nodes:
                if node != self:
                    Thread(target=self.send_valid, args=(node,)).start()

    def send_valid(self, node):
        time.sleep(0.1)  # Затримка в 100 мс для симуляції передачі
        node.receive_valid()

    def receive_valid(self):
        self.received_valid_msgs += 1

    def validate_block(self, block: Block):
        return block.block_hash.startswith("0000") and block.verify_merkle_root()  # перевірка підпису та транзакцій

    def finalize_block(self, block: Block, total_nodes):
        if self.received_valid_msgs >= (2 * total_nodes) // 3:
            self.blockchain.add_block(block)
 #           print(f"Блок успішно додано до ланцюга в вузлі {self.node_id}")


def bft_protocol(num_nodes):
    blockchain = Blockchain()
    nodes = [Node(blockchain, i) for i in range(num_nodes)]
    transactions = [Transaction(f"sender_{i}", [f"receiver_{i}"], random.uniform(1, 100)) for i in range(5)]
    leader_node = nodes[0]

    # майнимо новий блок і виводимо інформацію про знайдений нонсе
    print(f"\nСимуляція для {num_nodes} вузлів:")
    new_block = leader_node.mine_block(transactions,
                                       difficulty_target=0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    print(f"Правильний нонсе знайдено: {new_block.nonce}")

    threads = []
    for node in nodes:
        thread = Thread(target=node.receive_block, args=(new_block, nodes))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for node in nodes:
        node.finalize_block(new_block, num_nodes)

    print("Блок успішно додано до ланцюга")


def measure_time_for_protocol(num_nodes):
    start_time = time.time()
    bft_protocol(num_nodes)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Час виконання для {num_nodes} вузлів: {duration:.2f} секунд")
    return duration


node_counts = [10, 100, 1000]
execution_times = []

for num_nodes in node_counts:
    execution_time = measure_time_for_protocol(num_nodes)
    execution_times.append(execution_time)


def plot_execution_time():
    plt.plot(node_counts, execution_times, marker='o')
    plt.title("Час виконання BFT протоколу залежно від кількості вузлів")
    plt.xlabel("Кількість вузлів")
    plt.ylabel("Час виконання (сек.)")
    plt.grid(True)
    plt.show()


plot_execution_time()
