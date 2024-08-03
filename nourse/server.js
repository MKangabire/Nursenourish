const express = require('express');
const mysql = require('mysql');
const bodyParser = require('body-parser');
const bcrypt = require('bcrypt');
const path = require('path');

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('static')); // Serve static files
app.set('views', path.join(__dirname, 'templates')); // Set views directory
app.set('view engine', 'ejs'); // Optional: if using a template engine

const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'your_mysql_password',
    database: 'nourish'
});

db.connect((err) => {
    if (err) throw err;
    console.log('Connected to database');
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'login.html'));
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const query = 'SELECT * FROM users WHERE username = ?';

    db.query(query, [username], (err, results) => {
        if (err) return res.status(500).send('Server error');
        if (results.length === 0) return res.status(401).send('Invalid username or password');

        const user = results[0];
        bcrypt.compare(password, user.password, (err, isMatch) => {
            if (err) return res.status(500).send('Server error');
            if (!isMatch) return res.status(401).send('Invalid username or password');

            res.redirect('/home');
        });
    });
});

app.get('/main', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'home.html'));
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
