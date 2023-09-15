"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorite_people, Favorite_planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


#-------------GET------------

@app.route('/users', methods=['GET'])
def users():

    usuarios = User.query.all()

    data = []
    for user in usuarios:
        data.append(user.serialize())
       

    return jsonify(data), 200

@app.route('/people', methods=['GET'])
def people():

    characters = People.query.all()

    data = []
    for people in characters:
        data.append(people.serialize())

    return jsonify(data), 200


@app.route('/planets', methods=['GET'])
def planets():

    planetas = Planets.query.all()

    data = []
    for planets in planetas:
        data.append(planets.serialize())

    return jsonify(data)

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):

    person = People.query.filter_by(id = people_id).first()

    data = []
    for people in person:
        data.append(people.serialize())
       

    return jsonify(data), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):

    planet = Planets.query.filter_by(id = planet_id).first()

    data = []
    for planets in planet:
        data.append(planets.serialize())
       

    return jsonify(data), 200


@app.route('/<int:user_id>/favorite_planets', methods=['GET'])
def get_user_favorite_planets(user_id):

    user_planetas_favoritos = Favorite_planets.query.filter_by(user_id = user_id).all()
    
    if not user_planetas_favoritos:
        return {"No favorite"}
    
    serialized_favorite_planet = [{
        "ID": favorite.planet_id,
        "Planet name": Planets.query.get(favorite.planet_id).name
    } for favorite in user_planetas_favoritos]
    return {"Planetas favoritos del usuario": serialized_favorite_planet}, 200


@app.route('/<int:user_id>/favorite_people', methods=['GET'])
def get_user_favorite_people(user_id):

    user_personas_favoritas = Favorite_people.query.filter_by(user_id = user_id).all()
    
    if not user_personas_favoritas:
        return {"No favorite"}
    
    serialized_favorite_people = [{
        "ID": favorite.people_id,
        "Planet name": People.query.get(favorite.people_id).name
    } for favorite in user_personas_favoritas]
    return {"Planetas favoritos del usuario": serialized_favorite_people}, 200


@app.route('/favorite_planets', methods=['GET'])
def favorite_planets():

    planetas_favs = Favorite_planets.query.all()

    data = []
    for planeta in planetas_favs:
        data.append(planeta.serialize())

    return jsonify(data), 200

@app.route('/favorite_people', methods=['GET'])
def favorite_people():

    personas_favs = Favorite_people.query.all()

    data = []
    for persona in personas_favs:
        data.append(persona.serialize())

    return jsonify(data), 200



#-------------------POST--------------

@app.route('/people', methods=['POST'])
def peoplePost():
    
    body = request.get_json()
    personas = People(
        name=body['name'],
        gender=body['gender']
    )
    db.session.add(personas)
    db.session.commit()
    response_body = {
    "msg": "People added correctly"
    }
    return jsonify(response_body),200


@app.route('/planets', methods=['POST'])
def planetsPost():

    body = request.get_json()
    planetas = Planets(
        name=body['name'],
        climate=body['climate']
    )
    db.session.add(planetas)
    db.session.commit()
    response_body = {
        "msg": "Planets added correctly"
    }
    return jsonify(response_body),200


@app.route('/favorite_planets', methods=['POST'])
def favorite_planets_post():

    body = request.get_json()
    favoritos_planetas = Favorite_planets(
        user_id=body['user_id'],
        planet_id=body['planet_id']
    )
    db.session.add(favoritos_planetas)
    db.session.commit()
    response_body = {
        "msg": "Favorite planet added correctly"
    }
    return jsonify(response_body),200


@app.route('/favorite_people', methods=['POST'])
def favorite_people_post():


    body = request.get_json()
    favoritos_personas = Favorite_people(
        user_id=body['user_id'],
        people_id=body['people_id']
    )
    db.session.add(favoritos_personas)
    db.session.commit()
    response_body = {
        "msg": "Favorite people added correctly"
    }
    return jsonify(response_body),200
    

@app.route('/user/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def post_user_favplanet(user_id, planet_id):

    user = User.query.get(user_id)
    if not user:
        return {"error": "El usuario no existe"}, 404
    
    planet = Planets.query.get(planet_id)
    if not planet:
        return {"error": "El planeta no existe"}, 404
    
    new_fav_planet = Favorite_planets(user_id=user_id, planet_id=planet_id)
    db.session.add(new_fav_planet)
    db.session.commit()
    response_body = {
        "msg": "Favorite planet added correctly"
    }
    
    return jsonify(response_body),200


@app.route('/user/<int:user_id>/people/<int:people_id>', methods=['POST'])
def post_user_favpeople(user_id, people_id):

    user = User.query.get(user_id)
    if not user:
        return {"error": "El usuario no existe"}, 404
    
    planet = People.query.get(people_id)
    if not people:
        return {"error": "El personaje no existe"}, 404
    
    new_fav_people = Favorite_people(user_id=user_id, people_id=people_id)
    db.session.add(new_fav_people)
    db.session.commit()
    response_body = {
        "msg": "Favorite people added correctly"
    }
    
    return jsonify(response_body),200
 




#--------------------DELETE-----------
@app.route('/favorite_people/<int:people_id>', methods=['DELETE'])
def delete_people(people_id):

    delete_people = Favorite_people.query.get(people_id)
   
    if not delete_people:
        return jsonify("No existe"),
    
    db.session.delete(delete_people)
    db.session.commit()

    return jsonify("The person has been deleted successfully"), 200

@app.route('/favorite_planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):

    delete_planet = Favorite_planets.query.get(planet_id)
   
    if not delete_planet:
        return jsonify("No existe"),
    
    db.session.delete(delete_planet)
    db.session.commit()

    return jsonify("The planet has been deleted successfully"), 200

    


    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)