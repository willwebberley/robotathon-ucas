####
# Copyright 2014 Cardiff University
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
####


import db_manager
import uuid, random, hashlib, time, json, os
from elo import rate_1vs1
from rgkit import run

def create_robot(user, robot_name, filename):
    result = {}
    name_row = db_manager.get_robot_by_name(robot_name)
    if name_row is not None:
        result['error'] = True
        result['message'] = 'There is already another robot with that name.'
        return result
    robot_id = str(uuid.uuid4())
    db_manager.create_robot(robot_id, user, robot_name, filename)
    result['error'] = False
    return result

def delete_robot(user, robot_id):
    result = {}
    robot = db_manager.get_robot_by_id(robot_id)
    if robot == None:
        result['error'] = True
        result['message'] = 'Invalid robot.'
        return result
    if robot['user_id'] != user:
        result['error'] = True
        result['message'] = 'Auth error.'
        return result
    db_manager.delete_robot(robot_id)
    result['error'] = False
    return result

def get_all_robots(user):
    robots = db_manager.get_all_robots(user)
    return robots 

def get_robot_source(user, robot_id):
    result = {}
    robot = db_manager.get_robot_by_id(robot_id)
    if robot == None:
        result['error'] = True
        result['message'] = 'Invalid robot.'
        return result
    if robot['user_id'] != user:
        result['error'] = True
        result['message'] = 'Auth error.'
        return result
    source = db_manager.get_robot_source(robot)
    result['error'] = False
    result['robot'] = robot
    result['source'] = source
    return result

def run_battle(robot1, robot2):
    result = {}
    result['robot1'] = robot1
    result['robot2'] = robot2
    if robot1 == None or robot2 == None:
        result['error'] = True
        result['messgae'] = 'There is an invalid robot.'
        return result
    robot1_file = './robots/'+robot1['robot_file']
    robot2_file = './robots/'+robot2['robot_file']
    try: 
        runner = run.Runner(player1_file=robot1_file, player2_file=robot2_file)
        runner.run()
        game = runner.game 
        options = runner.options
        history = game.get_history()
        scores = game.get_scores() 
        
        map_file = open(options.map_filepath, 'r')
        map = map_file.read()
        map_file.close()    
        for item in history:
            for item2 in item:
                item2['location'] = [item2['location'][0],item2['location'][1]]

        result['map'] = map.replace("(","[").replace(")","]")
        result['error'] = False
        result['scores'] = scores
        result['history'] = history
        return result
    except Exception as e:
        result['error'] = True
        return result

def test(robot_id):
    robot = db_manager.get_robot_by_id(robot_id)
    result = run_battle(robot, robot)
    if result['error'] == False:
        db_manager.robot_tested(robot_id, True)
    else:
        db_manager.robot_tested(robot_id, False)
    return result

def battle(user, robot1_id, robot2_id):
    if robot1_id == robot2_id:
        return {'error': True, 'message': 'Robots cannot battle themselves.'}
    robot1 = db_manager.get_robot_by_id(robot1_id)
    if robot1['user_id'] != user:
        return {'error':True, 'message':'Auth error.'}
    robot2 = db_manager.get_robot_by_id(robot2_id)
    if robot1['user_id'] == robot2['user_id']:
        return {'error': True, 'message': 'Users cannot battle themselves.'}
    result = run_battle(robot1, robot2)
    result['opposer'] = robot1['user_id'] 
    result['opposee'] = robot2['user_id'] 
    
    if result['error'] == False:
        rating = (robot1['score'], robot2['score'])
        if result['scores'][0] > result['scores'][1]:
            rating = rate_1vs1(robot1['score'], robot2['score'])
        if result['scores'][1] > result['scores'][0]:
            rating = rate_1vs1(robot2['score'], robot1['score'])

        db_manager.update_robot_score(robot1, int(round(rating[0])))
        db_manager.update_robot_score(robot2, int(round(rating[1]))) 

        timestamp = int(time.time())
        battle_id = str(uuid.uuid4())
        db_manager.store_battle(battle_id, user, robot2['user_id'], robot1_id, robot2_id, robot1['robot_name'], robot2['robot_name'], timestamp, result['scores'][0], result['scores'][1], json.dumps(result['history']))
    return result

def get_battle(battle_id):
    battle = db_manager.get_battle(battle_id)
    result = {}
    
    map_file = open('./rgkit/maps/default.py', 'r')
    map = map_file.read()
    map_file.close()    

    history = json.loads(battle['history'])
    for item in history:
        for item2 in item:
            item2['location'] = [item2['location'][0],item2['location'][1]]

    result['timestamp'] = battle['timestamp']
    result['map'] = map.replace("(","[").replace(")","]")
    result['error'] = False
    result['scores'] = []
    result['scores'].append(battle['score1'])
    result['scores'].append(battle['score2'])
    result['history'] = (json.dumps(history)).replace("u'",";")
    result['robot1'] = {}
    result['robot1']['robot_name'] = battle['robot1_name'];
    result['robot2'] = {}
    result['robot2']['robot_name'] = battle['robot2_name'];
    print result['scores']

    return result
