from application import app, db, api
from flask import render_template, request, json, jsonify, Response, redirect, flash, url_for, session
from application.models import User, Constituency, BlockChain
from application.forms import LoginForm, RegisterForm, ConstituencyForm
from flask_restplus import Resource
from application.course_list import course_list
import hashlib, datetime, json
from pymongo import command_cursor

courseData = [
    {"courseID": "1111", "title": "PHP 111", "description": "Intro to PHP", "credits": "3", "term": "Fall, Spring"},
    {"courseID": "2222", "title": "Java 1", "description": "Intro to Java Programming", "credits": "4",
     "term": "Spring"},
    {"courseID": "3333", "title": "Adv PHP 201", "description": "Advanced PHP Programming", "credits": "3",
     "term": "Fall"}, {"courseID": "4444", "title": "Angular 1", "description": "Intro to Angular", "credits": "3",
                       "term": "Fall, Spring"},
    {"courseID": "5555", "title": "Java 2", "description": "Advanced Java Programming", "credits": "4", "term": "Fall"}]


#######################################

@api.route('/api', '/api/')
class GetAndPost(Resource):

    # GET ALL
    def get(self):
        return jsonify(User.objects.all())

    # POST
    def post(self):
        data = api.payload
        user = User(user_id=data['user_id'], email=data['email'], first_name=data['first_name'],
                    last_name=data['last_name'])
        user.set_password(data['password'])
        user.save()
        return jsonify(User.objects(user_id=data['user_id']))


@api.route('/api/<idx>')
class GetUpdateDelete(Resource):

    # GET ONE
    def get(self, idx):
        return jsonify(User.objects(user_id=idx))

    # PUT
    def put(self, idx):
        data = api.payload
        User.objects(user_id=idx).update(**data)
        return jsonify(User.objects(user_id=idx))

        # DELETE

    def delete(self, idx):
        User.objects(user_id=idx).delete()
        return jsonify("User is deleted!")


#######################################

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", title="Home", index=True)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.objects(email=email).first()
        if user:
            if user.get_password(password):
                session['user_id'] = user.user_id
                session['username'] = user.first_name
                session['email'] = user.email
                flash(f"{user.first_name}, you are successfully logged in!", "success")
                return redirect("/index")
            else:
                flash(f"{user.first_name}, Incorrect Password!", "danger")
                return redirect("/index")
        else:
            flash("Invalid Email ID", "danger")
    return render_template("login.html", title="Login", form=form, login=True)


@app.route("/logout")
def logout():
    session['user_id'] = False
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/constituency/")
@app.route("/constituency/<term>")
def constituency(term=None):
    if term is None:
        term = "2021 "

    constituency = Constituency.objects.order_by("constituencyID")
    return render_template("constituency.html", constituencyData=constituency, title="cons", courses=True, term=term)


@app.route("/register", methods=['POST', 'GET'])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = list(User.objects.all())
        user_id = user_id[-1]['user_id']
        user_id += 1
        email = form.email.data
        voterid = form.voterid.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User(user_id=user_id, voterid=voterid, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!", "success")
        return redirect(url_for('index'))
    return render_template("register.html", title="Register", form=form, register=True)


@app.route("/userpage", methods=["GET", "POST"])
def userpage():
    if not session.get('username'):
        return redirect(url_for('login'))

    voted = BlockChain.objects(email=session.get('email')).first()

    totalVotes=BlockChain.objects.all()


    if not voted:

        party = request.form.get('party')
        if party:

            user_id = session.get('user_id')
            email = session.get('email')
            timestamp = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            entries = list(BlockChain.objects.all())
            prevhash = entries[-1]["curhash"]
            candidate = request.form.get('candidate')
            curhash = hashlib.sha256(
                json.dumps({"user_id": user_id, "name": session.get('username'), "prevhash": prevhash, "email": email,
                            "party": party, "timestamp": timestamp, "candidate": candidate}).encode()).hexdigest()

            d1 = BlockChain(user_id=user_id, name=session.get('username'), party=party, timestamp=timestamp, email=email,
                            prevhash=prevhash, curhash=curhash, candidate=candidate)
            d1.save()
            flash("You are successfully Voted!", "success")
            return redirect(url_for('index'))
        else:
            return redirect(url_for("constituency"))

    return render_template("userpage.html", enrollment=True, title="Enrollment", totalVotes=totalVotes, voted=voted)
    # classes = course_list(user_id)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    # votes = blockchain.insert_one({"Name":"harsh"})
    if not session.get('username'):
        return redirect(url_for('login'))

    votes = list(BlockChain.objects.aggregate(*[
        {
            '$group': {
                '_id': '$party',
                'count': {
                    '$sum': 1
                }
            }
        }
    ]))

    totalVotes=BlockChain.objects.all()

    return render_template("admin.html", votes=votes, title="Admin", totalVotes=totalVotes, admin=True)


@app.route("/addCandidates", methods=["GET", "POST"])
def add():
    if session['user_id'] != "Admin":
        redirect(url_for('login'))

    form = ConstituencyForm()
    if form.validate_on_submit():

        constituencyID = form.constituencyID.data
        constituency = form.constituency.data
        candidate = form.candidate.data
        party = form.party.data
        term = form.term.data

        con = Constituency(constituencyID=constituencyID, constituency=constituency, party=party, candidate=candidate, term=term)
        con.save()
        flash("You are successfully added !", "success")
        redirect(url_for('constituency'))

    return render_template("addCandidate.html", form=form, title="add")


@app.route("/success", methods=["GET", "POST"])
def success():
    if session['email']:
        render_template('success.html')
    render_template('success.html')

# @app.route("/api/")
# @app.route("/api/<idx>")
# def api(idx=None):
#     if(idx == None):
#         jdata = courseData
#     else:
#         jdata = courseData[int(idx)]

#     return Response(json.dumps(jdata), mimetype="application/json")


@app.route("/user")
def user():
    # User(user_id=1, first_name="Christian", last_name="Hur", email="christian@uta.com", password="abc1234").save()
    # User(user_id=2, first_name="Mary", last_name="Jane", email="mary.jane@uta.com", password="password123").save()
    if not session.get('username'):
        return redirect(url_for('login'))

    users = User.objects.all()
    return render_template("user.html", users=users)
