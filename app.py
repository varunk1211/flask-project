from flask import Flask,render_template
app = Flask(__name__)
b = [
    {
        'id': 1,
        'name': 'varun',
    },
    {
        'id': 2,
        'name': 'rohit',
    }
]
@app.route('/')
def hello():
    return render_template('index.html',data=b)
if __name__ == '__main__':
    app.run()
