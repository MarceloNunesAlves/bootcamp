import sqlite3

def initDb():
    c = sqlite3.connect('./recommendation.db')
    # Create table
    c.execute("CREATE TABLE if not exists client (id_grupo varchar(1), id_produto varchar(20))")
    c.close()

def putRecommendation(id_grupo, id_produto):
    c = sqlite3.connect('./recommendation.db')
    # Insert a row of data
    c.execute("INSERT INTO client VALUES (?, ?)", [id_grupo, id_produto])
    # Save (commit) the changes
    c.commit()
    c.close()

def removerRecommendation(id_grupo):
    c = sqlite3.connect('./recommendation.db')
    # Insert a row of data
    c.execute("DELETE FROM client WHERE id_grupo = ?", [id_grupo])
    # Save (commit) the changes
    c.commit()
    c.close()

def getRecommendation(id_grupo):
    c = sqlite3.connect('./recommendation.db')
    # Insert a row of data
    tuplaDados = c.execute("SELECT id_produto FROM client WHERE id_grupo = ? group by id_produto having count(*)>2", [id_grupo]).fetchall()
    if tuplaDados == None:
        return None
    else:
        return tuplaDados
    c.close()