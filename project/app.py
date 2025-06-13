"""
網站名: Flask 網頁框架 - HackMD
作者: ju peter
參考來源: http://hackmd.io/@peterju/HJftWmE5kg

功能：
- 使用者註冊與登入驗證（使用 SQLite 和 SQLAlchemy）。
- 登錄失物資訊，顯示與修改。
- 管理員審核使用者身分。
"""
import os
from flask import Flask, session, render_template
from flask import request, redirect, url_for, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

# 密碼生成函數(generate_password_hash)和密碼驗證函數(check_password_hash)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.json.ensure_ascii = False

# ----------------------------------------------
# session 程式
# 參考來源: https://hackmd.io/@peterju/S1FoLvgbkg
# 網站名: Flask-Session 套件 - HackMD
# 作者: ju peter
#
# SQLAlchemy 資料庫操作
# 參考來源: https://www.maxlist.xyz/2019/10/30/flask-sqlalchemy/
# 網站名: [Flask教學] Flask-SQLAlchemy 資料庫操作-ORM篇(二) - Max行銷誌
# 作者: Max
# ----------------------------------------------

# 設定 SQLAlchemy 連接到 SQLite 資料庫。
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化 SQLAlchemy。
db = SQLAlchemy(app)

# 設定 Flask-Session。
app.config['SESSION_TYPE'] = 'sqlalchemy'
# 設定使用 SQLAlchemy。
app.config['SESSION_SQLALCHEMY'] = db
app.config['SECRET_KEY'] = 'my_secret_key'

Session(app)


# 建立 session 資料表。
# 有兩張資料表，一張members (紀錄帳號基本資料)，一張lost_items（紀錄失物資料）。
class Member(db.Model):
    """會員資料表"""
    # 資料表members。
    __tablename__ = 'members'

    # 下方是資料表。
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    # 改成存加密密碼。
    password = db.Column(db.String, nullable=False)
    contact = db.Column(db.String)
    address = db.Column(db.String)
    lost_items = db.relationship('LostItem', backref='member', lazy=True)


class LostItem(db.Model):
    """失物資料表"""
    # 資料表lost_items。
    __tablename__ = 'lost_items'

    # 下方是資料表。
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'),
                          nullable=False)
    lost_county = db.Column(db.String, nullable=False)
    lost_district = db.Column(db.String, nullable=False)
    lost_location = db.Column(db.String, nullable=False)
    lost_date = db.Column(db.String, nullable=False)
    lost_category = db.Column(db.String, nullable=False)
    lost_image = db.Column(db.String)
    note = db.Column(db.Text)
    post_time = db.Column(db.DateTime, server_default=db.func.now())


class UnderReview(db.Model):
    """待審核帳號資料表"""
    # 資料表under_review。
    __tablename__ = 'under_review'

    # 下方是資料表。
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    # 改成存加密密碼。
    password = db.Column(db.String, nullable=False)
    contact = db.Column(db.String)
    address = db.Column(db.String)


# 管理員名稱及密碼。
class Administers(db.Model):
    """管理員帳號資料表"""

    # 資料表administers。
    __tablename__ = 'administers'

    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String, unique=True, nullable=False)

    # 改成存加密密碼。
    password = db.Column(db.String, nullable=False)


# 頁面路由與功能如下。
@app.route('/')
def index():
    """首頁畫面"""
    return render_template('index.html')


# 後端要寫的部分。
@app.route('/add', methods=['GET', 'POST'])
def add():
    """刊登失物畫面"""
    if 'user_id' not in session:
        # return redirect(url_for('login_register'))
        return render_template('error.html', message="請先登入或註冊")
    if request.method == 'POST':
        lost_county = request.form['lost_county']
        lost_district = request.form['lost_district']
        lost_location = request.form['lost_location']
        lost_date = request.form['lost_date']
        lost_category = request.form['lost_category']
        lost_image = request.files.get('lost_image')
        note = request.form['note']

        path = None
        if lost_image and lost_image.filename != '':
            latest_item = LostItem.query.order_by(LostItem.id.desc()).first()
            name_id = 1 if not latest_item else latest_item.id + 1
            path = f"{name_id}_{lost_image.filename}"
            complete_path = os.path.join('static', 'lost_images', path)
            try:
                lost_image.save(complete_path)
            except Exception:
                # print("圖片儲存失敗")
                return render_template('error.html', message="圖片儲存失敗")

        new = LostItem(member_id=session['user_id'],
                       lost_county=lost_county,
                       lost_district=lost_district,
                       lost_location=lost_location,
                       lost_date=lost_date,
                       lost_category=lost_category,
                       lost_image=path, note=note
                       )

        db.session.add(new)
        db.session.commit()
        return redirect(url_for('home'))
    member = Member.query.get(session['user_id'])
    return render_template('add.html', member=member)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """找尋失物畫面"""
    if request.method == 'POST':
        lost_county = request.form['lost_county']
        lost_district = request.form['lost_district']
        lost_location = request.form['lost_location']
        lost_date = request.form['lost_date']
        lost_category = request.form['lost_category']

        query = LostItem.query

        if lost_county:
            query = query.filter_by(lost_county=lost_county)
        if lost_district:
            query = query.filter_by(lost_district=lost_district)
        if lost_location:
            query = query.filter(LostItem.lost_location.contains(lost_location)
                                 )
        if lost_date:
            query = query.filter_by(lost_date=lost_date)
        if lost_category:
            query = query.filter(LostItem.lost_category.contains(lost_category)
                                 )

        items = query.order_by(LostItem.post_time.desc()).all()
    else:
        # 預設顯示所有失物。
        items = LostItem.query.order_by(LostItem.post_time.desc()).all()

    # 為每筆 item 加上 image_exists 屬性。
    for item in items:
        # 確保不是 None 或空字串。
        if item.lost_image:
            image_path = os.path.join(app.static_folder, 'lost_images',
                                      item.lost_image)
            item.image_exists = os.path.isfile(image_path)
        else:
            item.image_exists = False

    return render_template('search.html', items=items)


@app.route('/update', methods=['GET', 'POST'])
def update():
    """編輯畫面"""
    if 'user_id' not in session:
        # return redirect(url_for('login_register'))
        return render_template('error.html', message="請先登入或註冊")

    item_id = request.args.get('item_id', type=int)
    # 要編輯的那一筆失物。
    item = LostItem.query.get_or_404(item_id)
    member = Member.query.get(session['user_id'])

    if request.method == 'POST':
        item.lost_county = request.form['lost_county']
        item.lost_district = request.form['lost_district']
        item.lost_location = request.form['lost_location']
        item.lost_date = request.form['lost_date']
        item.lost_category = request.form['lost_category']
        item.note = request.form['note']
        lost_image = request.files.get('lost_image')

        path = None
        if lost_image and lost_image.filename != '':
            if item.lost_image:
                old_path = os.path.join('static', 'lost_images',
                                        item.lost_image)
                if os.path.exists(old_path):
                    os.remove(old_path)

            latest_item = LostItem.query.order_by(LostItem.id.desc()).first()
            name_id = 1 if not latest_item else latest_item.id + 1
            name = f"{name_id}_{lost_image.filename}"
            path = os.path.join('static', 'lost_images', name)
            try:
                lost_image.save(path)
                item.lost_image = name
            except Exception:
                # print("圖片儲存失敗")
                return render_template('error.html', message="圖片儲存失敗")

        db.session.commit()
        return redirect(url_for('home'))
    return render_template('update.html', item=item, member=member)


@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    """刪除失物"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    item = LostItem.query.get_or_404(item_id)
    print("item.member_id:", item.member_id)
    print("session user_id:", session.get('user_id'))

    if item.member_id != session['user_id']:
        return redirect(url_for('home'))

    # 刪除圖片（如果有）。
    if item.lost_image:
        image_path = os.path.join('static', 'lost_images', item.lost_image)
        if os.path.exists(image_path):
            os.remove(image_path)

    # 刪除資料。
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for('home'))


# 關於我們。
@app.route('/about')
def about():
    return render_template('about.html')


# 登入。
@app.route('/login', methods=['POST'])
def login():
    """帳號（已通過審核的）登入"""
    email = request.form['email']
    password = request.form['password']
    user = Member.query.filter_by(email=email).first()

    print("user:", user)
    if user:
        print(f"user.password: '{user.password}'")
        print(f"input password: '{password}'")

    # 用 check_password_hash 來驗證密碼。
    if user and check_password_hash(user.password, password):

        # 登入時將帳號資訊存入session。
        session['user_id'] = user.id
        session['username'] = user.username
        session['email'] = user.email

        return redirect(url_for('home'))
    else:
        message = request.args.get("message", "帳號或密碼錯誤")
        return render_template('error.html', message=message)


# 註冊。
@app.route('/register', methods=['GET', 'POST'])
def register():
    """帳號註冊：輸入資料後送入 UnderReview 等待審核"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        contact = request.form['contact']
        address = request.form['address']

        # 只要有一筆資料(email)相同，就回傳訊息。
        if Member.query.filter_by(email=email).first():
            message = request.args.get("message", "電子郵件已被註冊")
            return render_template('error.html', message=message)

        # 使用 generate_password_hash 加密密碼再存入資料庫。
        hashed_pw = generate_password_hash(password)

        # 將會員的資料增加進去資料庫的members資料表。
        new_user = UnderReview(email=email, password=hashed_pw,
                               username=username, contact=contact,
                               address=address)
        db.session.add(new_user)
        db.session.commit()

        # 或回首頁/登入畫面。
        return redirect(url_for('index'))

    # 這邊是處理 GET 請求的回應，不能省略。
    return redirect(url_for('index'))


# 帳號首頁（類似之前的welcome）。
@app.route('/home')
def home():
    """帳號首頁"""
    if 'user_id' not in session:
        return redirect(url_for('index'))

    # 查詢目前這個帳號所發布的遺失物。
    user_items = LostItem.query.filter_by(member_id=session['user_id']
                                          ).order_by(LostItem.post_time.desc()
                                                     ).all()

    # 檢查每筆資料的圖片是否真的存在。
    for item in user_items:
        image_path = os.path.join('static', 'lost_images',
                                  item.lost_image or '')
        item.image_exists = os.path.isfile(image_path)

    return render_template('home.html', user_items=user_items)


# 進入管理員頁面。
@app.route('/admin')
def admin():
    """審核（管理員）首頁"""
    # 找出所有尚未通過審核的帳號。
    user_review = UnderReview.query.all()
    return render_template('admin.html', user_review=user_review)


# 帳號審核通過。
# 將審核中帳號新增至members資料表，並刪除under_review資料表的帳號。
@app.route('/passed', methods=['POST'])
def passed():
    """帳號通過"""
    data = request.get_json()
    ids = data.get('ids', [])

    print("收到的資料:", data)
    print("ID 清單:", ids)

    for iid in ids:
        user_review = UnderReview.query.get(iid)
        if not user_review:
            # 找不到這筆就跳過。
            continue

        # 建立新會員 (移動資料)。
        new_member = Member(
            username=user_review.username,
            email=user_review.email,
            # 密碼已加密，可直接移。
            password=user_review.password,
            contact=user_review.contact,
            address=user_review.address
        )

        db.session.add(new_member)
        # 刪除審核表中的該筆。
        db.session.delete(user_review)

    db.session.commit()

    return jsonify({'success': True, 'message': '帳號已通過審核並移動至會員資料表'})


# 帳號審核不通過。
# 直接刪除under_review資料表的帳號。
@app.route('/failed', methods=['POST'])
def failed():
    """帳號不通過"""
    data = request.get_json()
    ids = data.get('ids', [])

    if not ids:
        return jsonify({'success': False, 'message': '未提供要審核的帳號ID'})

    for iid in ids:
        user_review = UnderReview.query.get(iid)
        if not user_review:
            # 找不到這筆就跳過。
            continue
        # 刪除審核表中的該筆。
        db.session.delete(user_review)

    db.session.commit()

    return jsonify({'success': True, 'message': '帳號沒通過審核'})


# 管理員登入。
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """管理員登入"""
    if request.method == 'POST':
        admin_name = request.form['admin_name']
        password = request.form['password']

        admin = Administers.query.filter_by(admin_name=admin_name).first()

        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['admin_name'] = admin.admin_name
            # 成功後導向管理頁。
            return redirect(url_for('admin'))
        else:
            message = request.args.get("message", "帳號或密碼錯誤")
            return render_template('error.html', message=message)

    return render_template('admin_login.html', login_error=False)


# 帳號登出。
@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/clear-session')
def clear_session():
    """清除session"""
    session.clear()
    return 'Session 已清除，請重新整理試試'


# 初始化資料庫。
with app.app_context():
    """首次執行前建立所有資料表並新增預設管理員帳號"""
    db.create_all()

    # 下面是預設的資料。
    if not Member.query.filter_by(email='counsel@ncut.edu.tw').first():
        default_user = Member(
            username='勤益科技大學生輔組',
            email='counsel@ncut.edu.tw',
            password=generate_password_hash('test1234'),
            contact='04-23924505#1234',
            address='台中市太平區中山路二段57號青永館六樓'
        )
        db.session.add(default_user)
        # 先提交，才能取得 default_user.id。
        db.session.commit()

        # 新增多筆失物資料。
        lost_items = [
            LostItem(
                member_id=default_user.id,
                lost_county='台中市',
                lost_district='太平區',
                lost_location='勤益科大工程館四樓桌子上',
                lost_date='2025-06-01',
                lost_category='學生證',
                lost_image='lost_image1.jpg',
                note='撿到一張學生證，姓名為王小明，已送交生輔組保管'
            ),
            LostItem(
                member_id=default_user.id,
                lost_county='台中市',
                lost_district='太平區',
                lost_location='勤益圖書館一樓自習室',
                lost_date='2025-06-03',
                lost_category='水壺',
                lost_image='lost_image2.jpg',
                note='遺失一個藍色水壺，上面貼有貼紙'
            ),
            LostItem(
                member_id=default_user.id,
                lost_county='台中市',
                lost_district='太平區',
                lost_location='校園餐廳附近',
                lost_date='2025-06-05',
                lost_category='雨傘',
                lost_image='lost_image3.jpg',
                note='黑色自動傘，忘在餐廳外的傘桶'
            ),

            LostItem(
                member_id=default_user.id,
                lost_county='台中市',
                lost_district='東區',
                lost_location='車站附近',
                lost_date='2025-05-05',
                lost_category='學生證',
                lost_image='lost_image4.jpg',
                note='放在車站沒拿'
            ),

            LostItem(
                member_id=default_user.id,
                lost_county='台中市',
                lost_district='太平區',
                lost_location='校內711',
                lost_date='2025-05-23',
                lost_category='背包',
                lost_image='lost_image6.jpg',
                note='藍色的'
            )
        ]

        db.session.add_all(lost_items)
        db.session.commit()

        # 預設管理員。
        administer = Administers(
            admin_name='hq8135',
            password=generate_password_hash('3b217029'),
        )

        db.session.add(administer)
        db.session.commit()
