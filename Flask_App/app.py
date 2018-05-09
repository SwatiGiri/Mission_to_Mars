from flask import Flask, render_template, jsonify, redirect
import pymongo


app = Flask(__name__)


conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars
collection = db.mars


@app.route('/')
def index():
    # Gettint the latest entry in the db
    # TOOD: optimize it to only get the latest entry
    all_data = list(db.collection.find()) 
    data = all_data[len(all_data) - 1]

    return render_template('index.html', data=data)


@app.route('/scrape')
def scrape():
    import scrape_script
    print("Getting new Data, I swear!")
    scrape_script.scrape_and_push_to_db()
    return redirect("http://localhost:5000/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
