####
# Copyright 2014 Cardiff University
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
####


from flask import Flask, render_template, request, redirect, Response, url_for, session
import time, os, uuid, json, base64, hmac, urllib, random, db_manager, api

app = Flask(__name__)
app.secret_key = "This should probably be set to something more secure and less visible."

ALLOWED_EXTENSIONS = set(['py'])

def generate_session():
    return uuid.uuid4()

def validate_session():
    if session == None:
        session['user'] = generate_session()
    if 'user' not in session:
        session['user'] = generate_session()
    if session['user'] == None:
        session['user'] = generate_session()
    
    global user
    user = str(session['user'])

@app.route('/')
def home():
    validate_session()
    robots = db_manager.get_robots_of_user(user) 
    others = db_manager.get_all_robots(user)
    return render_template('dashboard.html', user = user, robots = robots, robot_count = len(robots), others = others, other_count = len(others))
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload_robot', methods=['POST'])
def upload_robot():
    validate_session()
    file = request.files['robot_file']
    if file and allowed_file(file.filename):
        robot_name = file.filename.rsplit(".",1)[0]
        filename = user+"_"+str(uuid.uuid4())+".py"
        file.save('./robots/'+filename)
        
        saved_file = open('./robots/'+filename, "r")
        source = saved_file.read()
        saved_file.close()
        source = "from rgkit import rg\nfrom rgkit import comsc_bot\n"+source
        source = source.replace("class Robot:", "class Robot(comsc_bot.ComscBot):")
        source = source.replace("self.move(", "return super(Robot, self).move(")
        source = source.replace("self.move_to_location(", "return super(Robot, self).move_to_location(")
        source = source.replace("self.move_towards(", "return super(Robot, self).move_towards(rg, ")
        source = source.replace("self.attack(", "return super(Robot, self).attack(")
        source = source.replace("self.attack_location(", "return super(Robot, self).attack_location(")
        source = source.replace("self.guard(", "return super(Robot, self).guard(")
        source = source.replace("self.self_destruct(", "return super(Robot, self).self_destruct(")
        source = source.replace("game.center_location", "rg.CENTER_POINT")
        source = source.replace("game.get_distance(", "rg.dist(")
        source = source.replace("game.get_walking_distance(", "rg.wdist(")
        source = source.replace("game.get_location_types(", "rg.loc_types(")
        source = source.replace("game.get_surrounding_locations(", "rg.locs_around(")
        saved_file = open('./robots/'+filename, "w")
        saved_file.write(source)
        saved_file.close()
        
        result = api.create_robot(user, robot_name, filename)
        return json.dumps(result)
    else:
        return json.dumps({'error': True, 'message': 'Invalid file type'})

@app.route('/robot_source')
def view_robot_source():
    validate_session()    
    id = request.args.get('id')
    result = api.get_robot_source(user, id)
    return render_template('source.html', robot = result['robot'], source = result['source'], user=user)

@app.route('/delete_robot', methods=['GET'])
def delete_robot():
    validate_session()
    id = request.args.get('id')
    api.delete_robot(user, id)
    return redirect(url_for('home'))

@app.route('/battles')
def battles():
    validate_session()
    battles = db_manager.get_battles()
    leaderboard = db_manager.get_leaderboard()
    return render_template('battles.html', battles=battles, battle_count = len(battles), leaderboard = leaderboard)

@app.route('/test')
def test():
    validate_session()    
    robot_id = request.args.get('id')
    result = api.test(robot_id)
    result['opposee'] = user
    return render_template('battle.html', result = result, user = user, test = True)

@app.route('/battle')
def battle():
    validate_session()
    robot1_id = request.args.get('id1')
    robot2_id = request.args.get('id2')
    result = api.battle(user, robot1_id, robot2_id)
    return render_template('battle.html', result = result, user = user, test = False, )        

@app.route("/replay")
def replay():
    validate_session()
    battle_id = request.args.get('id')
    result = api.get_battle(battle_id)
    return render_template('battle.html', result = result, user = user, test = False, replay = True)

@app.route("/delete_all_data")
def clear_all():
    db_manager.clear_db()
    db_manager.clear_sources()
    return "Database cleared. <a href='/'>Return home</a>.";

# Main code
if __name__ == '__main__':
    db_manager.initalise()
    app.debug = False
    port = int(os.environ.get('PORT', 8088))
    app.run(host='0.0.0.0', port=port)
    
