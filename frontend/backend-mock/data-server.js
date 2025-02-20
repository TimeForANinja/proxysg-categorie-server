const DATA = {
    categories: [
        {id: 0, name: 'Alphabet', color: 1, description: 'Google Services'},
        {id: 1, name: 'Social Media', color: 2, description: 'Name says it all'},
        {id: 2, name: 'Meta', color: 3, description: 'aka Facebook'},
        {id: 3, name: 'Video Content', color: 4, description: ''},
        {id: 4, name: 'Audio Content', color: 5, description: ''},
    ],
    urls: [
        {id: 0, hostname: 'google.com', categories: [0, 1, 3]},
        {id: 1, hostname: 'youtube.com', categories: [0, 3]},
        {id: 2, hostname: 'gmail.com', categories: [0,1]},
        {id: 3, hostname: 'facebook.com', categories: [2]},
        ...new Array(500).fill(0).map((_, idx) => ({ id: idx + 100, hostname: idx+'.cdn.test.com', categories: []})),],
    apiTokens: [
        { id: 0, token: "aaaa", categories: [1, 2, 3], description: "Side level", lastUse: "2024-10-02"},
        { id: 1, token: "bbbb", categories: [1, 2], description: "INet", lastUse: "2024-10-02"},
        { id: 2, token: "cccc", categories: [3], description: "Shared 2 DIV", lastUse: "2024-10-02"},
        { id: 3, token: "dddd", categories: [], description: "None", lastUse: "2024-10-02"},
    ],
    history: [
        { id: 2, time: 3e5, name: "third commit", atomics: [
                {id: 6, action: "add-category", data: 5},
                {id: 7, action: "del-category", data: 5},
                {id: 8, action: "add-category", data: 3},
            ]},
        { id: 1, time: 2e5, name: "second commit", atomics: [
                {id: 5, action: "add-category", data: 4},
            ]},
        { id: 0, time: 1e5, name: "first commit", atomics: []},
    ],
}

const addDataRoutes = (app) => {
    app.get('/api/categories', (_req, res) => {
        res.status(200).json({
            message: 'success',
            data: DATA.categories,
        })
    })

    app.get('/api/urls', (_req, res) => {
        res.status(200).json({
            message: 'success',
            data: DATA.urls,
        })
    })

    app.get('/api/api-tokens', (_req, res) => {
        res.status(200).json({
            message: 'success',
            data: DATA.apiTokens,
        })
    })

    app.get('/api/history/:id', (_req, res) => {
        res.status(200).json({
            message: 'success',
            data: DATA.history,
        })
    })
}

export default addDataRoutes;
