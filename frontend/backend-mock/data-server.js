import { JSONFilePreset  } from 'lowdb/node';

// init low db
let db;
JSONFilePreset('./user-db.json', {users: []}).then(x => {
    db = x;
})

const addDataRoutes = (app) => {
    app.get('/api/categories', (_req, res) => {
        res.status(200).json({
            message: 'success',
            data: [
                {id: 0, name: 'Alphabet', color: 1},
                {id: 1, name: 'Social Media', color: 2},
                {id: 2, name: 'Meta', color: 3},
                {id: 3, name: 'Video Content', color: 4},
                {id: 4, name: 'Audio Content', color: 5},
            ]
        })
    })

    app.get('/api/urls', (_req, res) => {
        res.status(200).json({
            message: 'success',
            data: [
                {id: 0, hostname: 'google.com', categories: [0, 1, 3]},
                {id: 1, hostname: 'youtube.com', categories: [0, 3]},
                {id: 2, hostname: 'gmail.com', categories: [0,1]},
                {id: 3, hostname: 'facebook.com', categories: [2]},
            ]
        })
    })

    app.get('/api/api-tokens', (_req, res) => {
        res.status(200).json({
            message: 'success',
            data: [
                { id: 0, token: "aaaa", categories: [1, 2, 3]},
                { id: 1, token: "bbbb", categories: [1, 2]},
                { id: 2, token: "cccc", categories: [3]},
                { id: 3, token: "dddd", categories: []},
            ]
        })
    })

    app.get('/api/history/:id', (_req, res) => {
        res.status(200).json({
            message: 'success',
            data: [
                { id: 0, time: 1e5, name: "first commit", atomics: [
                        {id: 4, action: "create"},
                ]},
                { id: 1, time: 2e5, name: "second commit", atomics: [
                        {id: 5, action: "add-category", data: 4},
                ]},
                { id: 2, time: 3e5, name: "third commit", atomics: [
                        {id: 6, action: "add-category", data: 5},
                        {id: 7, action: "del-category", data: 5},
                        {id: 8, action: "add-category", data: 3},
                ]},
            ]
        })
    })
}

export default addDataRoutes;
