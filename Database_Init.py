from cassandra.cluster import Cluster

cluster = Cluster()
dbsession = cluster.connect()
dbsession.execute("CREATE KEYSPACE intro with replication = {'class': 'SimpleStrategy', 'replication_factor':1};")
dbsession.execute("USE intro;")
dbsession.execute("CREATE TABLE employees (id INT PRIMARY KEY, name TEXT, surname TEXT, age INT);")
dbsession.execute("INSERT INTO employees (id, name, surname, age) values (1001, 'John', 'Smith', 41);")
dbsession.execute("INSERT INTO  employees (id, name, surname, age) values (1002, 'Alice', 'Thomson', 30);")

