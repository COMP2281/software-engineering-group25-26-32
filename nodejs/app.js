const DEV_URL = "http://localhost:8000";
const express = require("express");
const app = express ();
const http = require("http");
const path = require("path");
const cookieParser = require("cookie-parser");
const server = http.createServer(app);
const port = process.env.PORT || 8080;
const { loadEnvFile } = require('node:process');
loadEnvFile('../python/.env');
let API_URL = process.env.API_DOMAIN || DEV_URL;
if (!API_URL.startsWith("http")) {
    API_URL = "https://" + API_URL;
}
app.use(express.static("./client"));
app.use(cookieParser());
app.use(express.json());
app.set("trust proxy", 1);

app.get("/config.js", (req, res) => {
    res.type("application/javascript");
    res.send(`window.APP_CONFIG = { API_URL: "${API_URL}" };`);
});

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
    const response = await fetch(`${API_URL}/token`, {
        method: 'GET',
        headers: { 'Cookie': `token=${token}` }
    });
    if (!response.ok) {
        return res.redirect('/login');
    }
    res.sendFile(path.join(__dirname, "client/admin.html"));
});

app.get("/setup", async (req, res) => {
    const token = req.cookies.token;
    if (!token) {
        return res.redirect('/login');
    }
    const response = await fetch(`${API_URL}/token`, {
        method: 'GET',
        headers: { 'Cookie': `token=${token}` }
    });
    if (!response.ok) {
        return res.redirect('/login');
    }
    res.sendFile(path.join(__dirname, "client/setup.html"));
});

server.listen(port, () => console.log('Server running on port', port));
