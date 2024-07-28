import psycopg2

def create_db(conn):    
    with conn.cursor() as cur:
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS client(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(256) UNIQUE NOT NULL     
        );
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone_data(
            id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES client(id),
            phone_number VARCHAR(15) UNIQUE CHECK (phone_number ~ '^[0-9]*$')    
        );
        """) 
        conn.commit() 
    print('database created')  

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO client(first_name, last_name, email)
        VALUES(%s, %s, %s)        
        RETURNING id;
        """, (first_name, last_name, email))
        client_id = cur.fetchone()[0] 
        
        if phones:
            for phone in phones:
                cur.execute("""
                INSERT INTO phone_data(client_id, phone_number)
                VALUES(%s, %s);
                """, (client_id, phone))
                conn.commit()    
    print('client added', client_id, first_name, last_name, email, phones) 
                 
def add_phone(conn, client_id, phone_number):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO phone_data (client_id, phone_number)
        VALUES (%s, %s);
        """, (client_id, phone_number))
        conn.commit()
    print('phone added', client_id, phone_number) 

def change_client(conn, client_id, first_name=None, last_name=None,
                  email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
            UPDATE client 
            SET first_name=%s 
            WHERE id=%s;
            """, (first_name, client_id))
            conn.commit()            
        
        if last_name:
            cur.execute("""
            UPDATE client 
            SET last_name=%s 
            WHERE id=%s;
            """, (last_name, client_id))
            conn.commit()
            
        if email:
            cur.execute("""
            UPDATE client 
            SET email=%s 
            WHERE id=%s;
            """, (email, client_id)) 
            conn.commit()
        
        if phones:
            cur.execute("""
            DELETE 
            FROM phone_data 
            WHERE client_id=%s;            
            """, (client_id,))
            conn.commit()
            for phone_number in phones:
                add_phone(conn, client_id, phone_number)
    print('client data has been changed', client_id)

def delete_phone(conn, client_id, phone_number):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE 
        FROM phone_data 
        WHERE client_id=%s AND phone_number=%s;            
        """, (client_id, phone_number))        
        conn.commit()
    print('phone number deleted', client_id, phone_number)

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE 
        FROM phone_data 
        WHERE client_id=%s;            
        """, (client_id,))        

        cur.execute("""
        DELETE 
        FROM client 
        WHERE id=%s;            
        """, (client_id,))
        conn.commit() 
    print('client deleted', client_id) 
        
def find_client(conn, first_name=None, last_name=None, email=None,
                phone_number=None):
    with conn.cursor() as cur:
        if email:
            cur.execute("""
            SELECT c.id, c.first_name, 
            c.last_name, c.email, pd.phone_number
            FROM client c
            LEFT JOIN phone_data pd ON c.id = pd.client_id 
            WHERE email=%s;  
            """, (email,))
            return cur.fetchall()
        elif phone_number:
            cur.execute("""
            SELECT pd.client_id, c.first_name,
            c.last_name, c.email, pd.phone_number 
            FROM phone_data pd
            LEFT JOIN client c ON c.id = pd.client_id
            WHERE phone_number=%s;
            """, (phone_number,))
            return cur.fetchall()
        elif first_name:
            if last_name:
                cur.execute("""
                SELECT c.id, c.first_name,
                c.last_name, c.email, pd.phone_number 
                FROM client c
                LEFT JOIN phone_data pd ON c.id = pd.client_id                 
                WHERE first_name=%s AND last_name=%s;
                """, (first_name, last_name)) 
                return cur.fetchall() 
            else:
                cur.execute("""
                SELECT c.id, c.first_name,
                c.last_name, c.email, pd.phone_number 
                FROM client c
                LEFT JOIN phone_data pd ON c.id = pd.client_id 
                WHERE first_name=%s;
                """, (first_name,)) 
                return cur.fetchall()                                                      
        elif last_name:
            cur.execute("""
            SELECT c.id, c.first_name,
            c.last_name, c.email, pd.phone_number 
            FROM client c
            LEFT JOIN phone_data pd ON c.id = pd.client_id 
            WHERE last_name=%s;
            """, (last_name,)) 
            return cur.fetchall() 

if __name__ == '__main__':
    
    print('enter Database')
    database = input()
    print('enter Username')
    user = input()
    print('enter Password')
    password = input() 
    
    with psycopg2.connect(database=database,
                          user=user,
                          password=password) as conn: 
        
        with conn.cursor() as cur:
            cur.execute("""
            DROP TABLE IF EXISTS phone_data;
            DROP TABLE IF EXISTS client;            
            """)
            conn.commit()
            
        create_db(conn)
        
        add_client(conn, 'Han', 'Solo', 'hansolo@mail.ru', ['880000000000'])
        add_client(conn, 'Luke', '2', 'luk2@mail.ru', ['123456987'])
        add_client(conn, 'Luke', 'Skywalker',
                   'LukeSkywalker@mail.ru', ['880000000001', '880000000002'])
        add_client(conn, 'R2', 'D2', 'R2D2@mail.ru', [])
        
        print(id := find_client(conn, email='hansolo@mail.ru'))        
        id = id[0][0]        
        add_phone(conn, id, '1234556')
        print(find_client(conn, email='hansolo@mail.ru'))
        change_client(conn, id, 
                        first_name='Boba', 
                        last_name='Fett',
                        email='bobafett@mail.ru',
                        phones=['26262'])
        print(find_client(conn, email='hansolo@mail.ru'))
        
        print(id := find_client(conn, email='bobafett@mail.ru'))
        id = id[0][0]
        delete_phone(conn, id, '26262')
        print(find_client(conn, email='bobafett@mail.ru'))
        delete_client(conn, id)
        print(find_client(conn, email='bobafett@mail.ru'))
        
        print(find_client(conn, phone_number='880000000001'))
        print(find_client(conn, first_name='Luke', last_name='Skywalker'))
        print(find_client(conn, first_name='Luke'))
        print(find_client(conn, first_name='R2'))
        print(find_client(conn, last_name='Skywalker'))
        
    conn.close()
     
                  
               
    