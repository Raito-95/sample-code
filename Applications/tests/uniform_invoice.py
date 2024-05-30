import math

# 各獎項中獎機率 (百分比形式)
probabilities = [
    0.000001,  # 1000萬
    0.000001,  # 200萬
    0.000003,  # 20萬
    0.00003,   # 4萬
    0.0003,    # 1萬
    0.003,     # 4000元
    0.03,      # 1000元
    0.3,       # 200元
    1.95,      # 500元
    0.1,       # 800元
    0.016,     # 2000元
    0.00003    # 100萬元
]

# 將百分比轉換為小數
probabilities = [p / 100 for p in probabilities]

# 計算單個號碼不中任何獎的機率
no_prize_probability = 1.0
for p in probabilities:
    no_prize_probability *= (1 - p)

# 計算單個號碼中至少一個獎的機率
at_least_one_prize_probability = 1 - no_prize_probability

# 計算不同中獎機率所需的發票數量
target_probabilities = [i / 100 for i in range(10, 100, 10)] + [0.99]
required_tickets = {}

for target_probability in target_probabilities:
    n = math.log(1 - target_probability) / math.log(1 - at_least_one_prize_probability)
    required_tickets[f"{int(target_probability * 100)}%"] = round(n)

# 輸出結果
print(f"單個號碼中至少一個獎的機率: {at_least_one_prize_probability * 100:.2f}%")
print("不同中獎機率所需購買的發票數量：")
for prob, tickets in required_tickets.items():
    print(f"{prob}: {tickets} 張")
