from flask import Flask
import Controllers.crudController as contr

app = Flask(__name__)

app.route('/create', methods=['POST'])(contr.create)
app.route('/read', methods=['GET'])(contr.read)
app.route('/update', methods=['POST'])(contr.update)
app.route('/delete', methods=['DELETE'])(contr.delete)

