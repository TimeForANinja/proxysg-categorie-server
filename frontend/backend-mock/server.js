import express from 'express';
import cors from 'cors';
import { JSONFilePreset  } from 'lowdb/node';
import addAuthRoutes from "./auth-server.js";
import addDataRoutes from "./data-server.js";

// init low db
let db;
JSONFilePreset('./user-db.json', {users: []}).then(x => {
    db = x;
})

// Initialize Express app
const app = express()

// Define a JWT secret key. This should be isolated by using env variables for security
const jwtSecretKey = 'dsfdsfsdfdsvcsvdfgefg'

// Set up CORS and JSON middlewares
app.use(cors())
app.use(express.json())
app.use(express.urlencoded({ extended: true }))


// endpoints
addAuthRoutes(app, jwtSecretKey);
addDataRoutes(app);

app.listen(3080)
