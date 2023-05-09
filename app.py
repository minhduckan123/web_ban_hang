from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
from login_manager import login_required
import random
import os


# ------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Khởi tạo máy chủ
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sukabliatsukabliat'
app._static_folder = os.path.abspath("templates/static/")



# Kết nối đến cơ sở dữ liệu MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="minhduckan312",  # Thay thế bằng tên người dùng MySQL của bạn
  password="minhduckan312",  # Thay thế bằng mật khẩu MySQL của bạn
  database="bookstore"  # Thay thế bằng tên cơ sở dữ liệu bạn muốn sử dụng
)

mycursor = mydb.cursor()    
mycursor.execute('SELECT * FROM books')
books = mycursor.fetchall()
mycursor.execute("SELECT * FROM books ORDER BY added")
books_added = mycursor.fetchall()
mycursor.execute("SELECT * FROM books ORDER BY sold")
books_sold = mycursor.fetchall()
mycursor.execute("SELECT * FROM books JOIN book_categories ON books.book_id = book_categories.book_id JOIN category ON book_categories.category_id = category.category_id WHERE category.category_name = 'Business Economics'")
books_economic = mycursor.fetchall()
mycursor.execute('SELECT name FROM queries ORDER BY id DESC LIMIT 1')
present_query = mycursor.fetchone()
# ------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Trang chủ
@app.route('/')
@app.route('/home')
def home():
    # Lấy danh sách sách từ cơ sở dữ liệu
    bookname = 'All Books'
    user_data = login_required(mycursor)
    return render_template('index.html', bookname= bookname, books=books[:20], books_added=books_added[:20], books_sold=books_sold[:20], books_economic=books_economic[:20], user=user_data)

@app.route('/aboutus')
def about_us():
    return render_template('about_us.html')

@app.route('/developer')
def developer():
    return render_template('developer.html')
# ------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Đăng nhập, đăng ký và kiểm tra đăng nhập
@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    user_data = login_required(mycursor)
    if user_data:
        return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        budget = 0.0

        mycursor.execute("INSERT INTO users (name, email, password, budget) VALUES (%s, %s, %s, %s)", (name, username, password, budget))
        mydb.commit()

        session['user'] = (mycursor.lastrowid, name, username, password, budget)
        return redirect('/')
    else:
        return render_template('sign_up.html')
@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    user_data = login_required(mycursor)
    if user_data:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mycursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (username, password))
        user = mycursor.fetchone()

        if user:
            session['user'] = user
            return redirect('/')
        else:
            error = 'Invalid login credentials'
            return render_template('sign_in.html', error=error)
    else:
        return render_template('sign_in.html')

@app.route('/signout')
def signout():
    session.pop('user', None)
    return redirect('/')
# ------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Xem thông tin tài khoản
@app.route('/user')
def user():
    user_data = login_required(mycursor)
    if not user_data:
        return redirect('/signin')
    return render_template('user.html', user=user_data)

@app.route('/my_cart')
def my_cart():
    user_data = login_required(mycursor)
    if not user_data:
        return redirect('/signin')
    mycursor.execute("SELECT quantity FROM bookadd_user WHERE user_id = %s", (user_data[0],))
    quantity = mycursor.fetchall()
    mycursor.execute("SELECT * FROM books JOIN bookadd_user ON books.book_id = bookadd_user.book_id JOIN users ON bookadd_user.user_id = users.user_id WHERE users.user_id = %s", (user_data[0],))
    books_search = mycursor.fetchall()
    for i in range(len(books_search)):
        books_search[i] = books_search[i] + quantity[i]
    return render_template('my_cart.html', books=books_search, user= user_data)

@app.route('/cart_paid')
def cart_paid():
    user_data = login_required(mycursor)
    if not user_data:
        return redirect('/signin')
    mycursor.execute("SELECT quantity FROM booksold_user WHERE user_id = %s", (user_data[0],))
    quantity = mycursor.fetchall()
    mycursor.execute("SELECT * FROM books JOIN booksold_user ON books.book_id = booksold_user.book_id JOIN users ON booksold_user.user_id = users.user_id WHERE users.user_id = %s", (user_data[0],))
    books_search = mycursor.fetchall()
    for i in range(len(books_search)):
        books_search[i] = books_search[i] + quantity[i]
    return render_template('my_cart.html', books=books_search, user= user_data, none= 'none')

@app.route('/manage_wallet', methods=['GET', 'POST'])
def manage_wallet():
    user_data = login_required(mycursor)
    if not user_data:
        return redirect('/signin')
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        mycursor.execute("UPDATE users SET budget = budget + %s WHERE user_id = %s", (amount, user_data[0]))
        mydb.commit()
        return redirect('/user')
    else:
        return render_template('manage_wallet.html')

@app.route('/change_info', methods=['GET', 'POST'])
def change_info():
    user_data = login_required(mycursor)
    if not user_data:
        return redirect('/signin')
    if request.method == 'POST':
        mycursor.execute("SELECT password FROM users WHERE user_id = %s", (user_data[0],))
        pass_database = mycursor.fetchone()[0]
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        if old_password == pass_database:
            mycursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password, user_data[0]))
            mydb.commit()
            return redirect('/user')
        else:
            return render_template('change_info.html')
    else:
        # Trang hiển thị form đổi mật khẩu
        return render_template('change_info.html')
# ------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Quyền hạn của tài khoản thường
# Xem chi tiết sách

@app.route('/random')
def random_book():
    id_ = random.randint(1,48)
    return redirect(f'/detail/{id_}')

@app.route('/detail/<int:id>')
def book_detail(id):
    user_data = login_required(mycursor)
    if not user_data:
        return redirect('/signin')
    # Lấy thông tin sách từ cơ sở dữ liệu dựa trên id
    mycursor.execute("SELECT * FROM books WHERE book_id = %s", (id,))
    book = mycursor.fetchone()
    return render_template('detail.html', book=book, query=present_query[0], user= user_data)
@app.route('/subjects')
def subjects_book():
    user_data = login_required(mycursor)
    mycursor.execute("SELECT category_name FROM category")
    category = mycursor.fetchall()
    user_data = login_required(mycursor)
    return render_template('category.html', books_added=books_added[:20], books_sold=books_sold[:20], books_economic=books_economic[:20], categories=category, user=user_data)

@app.route('/<subject>')
def subject_book(subject):
    user_data = login_required(mycursor)
    bookname = subject
    mycursor.execute("SELECT * FROM books JOIN book_categories ON books.book_id = book_categories.book_id JOIN category ON book_categories.category_id = category.category_id WHERE category.category_name = %s", (subject,))
    subject_books = mycursor.fetchall()
    return render_template('index.html', bookname=bookname, books=subject_books, books_added=books_added[:20], books_sold=books_sold[:20], books_economic=books_economic[:20], user=user_data)
    

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user_data = login_required(mycursor)
    if user_data:
        user_id = user_data[0]  # get user ID from session
        book_id = request.form['book_id']
        quantity = request.form['quantity']
        # add book to user's cart in user_book table
        mycursor.execute('INSERT INTO bookadd_user (user_id, book_id, quantity) VALUES (%s, %s, %s)', (user_id, book_id, quantity))
        mycursor.execute("UPDATE books SET added = added + %s WHERE book_id = %s", (quantity, book_id))
        mydb.commit()
        return jsonify({'status': 'success'})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    user_data = login_required(mycursor)
    if user_data:
        user_id = user_data[0]  # get user ID from session
        book_id = request.form.get('book_id')
        quantity = request.form.get('quantity')
        # add book to user's cart in user_book table
        mycursor.execute('DELETE FROM bookadd_user WHERE user_id = %s AND book_id = %s AND quantity = %s LIMIT 1', (user_id, book_id, quantity))
        mycursor.execute("UPDATE books SET added = added - %s WHERE book_id = %s", (quantity, book_id))
        mydb.commit()
        return redirect('/my_cart')
    else:
        return redirect('/signin')

@app.route('/pay', methods=['POST'])
def pay():
    user_data = login_required(mycursor)
    if not user_data:
        return redirect('/signin')
    book_id = request.form.get('book_id')
    quantity = request.form.get('quantity')
    mycursor.execute("SELECT price FROM books WHERE book_id = %s", (book_id,))
    price = mycursor.fetchone()[0]
    total_payment = price * int(quantity)
    mycursor.execute("SELECT budget FROM users WHERE user_id = %s", (user_data[0],))
    budget = mycursor.fetchone()[0]
    if total_payment > budget:
        return jsonify({'status': 'Fail'})
    mycursor.execute("SELECT quantity FROM books WHERE book_id = %s", (book_id,))
    stock_quantity = mycursor.fetchone()[0]
    if int(quantity) > stock_quantity:
        return jsonify({'status': 'Fail'})
    mycursor.execute("UPDATE users SET budget = budget - %s WHERE user_id = %s", (total_payment, user_data[0]))
    mycursor.execute("UPDATE books SET quantity = quantity - %s WHERE book_id = %s", (int(quantity), book_id))
    mycursor.execute("UPDATE books SET added = added - %s WHERE book_id = %s", (quantity, book_id))
    mycursor.execute("UPDATE books SET sold = sold + %s WHERE book_id = %s", (quantity, book_id))
    mycursor.execute("DELETE FROM bookadd_user WHERE user_id = %s AND book_id = %s LIMIT 1", (user_data[0], book_id))
    mycursor.execute("INSERT INTO booksold_user (book_id, user_id, quantity) VALUES (%s, %s, %s)", (book_id, user_data[0], quantity))
    mydb.commit()
    return jsonify({'status': 'Success'})


@app.route('/pay_all', methods=['POST'])
def pay_all():
    user_data = login_required(mycursor)
    if not user_data:
        return redirect('/signin')
    mycursor.execute("SELECT * FROM bookadd_user WHERE user_id = %s", (user_data[0],))
    bookadds = mycursor.fetchall()
    total_payment = 0
    for bookadd in bookadds:
        mycursor.execute("SELECT price FROM books WHERE book_id = %s", (bookadd[0],))
        price = mycursor.fetchone()[0]
        quantity = bookadd[-1]
        total_payment += (price * quantity)
    mycursor.execute("SELECT budget FROM users WHERE user_id = %s", (user_data[0],))
    budget = mycursor.fetchone()[0]
    if total_payment > budget:
        return jsonify({'status': 'Fail'})
    quantity_dict = {}
    for book in bookadds:
        book_id = book[0]
        quantity = book[-1]
        mycursor.execute("SELECT quantity FROM books WHERE book_id = %s", (book_id,))
        stock_quantity = mycursor.fetchone()[0]
        try:
            quantity_dict[book[0]] += int(quantity)
        except:
            quantity_dict[book[0]] = int(quantity)
        if quantity_dict[book[0]] > stock_quantity:
            return jsonify({'status': 'Fail'})
    for book in bookadds:
        book_id = book[0]
        quantity = book[-1]
        mycursor.execute("UPDATE books SET quantity = quantity - %s WHERE book_id = %s", (quantity, book_id))
        mycursor.execute("INSERT INTO booksold_user (book_id, user_id, quantity) VALUES (%s, %s, %s)", (book_id, user_data[0], quantity))
        mycursor.execute("UPDATE books SET added = added - %s WHERE book_id = %s", (quantity, book_id))
        mycursor.execute("UPDATE books SET sold = sold + %s WHERE book_id = %s", (quantity, book_id))
    mycursor.execute("DELETE FROM bookadd_user WHERE user_id = %s", (user_data[0],))
    mycursor.execute("UPDATE users SET budget = budget - %s WHERE user_id = %s", (total_payment, user_data[0]))
    mydb.commit()
    return jsonify({'status': 'Success'})


# ------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Quyền hạn của tài khoản admin
# Thêm sách mới
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = float(request.form['price'])

        # Thêm sách vào cơ sở dữ liệu
        mycursor.execute("INSERT INTO books (title, author, price) VALUES (%s, %s, %s)", (title, author, price))
        mydb.commit()
        
        return redirect('/search/%s'% present_query)
    else:
        return render_template('add.html')


# Cập nhật sách
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = float(request.form['price'])

        # Cập nhật thông tin sách trong cơ sở dữ liệu
        mycursor.execute("UPDATE books SET title = %s, author = %s, price = %s WHERE book_id = %s", (title, author, price, id))
        mydb.commit()

        return redirect('/search/%s'% present_query)
    else:
        # Lấy thông tin sách từ cơ sở dữ liệu dựa trên id
        mycursor.execute("SELECT * FROM books WHERE book_id = %s", (id,))
        book = mycursor.fetchone()
        return render_template('update.html', book=book)
    
@app.route('/delete/<int:id>', methods=['POST'])
def delete_book(id):
    # Xóa sách khỏi cơ sở dữ liệu dựa trên id
    mycursor.execute("DELETE FROM books WHERE book_id = %s", (id,))
    mydb.commit()
    return redirect('/search/%s'% present_query)
# ------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Mục tìm kiếm
@app.route('/advanced_search', methods=['GET', 'POST'])
def advanced_search():
    if request.method == 'POST':
        user_data = login_required(mycursor)
        bookname = "Advanced Search"
        categories = request.form.getlist('categories')
        if categories != []:
            category_search = ', '.join(['%s'] * len(categories))
            mycursor.execute("SELECT category_id FROM category WHERE category_name IN ({})".format(category_search), tuple(categories))
            categories_id = mycursor.fetchall()
            categories_ids = []
            for i in categories_id:
                categories_ids.append(str(i[0]))
            categories_id = ",".join(categories_ids)
            sql = f'SELECT * FROM books WHERE book_id IN ( SELECT book_id FROM book_categories WHERE category_id IN ({categories_id}) GROUP BY book_id HAVING COUNT(DISTINCT category_id) = {len(categories_ids)})'
            mycursor.execute(sql)
            results = mycursor.fetchall()
        else:
            results = books
        mycursor.execute("SELECT * FROM books ORDER BY added")
        books_added = mycursor.fetchall()
        mycursor.execute("SELECT * FROM books ORDER BY sold")
        books_sold = mycursor.fetchall()
        mycursor.execute("SELECT * FROM books JOIN book_categories ON books.book_id = book_categories.book_id JOIN category ON book_categories.category_id = category.category_id WHERE category.category_name = 'Business Economics'")
        books_economic = mycursor.fetchall()
        return render_template('index.html', bookname=bookname, books=results, books_added=books_added[:20], books_sold=books_sold[:20], books_economic=books_economic[:20], user=user_data)
    else:
        return render_template('advanced_search.html')

@app.route('/search_live', methods=['POST'])
def search_live():
    query = request.form.get('query')
    # Tìm kiếm sách trong cơ sở dữ liệu dựa trên từ khóa
    mycursor.execute("SELECT * FROM books WHERE title LIKE %s", ('%' + query + '%',))
    books_search = mycursor.fetchall()
    return jsonify({ 'results': books_search })

@app.route('/search', methods=['POST'])
def search():
    global present_query
    query = request.form.get('keyword')
    mycursor.execute("INSERT INTO queries (name) VALUES (%s)", (query,))
    mydb.commit()
    mycursor.execute('SELECT name FROM queries ORDER BY id DESC LIMIT 1')
    present_query = mycursor.fetchone()
    # Tìm kiếm sách trong cơ sở dữ liệu dựa trên từ khóa
    mycursor.execute("SELECT * FROM books WHERE title LIKE %s", ('%' + query + '%',))
    books_search = mycursor.fetchall()
    return render_template('search.html', books=books_search)

@app.route('/search/<query>')
def search_(query):
    # Tìm kiếm sách trong cơ sở dữ liệu dựa trên từ khóa
    mycursor.execute("SELECT * FROM books WHERE title LIKE %s", ('%' + query + '%',))
    books_search = mycursor.fetchall()
    return render_template('search.html', books=books_search)
# ------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Khởi chạy
if __name__ == '__main__':
    app.run(debug=True)