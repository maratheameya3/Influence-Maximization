import pandas as pd
from collections import defaultdict

# def find_next_employers(df):
#     users = defaultdict(list)
#     for i, row in df.iterrows():
#         users[row['user_id']].append((row['employer'], row['start_date']))
    
#     ans = 0
#     for user, temp in users.items():
#         employers = temp
#         employers.sort(key=lambda x:x[1])
#         employers = [i[0] for i in employers]
#         school = False
#         for i in (employers):
#             if i == 'School':
#                 school = True
#             if i == 'Blend360' and school:
#                 ans += 1
#     return ans


# data = {'user_id':  [1, 1, 2, 2, 3],
#         'employer': ['School', 'Blend360', 'Blend360', 'School', 'School'],
#         'position':['developer', 'developer', 'manager', 'manager', 'analyst'],
#         'start_date':['2020-04-13', '2021-11-01', '2021-01-01', '2021-01-11', '2019-03-15'],
#         'end_date':['2021-11-01', '', '2021-01-11', '', '2020-07-24']
#     }

# df = pd.DataFrame(data)

# find_next_employers(df)

def find_latest(input):
    input = input.sort_values('customer_ID')
    customers = defaultdict(list)
    answer = defaultdict(list)
    for _, row in input.iterrows():
        customers[row['customer_ID']].append((row['date'], row['product']))
    for cust_id, info in customers.items():
        temp = info
        temp.sort(key=lambda x:x[0])
        temp = [i[1] for i in temp]
        answer['customer_ID'].append(cust_id)
        answer['most_recent_purchase_1'].append(temp[0] if len(temp) > 0 else "NA")
        answer['most_recent_purchase_2'].append(temp[1] if len(temp) > 1 else "NA")
        answer['most_recent_purchase_3'].append(temp[2] if len(temp) > 2 else "NA")
    return pd.DataFrame(answer)

data = {'customer_ID':  [3017, 3079, 3090, 3057, 3057],
        'date':['2021-11-03 01:23:27', '2021-10-02 11:36:07', '2021-06-10 20:37:45', '2021-04-27 02:26:02', '2021-08-09 16:19:49'],
        'product':['C', 'A', 'C', 'D', 'B']
        }

df = pd.DataFrame(data)

print(find_latest(df))