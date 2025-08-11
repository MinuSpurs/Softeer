from multiprocessing import Queue

class multi_Queue:
    """
    Queue 클래스 정의

    put: 큐에 아이템을 추가
    get: 큐에서 아이템을 꺼냄
    empty: 큐가 비어있는지 확인
    """
    def __init__(self, maxsize=0):
        self.queue = Queue(maxsize)

    def put(self, item):
        self.queue.put(item)

    def get(self):
        return self.queue.get()
    
    def empty(self):
        return self.queue.empty()
    
if __name__ == "__main__":
    color_queue = multi_Queue(maxsize=4)  # maxsize를 4로 설정
    color_list = ['red', 'green', 'blue', 'black']

    print('pushing items to queue:')
    num = 1

    for color in color_list:        # 큐에 아이템 추가
        color_queue.put(color)
        print(f'item no: {num} {color}')
        num += 1
        
    print('popping items from queue:')
    num = 0

    while not color_queue.empty():  # 큐가 빌때까지 아이템 가져오기
        item = color_queue.get()
        print(f'item no: {num} {item}')
        num += 1