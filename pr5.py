import time
import matplotlib.pyplot as plt
import threading

class Node:
    def __init__(self, id, n):
        self.id = id
        self.n = n
        self.blockchain = []
        self.received_valid_messages = {}

    def validate_block(self, block):
        return True

    def send_valid_message(self, block, node):
        time.sleep(0.01)
        node.receive_valid_message(self.id, "Valid")

    def receive_valid_message(self, sender_id, message):
        self.received_valid_messages[sender_id] = message

    def add_block_to_blockchain(self, block):
        self.blockchain.append(block)
        print(f"Node {self.id} added block {block['id']} to blockchain.")

    def receive_block(self, block, nodes):
        if self.validate_block(block):
            threads = []
            for node in nodes:
                if node.id != self.id:
                    thread = threading.Thread(target=self.send_valid_message, args=(block, node))
                    threads.append(thread)
                    thread.start()

            for thread in threads:
                thread.join()

    def process_block(self, block):
        valid_votes = list(self.received_valid_messages.values()).count("Valid")
        if valid_votes >= 2 * self.n // 3:
            self.add_block_to_blockchain(block)
            return True
        return False

# спрощений BFT протокол
def bft_protocol(n):
    nodes = [Node(i, n) for i in range(n)]
    leader = nodes[0]

    # лідер створює блок і розсилає його іншим вузлам
    block = {"id": 1, "transactions": ["tx1", "tx2", "tx3"]}
    print(f"Leader Node {leader.id} created block {block['id']}.")

    start_time = time.time()

    for node in nodes[1:]:
        node.receive_block(block, nodes)

    consensus_reached = all(node.process_block(block) for node in nodes)

    end_time = time.time()
    return end_time - start_time

participants = [10, 20, 45, 100, 1000 ]
times = []

for n in participants:
    execution_time = bft_protocol(n)
    times.append(execution_time)
    print(f'Кількість учасників: {n}, Час виконання: {execution_time:.4f} секунд')

# Побудова графіку
plt.plot(participants, times, marker='o')
plt.xlabel('Кількість учасників')
plt.ylabel('Час виконання (секунди)')
plt.title('Залежність часу виконання протоколу BFT від кількості учасників')
plt.grid(True)
plt.show()
