import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import {JSONFilePreset} from 'lowdb/node';

// init low db
let db;
JSONFilePreset('./user-db.json', {users: []}).then(x => {
    db = x;
})

const addAuthRoutes = (app, jwtSecretKey) => {
    // Basic home route for the API
    app.get('/', (_req, res) => {
        res.send('Auth API.\nPlease use POST /auth & POST /verify for authentication')
    })

    // The auth endpoint that creates a new user record or logs a user based on an existing record
    app.post('/auth', (req, res) => {
        const {username, password} = req.body

        // Look up the user entry in the database
        const user = db.data.users.filter((user) => username === user.username)

        // If found, compare the hashed passwords and generate the JWT token for the user
        if (user.length === 1) {
            bcrypt.compare(password, user[0].password, function (_err, result) {
                if (!result) {
                    return res.status(401).json({message: 'Invalid password or unknown user'})
                } else {
                    let loginData = {
                        username,
                        signInTime: Date.now(),
                    }

                    const token = jwt.sign(loginData, jwtSecretKey)
                    res.status(200).json({message: 'success', token})
                }
            })
        } else {
            /* old version that creates a new user
            createNewUserInDB(username, password, jwtSecretKey).then(token => {
                res.status(200).json({message: 'success', token})
            });
            */
            return res.status(401).json({message: 'Invalid password or unknown user'})
        }
    })

    // The verify endpoint that checks if a given JWT token is valid
    app.post('/verify', (req, res) => {
        const tokenHeaderKey = 'jwt-token'
        const authToken = req.headers[tokenHeaderKey]
        try {
            const verified = jwt.verify(authToken, jwtSecretKey)
            if (verified) {
                return res.status(200).json({status: 'logged in', message: 'success'})
            } else {
                // Access Denied
                return res.status(401).json({status: 'invalid auth', message: 'error'})
            }
        } catch (error) {
            // Access Denied
            return res.status(401).json({status: 'invalid auth', message: 'error'})
        }
    })
}

const createNewUserInDB = (username, password, jwtSecretKey) => new Promise(resolve => {
    // hash the given password and create a new entry in the auth db with the username and hashed password
    bcrypt.hash(password, 10, function (_err, hash) {
        console.log({username, password: hash})
        db.update(({users}) => users.push({username, password: hash}));

        let loginData = {
            username,
            signInTime: Date.now(),
        }

        const token = jwt.sign(loginData, jwtSecretKey)
        resolve(token);
    })
});

export default addAuthRoutes;
