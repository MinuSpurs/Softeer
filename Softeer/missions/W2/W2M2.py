from multiprocessing import Process

def print_continent(continent='Asia'):  # Default continent는 Asia로 지정
    print(f'The name of continent is {continent}')

if __name__ == '__main__':
    p1 = Process(target=print_continent)    # Default continent 출력
    p2 = Process(target=print_continent, args=("America",))
    p3 = Process(target=print_continent, args=("Europe",))
    p4 = Process(target=print_continent, args=("Africa",))

    processes = [p1, p2, p3, p4]    # 프로세스 정의

    for process in processes:
        process.start() # 프로세스 시작 

    for process in processes:
        process.join()  # 프로세스 대기 후 종료