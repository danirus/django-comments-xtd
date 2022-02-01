const path = require("path");
const express = require("express");
const app = express();
const port = 3000;

const PRJ_PATH = path.resolve(
    __dirname, '..', 'django_comments_xtd', 'static', 'django_comments_xtd'
);

app.use(express.static(PRJ_PATH));

app.get('/', (req, res) => {
    res.send("Serve static resources for jest tests.");
});

app.listen(port, () => {});
