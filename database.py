import sqlite3


class DataBase:
    def __init__(self, file='db.sqlite'):
        self.connection = sqlite3.connect(file)
        self.cursor = cur = self.connection.cursor()
                
        cur.execute('CREATE TABLE IF NOT EXISTS chats(id int UNIQUE, progress_message_id int)')
        cur.execute('CREATE TABLE IF NOT EXISTS offers(token_id int UNIQUE, contract_address text(42), price double, description text)')

        self.connection.commit()

    def offer_exists(self, token_id):
        return bool(self.get_offer(token_id))
    
    def get_offer(self, token_id):
        self.cursor.execute('SELECT * FROM chats WHERE id=%i' % token_id)
        return self.cursor.fetchall()
    
    def get_offers(self, max_price):
        self.cursor.execute('SELECT * FROM offers WHERE price<=%i' % max_price)
        return self.cursor.fetchall()
    
    def insert_offer(self, token_id, contract_address, price, description):
        assert len(contract_address) == 42
        
        sql = 'INSERT INTO offers VALUES ("%i", "%s", "%f", "%s")'
        try:
            self.cursor.execute(sql % (token_id, contract_address, price, description))
            self.connection.commit()
        except sqlite3.DatabaseError as e:
            if 'UNIQUE' in str(e):
                sql = 'UPDATE offers SET price=%f WHERE token_id=%i'
                self.cursor.execute(sql % (price, token_id))
                self.connection.commit()      
            return False
        return True
        
    
    def insert_chat(self, _id, progress_message_id):
        sql = 'INSERT INTO chats VALUES ("%i", "%i")' 
        self.cursor.execute(sql % (_id, progress_message_id) )
        self.connection.commit()

    def close(self):
        self.connection.close()

if __name__ == "__main__":
    d = DataBase()

    d.insert_offer(400010051, 'a' * 42, 51, 'asd')
    
