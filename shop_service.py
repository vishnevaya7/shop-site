import sqlite3


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
    # image_url,
    # монитор
    # герцовка значение
    # диагональ значение
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
        self.cursor = self.conn.cursor()

    def add_product(self, name, price, quantity):
        self.cursor.execute('insert into products (product_name, price, quantity) values (?, ?, ?)',
                            (name, price, quantity))
        self.conn.commit()

    def get_product(self, product_id):
        self.cursor.execute('''SELECT p.id, product_name, price, quantity,i.url, g.group_name
                                   FROM products p
                                   left join product_image i on p.id = i.product_id
                                   left join product_group g on  p.group_id=g.id
                                   where product_id = ?''', (product_id,))
        return self.cursor.fetchone()

    def get_all_products(self):
        self.cursor.execute('''
        SELECT products.id,products.product_name as name,products.price, product_group.group_name, product_image.url from products
        left join product_group on  products.group_id=product_group.id
        left join product_image
        on products.id = product_image.product_id and is_main=true''')
        return self.cursor.fetchall()

    def update_product(self, product_id, name=None, price=None, quantity=None):
        if name:
            self.cursor.execute('update products SET product_name = ? where id = ?', (name, product_id))
        if price:
            self.cursor.execute('update products SET price = ? where id = ?', (price, product_id))
        if quantity:
            self.cursor.execute('update products SET quantity = ? where id = ?', (quantity, product_id))
        self.conn.commit()

    def delete_product(self, product_id):
        self.cursor.execute('delete from products where id = ?', (product_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    create_database()

    store = Store()
    # app.run()
    store.add_product('Apple', 0.5, 100)
    store.add_product('Banana', 0.3, 150)

    products = store.get_all_products()
    print(products)

    product = store.get_product(1)
    print(product)

    store.update_product(1, price=1, name='Pineapple', quantity=200)

    store.delete_product(2)

    store.close()
