import hashlib
import time
import json
import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1

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
            print("Блок уже доданий до ланцюга.")
            return False
        self.chain.append(new_block)
        return True

    def get_latest_block(self):
        return self.chain[-1]

    def __str__(self):
        return "\n".join(str(block) for block in self.chain)

class Node:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain

    def mine_block(self, transactions: list, difficulty_target: int):
        prev_block = self.blockchain.get_latest_block()
        new_block = Block("1.0", prev_block.block_hash, transactions, difficulty_target)
        print(f"Майнинг нового блоку з хешем попереднього блоку: {prev_block.block_hash}")

        while int(new_block.block_hash, 16) >= difficulty_target:
            new_block.nonce += 1
            new_block.block_hash = new_block.calculate_hash()

        print(f"Блок знайдено! Nonce: {new_block.nonce}, Хеш блоку: {new_block.block_hash}")
        return new_block

    def receive_block(self, block: Block):
        if self.blockchain.add_block(block):
            print(f"Блок успішно доданий до локального блокчейну ноди.")
        else:
            print(f"Блок відхилено.")

# Імітація роботи мережі
def simulate_network():
    # ств. ключову пару
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()

    # ств. транзакції
    tx1 = Transaction("sender_address_1", ["receiver_address_1"], 100.0)
    tx1.sign_transaction(private_key)

    tx2 = Transaction("sender_address_2", ["receiver_address_2", "receiver_address_3"], 50.0)
    tx2.sign_transaction(private_key)

    # ств. блокчейн та кілька нод
    blockchain_1 = Blockchain()
    blockchain_2 = Blockchain()

    node_1 = Node(blockchain_1)
    node_2 = Node(blockchain_2)

    # майнимо новий блок на першій ноді
    difficulty_target = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    new_block = node_1.mine_block([tx1, tx2], difficulty_target)

    # передаємо блок на іншу ноду
    print("\nНода 1 передає блок Ноді 2 для верифікації та додавання:")
    node_2.receive_block(new_block)

    # виводимо інформацію про блокчейн кожної ноди
    print("\nБлокчейн ноди 1:")
    print(blockchain_1)

    print("\nБлокчейн ноди 2:")
    print(blockchain_2)

if __name__ == "__main__":
    simulate_network()