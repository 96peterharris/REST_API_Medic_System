from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from sqlalchemy.orm import validates
from marshmallow import fields, validate

app = Flask(__name__) 
api = Api(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicSystem.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app) 
ma = Marshmallow(app)

#log ze statytykami np. czas wykonania innych komend / czas komunikacji z klientami
#zasoby - jak każde połączenie wpływa / zabezpieczenia wątków
#połączenie za pomocą zapytań sql
#wypłeninie losowe

####### User ##############

class User(db.Model): 
    user  = db.Table('user', 
    db.Column('id', db.Integer, primary_key=True),
    db.Column('pesel', db.String(11), unique=True),
    db.Column('password', db.String(32)),
    db.Column('first_name', db.String(32)),
    db.Column('last_name', db.String(32)),
    db.Column('research_result', db.BLOB))
    
    # @validates('pesel')
    # def check_pesel(self, key, value):
    #     if value.isDigit() == False or len(value) < 11:
    #         raise AssertionError("Bad pesel format!!!")
    #     return value

    def __init__(self, pesel, password, first_name, last_name, research_result):
        self.pesel = pesel
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.research_result

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'pesel', 'password', 'first_name', 'last_name', 'research_result')

user_schema = UserSchema() 
users_schema = UserSchema(many=True)

class UserManager(Resource): 
    @staticmethod
    def get():
        try: id = request.args['id']
        except Exception as _: id = None

        if not id:
            users = User.query.all()
            return jsonify(users_schema.dump(users))
        user = User.query.get(id)
        return jsonify(user_schema.dump(user))

    @staticmethod
    def get():
        try: pesel = request.args['pesel']
        except Exception as _: pesel = None

        if not pesel:
            users = User.query.all()
            return jsonify(users_schema.dump(users))
        user = User.query.filter_by(pesel=pesel).first()
        return jsonify(user_schema.dump(user))

    @staticmethod
    def post():
        pesel = request.json['pesel']
        password = request.json['password']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        research_result = request.json['research_result']

        user = User(pesel, password, first_name, last_name, research_result)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'Message': f'User {first_name} {last_name} inserted.'
        })
    
    @staticmethod
    def put():
        try: pesel = request.args['pesel']
        except Exception as _: pesel = None

        if not pesel:
            return jsonify({ 'Message': 'Must provide the user pesel' })

        user = User.query.get(pesel)
        pesel = request.json['pesel']
        password = request.json['password']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        research_result = request.json['research_result']
        
        user.pesel = pesel
        user.password = password
        user.first_name = first_name
        user.last_name = last_name
        user.research_result = research_result

        db.session.commit()
        return jsonify({
            'Message': f'User {first_name} {last_name} altered.'
        })

    @staticmethod
    def delete():
        try: pesel = request.args['pesel']
        except Exception as _: pesel = None

        if not pesel:
            return jsonify({ 'Message': 'Must provide the user pesel' })

        user = User.query.get(pesel)
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'Message': f'User {pesel} deleted.'
        })


api.add_resource(UserManager, '/api/users')

####### Employee ##############

class Employee(db.Model):
    employee  = db.Table('employee', 
    db.Column('id', db.Integer, primary_key=True),
    db.Column('username', db.String(32), unique=True),
    db.Column('password', db.String(32)),
    db.Column('first_name', db.String(32)),
    db.Column('last_name', db.String(32)))

    def __init__(self, username, password, first_name, last_name):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

class EmployeeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'first_name', 'last_name')

employee_schema = EmployeeSchema() 
employee_schema = EmployeeSchema(many=True)

class EmployeeManager(Resource): 
    @staticmethod
    def get():
        try: id = request.args['id']
        except Exception as _: id = None

        if not id:
            employees = Employee.query.all()
            return jsonify(employee_schema.dump(employees))
        employee = Employee.query.get(id)
        return jsonify(employee_schema.dump(employee))

    @staticmethod
    def get():
        try: username = request.args['username']
        except Exception as _: username = None

        if not username:
            employees = Employee.query.all()
            return jsonify(employee_schema.dump(employees))
        employee = Employee.query.filter_by(username=username).all()
        return jsonify(employee_schema.dump(employee))

    @staticmethod
    def post():
        username = request.json['username']
        password = request.json['password']
        first_name = request.json['first_name']
        last_name = request.json['last_name']

        employee = Employee(username, password, first_name, last_name)
        db.session.add(employee)
        db.session.commit()

        return jsonify({
            'Message': f'Employee {first_name} {last_name} inserted.'
        })
    
    @staticmethod
    def put():
        try: id = request.args['id']
        except Exception as _: id = None

        if not id:
            return jsonify({ 'Message': 'Must provide the employee ID' })

        employee = Employee.query.get(id)
        username = request.json['username']
        password = request.json['password']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
    
        employee.username = username
        employee.password = password
        employee.first_name = first_name
        employee.last_name = last_name

        db.session.commit()
        return jsonify({
            'Message': f'Employee {first_name} {last_name} altered.'
        })

    @staticmethod
    def delete():
        try: id = request.args['id']
        except Exception as _: id = None

        if not id:
            return jsonify({ 'Message': 'Must provide the user ID' })

        employee = Employee.query.get(id)
        db.session.delete(employee)
        db.session.commit()

        return jsonify({
            'Message': f'Employee {str(id)} deleted.'
        })

api.add_resource(EmployeeManager, '/api/employees')

if __name__ == '__main__':
    app.run(debug=True)