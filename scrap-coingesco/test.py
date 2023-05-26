import multiprocessing

def sum(x):
    x += 1
    yield 'err'

links = [0, 1, 2, 3]

with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
    for i in links:
        result_data = process.map(sum, links)
        print(result_data)
