const express = require("express");
const app = express ();
const http = require("http");
const path = require("path");
const server = http.createServer(app);

const port = process.env.PORT || 8080;

app.use(express.static("./client"));

app.use(express.json());

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "client/index.html"));
});

server.listen(port, () => console.log('Server running on port', port));

