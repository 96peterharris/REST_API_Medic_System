from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from sqlalchemy.orm import validates
from marshmallow import fields, validate
import datetime
from sqlalchemy.sql import func

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
    db.Column('last_name', db.String(32)))

    def __init__(self, pesel, password, first_name, last_name):
        self.pesel = pesel
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'pesel', 'password', 'first_name', 'last_name')

user_schema = UserSchema() 
users_schema = UserSchema(many=True)

class UserManager(Resource):
    # @staticmethod
    # def get():
    #     try: id = request.args['id']
    #     except Exception as _: id = None

    #     if not id:
    #         users = User.query.all()
    #         return jsonify(users_schema.dump(users))
    #     user = User.query.get(id)
    #     return make_response(jsonify(user_schema.dump(user)),200)

    @staticmethod
    def get():
        try: pesel = request.args['pesel']
        except Exception as _: pesel = None

        if not pesel:
            users = User.query.all()
            return make_response(jsonify(users_schema.dump(users)),200)
        elif check_pesel(pesel) == False:
            return make_response(jsonify({ 'Message': 'Wrong pesel format!' }),400)
        else:
            user = User.query.filter_by(pesel=pesel).first()
            if user == None:
                return make_response(jsonify({ 'Message': 'Wrong pesel!' }),400)
            else:
                return make_response(jsonify(user_schema.dump(user)),200)

    @staticmethod
    def post():
        pesel = request.json['pesel']
        password = request.json['password']
        first_name = request.json['first_name']
        last_name = request.json['last_name']

        if check_pesel(pesel) == True and User.query.filter_by(pesel=pesel).first() == None:
            user = User(pesel, password, first_name, last_name)
            db.session.add(user)
            db.session.commit()
            return make_response(jsonify({'Message': f'User {first_name} {last_name} inserted.'}),201)
        else:
            return make_response(jsonify({ 'Message': 'Wrong credentials!' }),400)
       
    
    @staticmethod
    def put():
        try: pesel = request.args['pesel']
        except Exception as _: pesel = None

        if not pesel or check_pesel(pesel) == False:
            return jsonify({ 'Message': 'Must provide the proper user pesel' })

        user = User.query.filter_by(pesel=pesel).first()
        pesel = request.json['pesel']
        password = request.json['password']
        first_name = request.json['first_name']
        last_name = request.json['last_name']

        user.pesel = pesel
        user.password = password
        user.first_name = first_name
        user.last_name = last_name

        db.session.commit()
        return jsonify({'Message': f'User {first_name} {last_name} altered.'})

    @staticmethod
    def delete():
        try: pesel = request.args['pesel']
        except Exception as _: pesel = None

        if not pesel or check_pesel(pesel) == False:
            return make_response(jsonify({ 'Message': 'Must provide the user pesel' }),400)

        user = User.query.get(pesel)

        if user == None:
             return make_response(jsonify({ 'Message': 'User not exist!' }),404)

        db.session.delete(user)
        db.session.commit()

        return make_response(jsonify({'Message': f'User {pesel} deleted.'}),200)


api.add_resource(UserManager, '/api/users')

####### Results ###############

class Result(db.Model): 
    result  = db.Table('result', 
    db.Column('id', db.Integer, primary_key=True),
    db.Column('pesel', db.String(11), db.ForeignKey('user.pesel')),
    db.Column('username', db.String(32), db.ForeignKey('employee.username')),
    db.Column('result_date', db.DateTime, default=func.now()),
    db.Column('result_file', db.String(255)))
    # user = relationship("User", backref=backref("user", uselist=False))
    # employee = relationship("Employee", backref=backref("employee", uselist=False))

    def __init__(self, pesel, username, result_file):
        self.pesel = pesel
        self.username = username
        # self.result_date = datetime.date.today()
        self.result_file# = result_file

class ResultSchema(ma.Schema):
    class Meta:
        fields = ('id', 'pesel', 'username', 'result_date', 'result_file')
# 
result_schema = ResultSchema() 
results_schema = ResultSchema(many=True)

class ResultManager(Resource):
    @staticmethod
    def get():
        try: pesel = request.args['pesel']
        except Exception as _: pesel = None

        if not pesel:
            results = Result.query.all()
            return jsonify(results_schema.dump(results))
        elif check_pesel(pesel) == False:
            return make_response(jsonify({ 'Message': 'Wrong pesel format!' }),400)
        else:
            result = Result.query.filter_by(pesel=pesel).all()
            return jsonify(results_schema.dump(result))

    @staticmethod
    def post():
        pesel = request.json['pesel']
        username = request.json['username']
        result_file = request.json['result_file']

        if check_pesel(pesel) == True:
            result = Result(pesel, username, result_file)
            db.session.add(result)
            db.session.commit()
            return jsonify({'Message': f'Result for pesel: {pesel} inserted.'})
        else:
            return make_response(jsonify({ 'Message': 'Wrong pesel format!' }),400)
       
    
    @staticmethod
    def put():
        try: pesel = request.args['pesel']
        except Exception as _: pesel = None

        if not pesel or check_pesel(pesel) == False:
            return jsonify({ 'Message': 'Must provide the proper user pesel' })

        result = Result.query.filter_by(pesel=pesel).first()
        pesel = request.json['pesel']
        result_file = result_file.json['result_file']

        user.pesel = pesel
        user.result_file = result_file

        db.session.commit()
        return jsonify({'Message': f'Result for Pesel {pesel} altered.'})

    @staticmethod
    def delete():
        try: pesel = request.args['pesel']
        except Exception as _: pesel = None

        if not pesel or check_pesel(pesel) == False:
            return jsonify({ 'Message': 'Must provide the user pesel' })

        result = Result.query.get(pesel)
        db.session.delete(result)
        db.session.commit()

        return jsonify({
            'Message': f'Result for pesel: {pesel} deleted.'
        })


api.add_resource(ResultManager, '/api/results')

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
employees_schema = EmployeeSchema(many=True)

class EmployeeManager(Resource): 
    # @staticmethod
    # def get():
    #     try: id = request.args['id']
    #     except Exception as _: id = None

    #     if not id:
    #         employees = Employee.query.all()
    #         return jsonify(employee_schema.dump(employees))
    #     employee = Employee.query.get(id)
    #     return jsonify(employee_schema.dump(employee))

    @staticmethod
    def get():
        try: username = request.args['username']
        except Exception as _: username = None

        if not username:
            employees = Employee.query.all()
            return make_response(jsonify(employees_schema.dump(employees)),200)
        elif Employee.query.filter_by(username=username).all() == None:
            return make_response(jsonify({ 'Message': 'Employee not exist!' }),404)
        else:
            employee = Employee.query.filter_by(username=username).first()
            return make_response(jsonify(employee_schema.dump(employee)),200)

    @staticmethod
    def post():
        username = request.json['username']
        password = request.json['password']
        first_name = request.json['first_name']
        last_name = request.json['last_name']

        if Employee.query.filter_by(username=username).first() != None:
            return make_response(jsonify({'Message': 'This username is used!'}),400)
        else:
            employee = Employee(username, password, first_name, last_name)
            db.session.add(employee)
            db.session.commit()
            return make_response(jsonify({'Message': f'Employee {first_name} {last_name} inserted.'}),201)
    
    @staticmethod
    def put():
        try: username = request.args['username']
        except Exception as _: username = None

        if not username:
            return jsonify({ 'Message': 'Must provide the employee \"username\"' })
        elif Employee.query.filter_by(username=username).all() == None:
            return make_response(jsonify({ 'Message': 'Employee not exist!' }),404)
        else:
            employee = Employee.query.filter_by(username=username).first()
            password = request.json['password']
            employee.password = password
            db.session.commit()
            return jsonify({'Message': f'Employee {employee.first_name} {employee.last_name} altered.'})
      

    @staticmethod
    def delete():
        try: username = request.args['username']
        except Exception as _: username = None

        if not username:
            return jsonify({ 'Message': 'Must provide the employee \"username\"' })
        elif Employee.query.filter_by(username=username).all() == None:
            return make_response(jsonify({ 'Message': 'Employee not exist!' }),404)
        else:
            employee = Employee.query.filter_by(username=username).first()
            db.session.delete(employee)
            db.session.commit()
            return make_response(jsonify({'Message': f'Employee {username} deleted.'}),200)

api.add_resource(EmployeeManager, '/api/employees')

def check_pesel(pesel):
        if len(pesel) == 11 and pesel.isdigit():
            return True
        else:
            return False


if __name__ == '__main__':
    app.run(debug=True)