from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import re


race_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
practice_driver_points = np.array([32.0, 12.5,20.5,  8.5, 40.5 ,40.5, 15.5, 32.0, 13.5, 8.0, 7.5, 2.5, 3.0, 13.5, 4.5, 4.5, 10.0, 5.0, 7.0, 2.0])
practice_team_points = np.array([41.5, 26.0, 78.0, 44.5, 18.5, 7.0, 13.5, 6.0, 12.0, 6.0])
print(len(practice_driver_points))
def comp_pts(a,b):
    pts = 0
    if b > 0:
        if b <= 10:
            pts += 14 - b
        elif b <= 15:
            pts += 2
        else:
            pts += 1
            
    else:
        pts -= 5
    if a == 0: 
        return pts
    if a <= 10 and a > 0:
        pts += race_points[int(a - 1)]
    if a < 0:
        pts += -10
    else:
        pts += 1
        if b > a:
            pts += min(10, 2*(b - a))
        else:
            pts += max(-10, 2*(b - a))
    return pts
    


fantasy_url = 'https://fantasy.formula1.com/'

stats_qualifying_url = 'https://www.statsf1.com/en/2022/bahrein/qualification.aspx'
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


race_stats = np.zeros((len(dr_list), 23))
quali_position = np.zeros((len(dr_list), 23))
race_position = np.zeros((len(dr_list), 23))
races = np.zeros((len(dr_list), 23))
race_streak = np.zeros((len(dr_list)))
quali_streak = np.zeros((len(dr_list)))


r = 0
driver = webdriver.Chrome(executable_path=path)
driver.get(stats_qualifying_url)
while True:
    positions = np.zeros((len(dr_list), 3))
    ql = driver.find_elements(By.XPATH, "//*[@class= 'datatable']/tbody/tr")
    if len(ql) == 0:
        break
    for i in range(len(ql)):
        line = re.split(r'\s+', ql[i].text)
        for j in range(len(dr_list)):
            if dr_list[j] == line[2]:
                races[j, r] += 1
                positions[j, 0] = i + 1
                quali_position[j, r] = i + 1

                

    # sl = driver.find_elements(By.XPATH, "//*[@class= 'GPgrid']/tbody/tr")
    # for i in range(len(sl)):
    #     line = sl[i].text
    #     pos_str = ""
    #     pos = 0
    #     for k in range(len(line)):
    #         if line[k] >= '0' and line[k] <= '9':
    #             pos_str += line[k]
    #         elif line[k] == '.' and pos_str != "":
    #             pos = int(pos_str)
    #             k += 4
    #             for j in range(len(dr_list)):
    #                 if line[k:k + len(dr_list[j])] == dr_list[j]:
    #                     positions[j, 0] = pos
    #                     k += len(dr_list[j])
    #                     break
                        
                
    #         else:
    #             pos_str = ""

    items = driver.find_elements(By.TAG_NAME, "a")
    for item in items:
        text = item.text
        if text == "Result":
            item.click()
            break     

    rl = driver.find_elements(By.XPATH, "//*[@class= 'datatable']/tbody/tr")
    rounds = 0
    for i in range(len(rl)):
        line = re.split(r'\s+', rl[i].text)
        if i == 0:
            s = 6
            while s < 10:
                if len(line[s]) < 3:
                    rounds = int(line[s])
                    break
                else:
                    s += 1
        if len(line) < 3:
            break
        for j in range(len(dr_list)):
            if dr_list[j] == line[3]:
                if rl[i].text[0] >= '0' and rl[i].text[0] <= '9':
                    positions[j, 1] = i + 1
                else:
                    positions[j, 1] = -1 
                rounds2 = 0
                e = 6
                while not (line[e][0] >= '0' and line[e][0] <= '9'):
                    e += 1
                rounds2 = int(line[e])
                if  rounds2 == rounds:
                    positions[j, 2] = 1
            race_position[j, r] = positions[j, 1]

    items = driver.find_elements(By.TAG_NAME, "a")
    for item in items:
        text = item.text
        if text == "Best laps":
            item.click()
            break

    rl = driver.find_elements(By.XPATH, "//*[@class= 'datatable']/tbody/tr")
    if len(rl) == 0:
        print("Best lap tbd...")
    else:
        line = re.split(r'\s+', rl[0].text)
        for j in range(len(dr_list)):
            if dr_list[j] == line[2]:
                race_stats[j] += 5
    rounds = 0
    items = driver.find_elements(By.TAG_NAME, "a")
    for item in items:
        text = item.text
        if text == "Qualifications":
            item.click()
            break

    for i in range(len(dr_list)):
        race_stats[i,r] += comp_pts(positions[i, 1], positions[i, 0])

    items = driver.find_elements(By.TAG_NAME, "a")
    i = 0
    while i < len(dr_list):
        if positions[i, 1] < positions[i + 1, 1]:
            if positions[i, 1] > 0:
                race_stats[i,r] += 3
            else: 
                race_stats[i + 1,r] += 3
        elif positions[i + 1, 1] > 0:
            race_stats[i + 1, r] += 3

        if positions[i, 0] < positions[i + 1, 0]:
            if positions[i, 0] > 0:
                race_stats[i,r] += 2
            else: 
                race_stats[i + 1,r] += 2
        elif positions[i + 1, 0] > 0:
            race_stats[i + 1, r] += 2
        

        i += 2

    for item in items:
        text = item.text
        if text == ">>":
            item.click()
            break
    r += 1

driver.close()

print("Number of Races: {}".format(r))
r -= 1
for j in range(len(dr_list)):
    s = 0
    while s <= r:
        if quali_position[j, r - s] <= 10 and quali_position[j, r - s] >= 1:
            s += 1
        else:
            break
    quali_streak[j] = s
    s = 0
    while s <= r:
        if race_position[j, r - s] <= 10 and race_position[j, r - s] >= 1:
            s += 1
        else:
            break
    race_streak[j] = s



quali_top_ten_odds = np.zeros((len(dr_list)))
race_top_ten_odds = np.zeros((len(dr_list)))


q = 0.3
factor =  (races * np.array([q**(22 - i) for i in range(23)]))
for j in range(len(dr_list)):
    top_ten = np.zeros(23)
    for i in range(23):
        if quali_position[j, i] >= 1 and quali_position[j, i] <= 10:
            top_ten[i] = 1
    quali_top_ten_odds[j] = np.sum(top_ten * factor) / np.sum(factor)

    top_ten = np.zeros(23)
    for i in range(23):
        if race_position[j, i] >= 1 and race_position[j, i] <= 10:
            top_ten[i] = 1
    race_top_ten_odds[j] = np.sum(top_ten * factor) / np.sum(factor)


#####################
# * Practice q
####################
practice_q = 0.0

dr_points = np.sum(race_stats * factor, axis = 1)  / np.sum(factor, axis = 1)
dr_points = (1 - practice_q)*dr_points + practice_q*practice_driver_points


team_points = np.zeros(int(len(dr_list) / 2))
k = 0
while k < len(dr_list) / 2:
    team_points[k] = dr_points[2*k] + dr_points[2*k + 1] - 5
    k += 1

team_points = (1 - practice_q)*team_points + practice_q*practice_team_points

for j in range(len(dr_list)):
    if quali_streak[j] % 5 == 4:
        dr_points[j] += 5 * quali_top_ten_odds[j]
    if race_streak[j] % 5 == 4:
        dr_points[j] += 10 * race_top_ten_odds[j]

for j in range(len(tm_list)):
    if (quali_streak[2*j] % 3 == 2 or quali_streak[2*j + 1] % 3 == 2) and (quali_streak[2 * j] >= 2 and quali_streak[2*j + 1] >= 2):
        team_points[j] += 5 * quali_top_ten_odds[2*j] * quali_top_ten_odds[2*j + 1]
    if (race_streak[2*j] % 3 == 2 or race_streak[2*j + 1] % 3 == 2) and (race_streak[2 * j] >= 2 and race_streak[2*j + 1] >= 2):
        team_points[j] += 5 * race_top_ten_odds[2*j] * race_top_ten_odds[2*j + 1]





################################
# * Prices
################################
dr_prices = np.array([30.4, 17.9, 23.8, 30.6, 18.7, 17.2, 14.2, 15.9, 12.7, 12.3, 13.0, 8.4, 9.1, 11.8, 7.7, 6.9, 9.5, 8.1, 6.1, 6.3])
team_prices = np.array([32.7, 34.2, 25.8, 17.7, 14.1, 10.2, 11.8, 6.2, 8.8, 6.4])

cash = 0.5 + 0.01
current_team = [2, 0, 5, 7, 18, 16]

print("")
print("Current Team")
print(tm_list[current_team[0]])
for i in range(1, 6):
    print(dr_list[current_team[i]])

cap = team_prices[current_team[0]] + sum(dr_prices[current_team[1:]]) + cash

print("")
print("Cap: ", cap)
print("")
sug_num = 50
subs = 6
value = 0
pts = 0
best_set = np.zeros((sug_num, 6))
best_points = np.zeros(sug_num)
best_prices = np.zeros(sug_num)

dr_omitted = set([14])
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
                        index2 = np.argsort([dr_points[d1], dr_points[d2], dr_points[d3], dr_points[d4], dr_points[d5]])[::-1]
                        d = np.array([d1,d2,d3,d4,d5])[index2]
                        for i in d:
                            if dr_prices[i] <= 20:
                                pts += dr_points[i]
                                break
                        penalty = 0
                        if 6 - len(set([current_team[0]]).intersection([t])) - len(set(current_team[1:]).intersection(set([d1,d2,d3,d4,d5])))  > subs - 3:
                            penalty = -10 * (6 - len(set([current_team[0]]).intersection([t])) - len(set(current_team[1:]).intersection(set([d1,d2,d3,d4,d5]))) - (subs - 3))
                        pts += penalty
                        if 6 - len(set([current_team[0]]).intersection([t])) - len(set(current_team[1:]).intersection(set([d1,d2,d3,d4,d5])))  <= subs and  pts >= best_points[-1] and tm_omitted.intersection(set([t])) == set() and dr_omitted.intersection(set([d1, d2, d3,d4,d5])) == set() and set(tm_forced).intersection(set([t])) == tm_forced and dr_forced.intersection(set([d1, d2, d3,d4,d5])) == dr_forced:   
                            best_points[-1] = pts
                            best_prices[-1] = value
                            best_set[-1] = np.array([t, d1, d2, d3, d4, d5])
                            index = np.argsort(best_points)[::-1]
                            best_points = best_points[index]
                            best_set = best_set[index]
                            best_prices = best_prices[index]
                        pts -= penalty
                        value -= dr_prices[d5]
                        pts -= dr_points[d5]
                        pts -= dr_points[i]
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

for i in range(10):
    print("Team {}".format(i + 1))
    print(tm_list[int(best_set[i, 0])], team_points[int(best_set[i, 0])])
    index2 = np.argsort(dr_points[best_set[i, 1:].astype(int)])[::-1]
    tb_driver_index = 0
    for tb_driver in index2:
        if dr_prices[int(best_set[i, tb_driver + 1])] <= 20:
            tb_driver_index = tb_driver + 1
            break
    for j in range(1, 6):
        if j == tb_driver_index:
            print(dr_list[int(best_set[i, j])], "(TD)", 2*dr_points[int(best_set[i, j])])
        else:
            print(dr_list[int(best_set[i, j])], dr_points[int(best_set[i, j])])
    print(best_points[i])
    print("{:.2f}m".format(best_prices[i]))
    print("Substitutions: {}".format(6 - len(set([current_team[0]]).intersection([best_set[i, 0]])) - len(set(current_team[1:]).intersection(set(best_set[i, 1:])))))
    print("")



if True:
    dr_ppm = dr_points / dr_prices
    team_ppm = team_points / team_prices
    dr_index = np.argsort(dr_ppm)[::-1]
    print("PPM:")
    for i in dr_index:
        print(dr_list[i], "{:.2f}".format(dr_ppm[i]))

    print("")
    team_index = np.argsort(team_ppm)[::-1]
    for i in team_index:
        print(tm_list[i], "{:.2f}".format(team_ppm[i]))

    total_dr_points = sum(dr_points) * 1.0
    total_team_points = sum(team_points) * 1.0 
    total_dr_costs = sum(dr_prices) * 1.0
    total_team_costs = sum(team_prices) * 1.0

    total_dr_ppm = total_dr_points / total_dr_costs
    total_team_ppm = total_team_points /total_team_costs

    print("")
    print("Total Dribver PPM: {:.2f}".format(total_dr_ppm))
    print("Total Team PPM: {:.2f}".format(total_team_ppm))
    print("")

    print("Projected prices:")
    projected_dr_prices = dr_points / total_dr_points * total_dr_costs
    dr_index = np.argsort(projected_dr_prices)[::-1]
    for i in dr_index:
        print(dr_list[i], "{:.2f}m".format(projected_dr_prices[i]), "{:.2f}".format(dr_points[i]))

    print("")
    projected_team_prices = team_points / total_team_points * total_team_costs
    team_index = np.argsort(projected_team_prices)[::-1]
    for i in team_index:
        print(tm_list[i], "{:.2f}m".format(projected_team_prices[i]), "{:.2f}".format(team_points[i]))

    print("")
    print("Cost ratio:")
    dr_bargain = projected_dr_prices / dr_prices
    for i in range(len(dr_list)):
        print(dr_list[i], "{:.2f}".format(dr_bargain[i]))

    print("")
    team_bargain = projected_team_prices / team_prices
    for i in range(len(tm_list)):
        print(tm_list[i], "{:.2f}".format(team_bargain[i]))

    dr_points = projected_dr_prices
    team_points = projected_team_prices

    sug_num = 50
    subs = 6
    value = 0
    pts = 0
    best_set = np.zeros((sug_num, 6))
    best_points = np.zeros(sug_num)
    best_prices = np.zeros(sug_num)

    dr_omitted = set([])
    tm_omitted = set([])
    dr_forced = set([])
    tm_forced = set([])

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
                            index2 = np.argsort([dr_points[d1], dr_points[d2], dr_points[d3], dr_points[d4], dr_points[d5]])[::-1]
                            d = np.array([d1,d2,d3,d4,d5])[index2]
                            for i in d:
                                if dr_prices[i] <= 20:
                                    # pts += dr_points[i]
                                    break
                            pts -= value
                            if 6 - len(set([current_team[0]]).intersection([t])) - len(set(current_team[1:]).intersection(set([d1,d2,d3,d4,d5])))  <= subs and  pts >= best_points[-1] and tm_omitted.intersection(set([t])) == set() and dr_omitted.intersection(set([d1, d2, d3,d4,d5])) == set() and set(tm_forced).intersection(set([t])) == tm_forced and dr_forced.intersection(set([d1, d2, d3,d4,d5])) == dr_forced:   
                                best_points[-1] = pts
                                best_prices[-1] = value
                                best_set[-1] = np.array([t, d1, d2, d3, d4, d5])
                                index = np.argsort(best_points)[::-1]
                                best_points = best_points[index]
                                best_set = best_set[index]
                                best_prices = best_prices[index]
                            pts += value
                            value -= dr_prices[d5]
                            pts -= dr_points[d5]
                            # pts -= dr_points[i]
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
    print("")
    for i in range(10):
        print("Team {}".format(i + 1))
        print(tm_list[int(best_set[i, 0])], "{:.2f}".format(team_points[int(best_set[i, 0])]))
       
        for j in range(1, 6):
            print(dr_list[int(best_set[i, j])], "{:.2f}".format(dr_points[int(best_set[i, j])]))

        print("")
        print("{:.2f}m + {:.2f}m".format(best_points[i], best_prices[i]))
        print("Substitutions: {}".format(6 - len(set([current_team[0]]).intersection([best_set[i, 0]])) - len(set(current_team[1:]).intersection(set(best_set[i, 1:])))))
        print("")
