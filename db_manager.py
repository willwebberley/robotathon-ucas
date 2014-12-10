####
# Copyright 2014 Cardiff University
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
####


import sqlite3, os

def connect():
    con = sqlite3.connect("main.db")
    con.row_factory = sqlite3.Row
    c = con.cursor()
    return (con, c)

def disconnect(con):
    con.close()

def initalise():
    print "Initialising database..."
    con, c = connect()
    c.execute("CREATE TABLE IF NOT EXISTS robot (robot_id TEXT, user_id TEXT, robot_name TEXT, robot_file TEXT, status NUMBER, score NUMBER)")
    c.execute("CREATE TABLE IF NOT EXISTS battle (battle_id TEXT, user1_id TEXT, user2_id TEXT, robot1_id TEXT, robot2_id TEXT, robot1_name TEXT, robot2_name, timestamp NUMBER, score1 NUMBER, score2 NUMBER, history TEXT)")
    con.commit()
    disconnect(con)

def clear_db():
    con, c = connect()
    c.execute("DELETE FROM robot")
    c.execute("DELETE FROM battle")
    con.commit()
    disconnect(con)

def clear_sources():
    folder = './robots'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            print e

def get_battle(battle_id):
    con, c = connect()
    row = c.execute("SELECT * FROM battle WHERE battle_id=?", [battle_id]).fetchone()
    disconnect(con)
    return row

def get_battles():
    con, c = connect()
    rows = c.execute("SELECT * FROM battle ORDER BY timestamp DESC LIMIT 30").fetchall()
    disconnect(con)
    return rows

def store_battle(battle_id, user1_id, user2_id, robot1_id, robot2_id, robot1_name, robot2_name, timestamp, score1, score2, history):
    con, c = connect()
    c.execute("INSERT INTO battle VALUES(?,?,?,?,?,?,?,?,?,?,?)", [battle_id, user1_id, user2_id, robot1_id, robot2_id, robot1_name, robot2_name, timestamp, score1, score2, history])
    con.commit()
    disconnect(con)

def update_robot_score(robot, score):
    con, c = connect()
    c.execute("UPDATE robot SET score = ? WHERE robot_id = ?", [score, robot['robot_id']])
    con.commit()
    disconnect(con)
 
def get_robots_of_user(id):
    con, c = connect()
    rows = c.execute("SELECT * FROM robot WHERE user_id= ?", [id]).fetchall()
    disconnect(con)
    return rows 

def get_leaderboard():
    con, c = connect()
    rows = c.execute("SELECT * FROM robot ORDER BY score DESC LIMIT 4").fetchall()
    disconnect(con)
    return rows 

def get_all_robots(user_id):
    con,c = connect()
    rows = c.execute("SELECT * FROM robot where status = 1 AND user_id !=?",[user_id]).fetchall()
    disconnect(con)
    return rows

def get_robot_by_id(id):
    con, c = connect()
    row = c.execute("SELECT * FROM robot WHERE robot_id= ?", [id]).fetchone()
    disconnect(con)
    return row 

def get_robot_by_name(name):
    con, c = connect()
    row = c.execute("SELECT * FROM robot WHERE robot_name= ?", [name]).fetchone()
    disconnect(con)
    return row 

def get_robot_source(robot):
    robot_file = open('./robots/'+robot['robot_file'], 'r')
    source = robot_file.read()
    robot_file.close()
    return source

def create_robot(robot_id, user_id, robot_name, robot_file):
    con, c = connect()
    c.execute("INSERT INTO robot VALUES(?,?,?,?,0,1400)", [robot_id, user_id, robot_name, robot_file])
    con.commit()
    disconnect(con)

def robot_tested(robot_id, status):
    con, c = connect()
    if status == True:
        c.execute("UPDATE robot SET status = 1 WHERE robot_id = ?", [robot_id])
    if status == False:
        c.execute("UPDATE robot SET status = -1 WHERE robot_id = ?", [robot_id])
    con.commit()
    disconnect(con)    

def delete_robot(robot_id):
    con, c = connect()
    c.execute("DELETE FROM robot WHERE robot_id = ?", [robot_id])
    con.commit()
    disconnect(con)
