import time


start_time = time.time()
time.sleep(5)
final_time = time.time()
# for char in zip(start_time, final_time):
#     if char == ":":
time_now = final_time - start_time
print(int(time_now))