from flask import Flask, request, jsonify

app = Flask(__name__)

# 假设用以下字典简单模拟数据库（开发时需替换为实际数据库操作）
members = {}            # phone -> {id, name, phone, level, register_date}
member_id_counter = 1

purchase_logs = []      # list of {member_id, amount, points_earned, store, purchase_time}

redeem_logs = []        # list of {member_id, points_used, item, redeem_time}

from datetime import datetime

# 注册会员并绑定手机号（手机号唯一）
@app.route('/register_member', methods=['POST'])
def register_member():
    global member_id_counter
    name = request.json['name']
    phone = request.json['phone']
    if phone in members:
        return jsonify({"msg": "该手机号已绑定会员，请勿重复注册"}), 400
    members[phone] = {
        "id": member_id_counter,
        "name": name,
        "phone": phone,
        "level": "普通会员",
        "register_date": datetime.now().date().isoformat()
    }
    member_id_counter += 1
    return jsonify({"msg": "注册并绑定手机号成功", "member": members[phone]})

# 用户消费后积分自动累计（1元=1积分），记录消费流水
@app.route('/add_purchase', methods=['POST'])
def add_purchase():
    phone = request.json['phone']
    amount = float(request.json['amount'])
    store = request.json.get('store', '')
    if phone not in members:
        return jsonify({"msg": "未找到对应会员手机号"}), 404
    points = int(amount)  # 积分规则：1元1分
    purchase_log = {
        "member_id": members[phone]["id"],
        "amount": amount,
        "points_earned": points,
        "store": store,
        "purchase_time": datetime.now().isoformat()
    }
    purchase_logs.append(purchase_log)
    return jsonify({"msg": f"消费记录添加，获得{points}积分", "purchase_log": purchase_log})

# 积分兑换
@app.route('/redeem', methods=['POST'])
def redeem():
    phone = request.json['phone']
    points_used = int(request.json['points_used'])
    item = request.json['item']
    if phone not in members:
        return jsonify({"msg": "未找到对应会员手机号"}), 404
    # 实际开发需校验剩余积分是否足够
    redeem_log = {
        "member_id": members[phone]["id"],
        "points_used": points_used,
        "item": item,
        "redeem_time": datetime.now().isoformat()
    }
    redeem_logs.append(redeem_log)
    return jsonify({"msg": "兑换成功", "redeem_log": redeem_log})

# 后台查询消费记录（可按手机号查，也可查全部）
@app.route('/admin/purchase_logs', methods=['GET'])
def admin_purchase_logs():
    phone = request.args.get('phone')
    if phone:
        if phone not in members:
            return jsonify({"msg": "未找到对应会员手机号"}), 404
        member_id = members[phone]["id"]
        filtered_logs = [log for log in purchase_logs if log["member_id"] == member_id]
    else:
        filtered_logs = purchase_logs
    return jsonify({"records": filtered_logs})

if __name__ == '__main__':
    app.run(debug=True)
