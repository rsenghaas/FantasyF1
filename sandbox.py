import numpy as np


race_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

def comp_pts(a,b):
    if a == 0: 
        return 0
    pts = 2
    if a <= 10 and a > 0:
        pts += race_points[int(a - 1)]
    if a < 0:
        pts = -10
    elif a > b:
        pts += min(10, 2*(a - b))
    else:
        pts += max(-10, 2*(a - b))
    if b < 15 and b > 0:
        pts += 1
    if b < 10 and b > 0:
        pts += 1
    return pts
    


fantasy_url = 'https://fantasy.formula1.com/'

stats_qualifying_url = 'https://www.statsf1.com/en/2021/abou-dhabi/qualification.aspx'
# stats_race_url = 'https://www.statsf1.com/en/2022/bahrein/qualification.aspx'

path = r'' # insert driver path here!

with open('drivers.txt', 'r', encoding= 'unicode_escape') as f:
    dr_list = f.read().splitlines()
f.close()


with open('teams.txt', 'r', encoding= 'unicode_escape') as f:
    tm_list  = f.read().splitlines()
f.close()

for i in range(len(dr_list)):
    dr_list[i] = dr_list[i].upper()


usage = np.zeros(len(dr_list))
tm_usage = np.zeros(len(tm_list))
q_factor = 0.95

for p in range(1):
    q = 1
    
    positions = np.zeros((len(dr_list), 2))
    race_stats = np.zeros((len(dr_list), 23))
    races = np.zeros((len(dr_list), 23))

    practice = [[2, 6, 5, 7, 3, 1, 8, 4, 10, 9, 13, 14, 12, 11, 16, 20, 0, 15, 17, 18],
                [4, 9, 8, 11, 1, 3, 5, 2, 6, 13, 15, 19, 14, 7, 20, 18, 10, 12, 16, 17]]


    for i in range(len(practice)):   
        data = practice[i]
        for j in range(len(data)):
            if data[j] == 0:
                continue
            races[j, i] = 1
            race_stats[j, i] = 0
            if data[j] == 1:
                race_stats[j, i] += 5
            if data[j] > 0 and data[j] <= 10:
                race_stats[j, i] += 10 - data[j] + 1
            if data[j] == 1:
                race_stats[j, i] += 5
            race_stats[j, i] += comp_pts(data[j], data[j])

        k = 0
        while k < len(dr_list):
            if data[k] < data[k + 1]:
                if data[k] > 0:
                    race_stats[k,i] += 5
                else: 
                    race_stats[k + 1, i] += 5
            elif data[k + 1] > 0:
                race_stats[k + 1, i] += 5
            k += 2

    factor =  (races * np.array([q**(22 - i) for i in range(23)]))
    dr_points = np.sum(race_stats * factor, axis = 1)  / np.sum(factor, axis = 1)
    team_points = np.zeros(int(len(dr_list) / 2))
    k = 0
    while k < len(dr_list) / 2:
        team_points[k] = dr_points[2*k] + dr_points[2*k + 1] - 3
        k += 1

    dr_prices = [30.5, 17.5, 24.0, 31.0, 18.0, 17.0, 14.5, 16.0, 12.5, 12.0, 13.5, 8.5, 9.5, 11.5, 7.5, 7.0, 9.0, 8.0, 5.5, 6.5]
    team_prices = [32.5, 34.5, 25.0, 18.5, 14.0, 10.5, 11.5, 7.0, 8.0, 6.0]
    cap = 100


    sug_num = 50
    value = 0
    pts = 0
    best_set = np.zeros((sug_num, 6))
    best_points = np.zeros(sug_num)
    best_prices = np.zeros(sug_num)

    dr_omitted = set([])
    tm_omitted = set([])
    dr_forced = set([])
    tm_forced = set([])
    if len(tm_forced) > 1:
        tm_forced == set([])
        print("To many teams forced")

    for t in range(len(team_prices)): 
        value +=  team_prices[t]
        pts += team_points[t]
        for d1 in range(len(dr_points)):
            value += dr_prices[d1]
            pts += dr_points[d1]
            for d2 in range(d1 + 1, len(dr_points)):
                value += dr_prices[d2]
                pts += dr_points[d2]
                if value > cap:
                    value -= dr_prices[d2]
                    pts -= dr_points[d2]
                    continue
                for d3 in range(d2 + 1, len(dr_points)):
                    value += dr_prices[d3]
                    pts += dr_points[d3]
                    if value > cap:
                        value -= dr_prices[d3]
                        pts -= dr_points[d3]
                        continue
                    for d4 in range(d3 + 1, len(dr_points)):
                        value += dr_prices[d4]
                        pts += dr_points[d4]
                        if value > cap:
                            value -= dr_prices[d4]
                            pts -= dr_points[d4]
                            continue
                        for d5 in range(d4 + 1, len(dr_points)):
                            value += dr_prices[d5]
                            pts += dr_points[d5]
                            if value > cap:
                                value -= dr_prices[d5]
                                pts -= dr_points[d5]
                                continue
                            if pts >= best_points[-1] and tm_omitted.intersection(set([t])) == set() and dr_omitted.intersection(set([d1, d2, d3,d4,d5])) == set() and set(tm_forced).intersection(set([t])) == tm_forced and dr_forced.intersection(set([d1, d2, d3,d4,d5])) == dr_forced:
                                best_points[-1] = pts
                                best_prices[-1] = value
                                best_set[-1] = np.array([t, d1, d2, d3, d4, d5])
                                index = np.argsort(best_points)[::-1]
                                best_points = best_points[index]
                                best_set = best_set[index]
                                best_prices = best_prices[index]
                            value -= dr_prices[d5]
                            pts -= dr_points[d5]
                        value -= dr_prices[d4]
                        pts -= dr_points[d4]
                    value -= dr_prices[d3]
                    pts -= dr_points[d3]
                value -= dr_prices[d2]
                pts -= dr_points[d2]
            value -= dr_prices[d1]
            pts -= dr_points[d1]
        value -=  team_prices[t]
        pts -= team_points[t]
    
    if True:
        print("q = {:.2f}".format(q))
        for i in range(5):
            print("Team {}".format(i + 1))
            print(tm_list[int(best_set[i, 0])])
            for j in range(1, 6):
                print(dr_list[int(best_set[i, j])], dr_points[int(best_set[i, j])])
            print(best_points[i])
            print(best_prices[i])
            print("")

    for i in range(sug_num):
        for j in range(1,6):
            usage[int(best_set[i,j])] += q_factor**i
    for i in range(sug_num):
        tm_usage[int(best_set[i,0])] += q_factor**i

print(usage)
print(tm_usage)
#index = np.argsort(usage)[::-1]
for j in range(len(dr_list)):
    print(j + 1, dr_list[j], dr_points[j])

#tm_index = np.argsort(tm_usage)[::-1]
for j in range(len(tm_list)):
    print(j + 1, tm_list[j], team_points[j])

team_points = tm_usage
dr_points = usage


sug_num = 5
value = 0
pts = 0
best_set = np.zeros((sug_num, 6))
best_points = np.zeros(sug_num)
best_prices = np.zeros(sug_num)

dr_omitted = set([])
tm_omitted = set([])
dr_forced = set([])
tm_forced = set([])
if len(tm_forced) > 1:
    tm_forced == set([])
    print("To many teams forced")

for t in range(len(team_prices)): 
    value +=  team_prices[t]
    pts += team_points[t]
    for d1 in range(len(dr_points)):
        value += dr_prices[d1]
        pts += dr_points[d1]
        for d2 in range(d1 + 1, len(dr_points)):
            value += dr_prices[d2]
            pts += dr_points[d2]
            if value > cap:
                value -= dr_prices[d2]
                pts -= dr_points[d2]
                continue
            for d3 in range(d2 + 1, len(dr_points)):
                value += dr_prices[d3]
                pts += dr_points[d3]
                if value > cap:
                    value -= dr_prices[d3]
                    pts -= dr_points[d3]
                    continue
                for d4 in range(d3 + 1, len(dr_points)):
                    value += dr_prices[d4]
                    pts += dr_points[d4]
                    if value > cap:
                        value -= dr_prices[d4]
                        pts -= dr_points[d4]
                        continue
                    for d5 in range(d4 + 1, len(dr_points)):
                        value += dr_prices[d5]
                        pts += dr_points[d5]
                        if value > cap:
                            value -= dr_prices[d5]
                            pts -= dr_points[d5]
                            continue
                        if pts >= best_points[-1] and tm_omitted.intersection(set([t])) == set() and dr_omitted.intersection(set([d1, d2, d3,d4,d5])) == set() and set(tm_forced).intersection(set([t])) == tm_forced and dr_forced.intersection(set([d1, d2, d3,d4,d5])) == dr_forced:
                            best_points[-1] = pts
                            best_prices[-1] = value
                            best_set[-1] = np.array([t, d1, d2, d3, d4, d5])
                            index = np.argsort(best_points)[::-1]
                            best_points = best_points[index]
                            best_set = best_set[index]
                            best_prices = best_prices[index]
                        value -= dr_prices[d5]
                        pts -= dr_points[d5]
                    value -= dr_prices[d4]
                    pts -= dr_points[d4]
                value -= dr_prices[d3]
                pts -= dr_points[d3]
            value -= dr_prices[d2]
            pts -= dr_points[d2]
        value -= dr_prices[d1]
        pts -= dr_points[d1]
    value -=  team_prices[t]
    pts -= team_points[t]

for i in range(0):
        print("Team {}".format(i))
        print(tm_list[int(best_set[i, 0])])
        for j in range(1, 6):
            print(dr_list[int(best_set[i, j])], dr_points[int(best_set[i, j])])
        print(best_points[i])
        print(best_prices[i])
        print("")
