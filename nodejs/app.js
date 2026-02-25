const express = require("express");
const app = express ();
const http = require("http");
const path = require("path");
const cookieParser = require("cookie-parser");
const server = http.createServer(app);

const port = process.env.PORT || 8080;

app.use(express.static("./client"));
app.use(cookieParser());
app.use(express.json());

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "client/index.html"));
});

app.get("/login", (req, res) => {
    res.sendFile(path.join(__dirname, "client/login.html"));
});

app.get("/admin", async (req, res) => {
    const token = req.cookies.token;
    if (!token) {
        return res.redirect('/login');
    }
    const response = await fetch('http://localhost:8000/token', {
        method: 'GET',
        headers: { 'Cookie': `token=${token}` }
    });
    if (!response.ok) {
        return res.redirect('/login');
    }
    res.sendFile(path.join(__dirname, "client/admin.html"));
});

app.get("/upload", async (req, res) => {
    const token = req.cookies.token;
    if (!token) {
        return res.redirect('/login');
    }
    const response = await fetch('http://localhost:8000/token', {
        method: 'GET',
        headers: { 'Cookie': `token=${token}` }
    });
    if (!response.ok) {
        return res.redirect('/login');
    }
    res.sendFile(path.join(__dirname, "client/shenanigans.html"));
});

server.listen(port, () => console.log('Server running on port', port));
