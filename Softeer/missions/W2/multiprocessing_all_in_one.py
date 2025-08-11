from multiprocessing import Queue, Process, current_process
import time

def work_task(tasks_to_accomplish, tasks_that_are_done):
    while not tasks_to_accomplish.empty():
        try:
            task = tasks_to_accomplish.get_nowait() # 큐에서 바로 꺼내기
        except:
            break  # 큐가 비었을 경우 바로 예외처리
        print(f'Task no {task}')
        time.sleep(0.5) # 작업 처리 시간 0.5초 설정
        proc_name = current_process().name  # 현재 프로세스 이름 가져오기
        tasks_that_are_done.put(f'Task no {task} is done by {proc_name}')

if __name__ == "__main__":
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    tasks = [f'{i}' for i in range(10)]    # task 리스트

    # task를 큐에 추가
    for task in tasks:
        tasks_to_accomplish.put(task)

    processes = []
    num_processes = 4

    # 프로세스 생성 및 시작
    for i in range(num_processes):
        p = Process(target=work_task, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # 모든 프로세스가 완료될 때까지 대기
    for p in processes:
        p.join()

    # 완료된 작업 출력
    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())