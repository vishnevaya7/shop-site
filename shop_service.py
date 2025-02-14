import datetime
import sqlite3

from user_service import UserService


def create_database():
    conn = sqlite3.connect('store.db', check_same_thread=False)
    conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            product_name NOT NULL,
            price  NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_image (
                id INTEGER PRIMARY KEY,
                product_id  INTEGER NOT NULL,
                url  VARCHAR NOT NULL,
                is_main BOOLEAN NOT NULL
            )
        ''')
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS product_group (
                    id INTEGER PRIMARY KEY,
                    group_name  VARCHAR NOT NULL,
                    parant_group_id INTEGER
                )
            ''')
    cursor.execute('''
                    ALTER TABLE products
                    ADD COLUMN group_id INTEGER;
                ''')

    conn.commit()
    conn.close()


class Store:
    def __init__(self, db_name='store.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        self.user_service = UserService()

    def cursor(self):
        return self.conn.cursor()

    def add_product(self, name, price, quantity):
        self.cursor.execute('insert into products (product_name, price, quantity) values (?, ?, ?)',
                            (name, price, quantity))
        self.conn.commit()

    def get_product(self, product_id):
        product = self.cursor().execute('''SELECT p.id, product_name, price, quantity,i.url, g.group_name, d.description
                                   FROM products p
                                   left join product_image i on p.id = i.product_id
                                   left join product_group g on  p.group_id=g.id
                                   left join product_description d on p.id = d.product_id
                                   where p.id = ?''', (product_id,)).fetchone()

        product['properties'] = self.cursor().execute('select property, value from product_property where product_id = ?',
                                                    (product_id,)).fetchall()
        return product

    def get_all_products(self, group_id=None):
        sql_query = '''
        SELECT products.id,products.product_name as name,products.price, product_group.group_name, product_image.url from products
        inner join product_group on  products.group_id=product_group.id
        left join product_image
        on products.id = product_image.product_id and is_main=true'''
        if group_id:
            sql_query += f' where products.group_id={group_id}'

        return self.cursor().execute(sql_query).fetchall()

    def update_product(self, product_id, name=None, price=None, quantity=None):
        if name:
            self.cursor().execute('update products SET product_name = ? where id = ?', (name, product_id)).fetchall()
        if price:
            self.cursor().execute('update products SET price = ? where id = ?', (price, product_id)).fetchall()
        if quantity:
            self.cursor().execute('update products SET quantity = ? where id = ?', (quantity, product_id)).fetchall()
        self.conn.commit()

    def delete_product(self, product_id):
        self.cursor().execute('delete from products where id = ?', (product_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_all_groups(self):
        return self.cursor().execute('select * from product_group')

    def get_products_in_basket(self, login):

        return self.cursor().execute('''select u.username, b.quantity, p.product_name, i.url, p.price,p.id
from user u
         inner join basket b on u.id = b.user_id
         left join products p on b.product_id = p.id
         left join product_image i on p.id = i.product_id
where u.username = ?''', (login,)).fetchall()

    def add_into_basket(self, login, product_id, count=1):
        user_id = self.user_service.get_user(login).get('id')
        print(user_id)
        quantity = self.cursor().execute('select quantity from basket where product_id = ? and user_id = ?',
                                         (product_id, user_id)).fetchone()
        cursor = self.cursor()
        if quantity is None:

            cursor.execute(''' insert into basket(product_id,quantity,user_id,login) values (?,?,?,?)''',
                           (product_id, count, user_id, login))
        else:
            cursor.execute('update basket set quantity = ? where product_id = ? and user_id = ?',
                           (int(count) + int(quantity.get('quantity', 0)), product_id, user_id))
        return cursor.fetchall()

    def delete_product_from_basket(self, id, username):
        self.cursor().execute('delete from basket where product_id = ? and login = ?', (id, username))
        self.conn.commit()

    def get_order(self, username):
        order = self.cursor().execute('''
            SELECT u.username, b.quantity, p.product_name, i.url, p.price, p.id
            FROM user u
            INNER JOIN basket b ON u.id = b.user_id
            LEFT JOIN products p ON b.product_id = p.id
            LEFT JOIN product_image i ON p.id = i.product_id
            WHERE u.username = ?
        ''', (username,)).fetchall()
        self.conn.commit()

        filename = f'orders/{datetime.datetime.now().strftime("%H-%M-%S_%b.%d.%Y")}_{username}.csv'

        with open(filename, 'w+') as file:
            file.write('product_name;price;quantity;total price\n')
            for product in order:
                file.write(
                    f'{product["product_name"]};{product["price"]};{product["quantity"]};{product["price"] * product["quantity"]}\n')

        self.cursor().execute('DELETE FROM basket WHERE user_id = (SELECT id FROM user WHERE username = ?)',
                              (username,))
        self.conn.commit()

        return order


if __name__ == '__main__':
    create_database()
