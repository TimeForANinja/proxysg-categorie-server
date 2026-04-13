# ProxySG Category Server Frontend

This is the frontend for the ProxySG Category Server, built with React, TypeScript, and Vite.

## Available Scripts

In the project directory, you can run:

### `npm run dev` or `npm start`

Runs the app in the development mode using Vite.  
Open [http://localhost:5173](http://localhost:5173) to view it in the browser.

The page will reload if you make edits.

### `npm run build`

Builds the app for production to the `build` folder.  
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified, and the filenames include the hashes.

### `npm run preview`

Locally preview the production build.

### `npm test`

Launches the test runner. (Note: Currently configured as a placeholder).

## Project Structure

The project follows a standard React/Vite structure:

- `src/api/`: Contains API implementation functions for all routes defined in the OpenAPI documentation.
- `src/components/`: React components for the application, including pages (History, Categories, URLs, Tokens) and shared UI elements.
- `src/hooks/`: Custom React hooks for managing state and side effects (e.g., branch selection, query parameters).
- `src/types/`: TypeScript type definitions and interfaces matching the backend API schemas.
- `src/util/`: General utility functions (e.g., date formatting).
- `src/index.tsx`: The entry point for the React application.
- `vite.config.ts`: Configuration for Vite, including proxy settings and plugin setup.
- `index.html`: The main HTML file (Vite's entry point).
- `public/`: Static assets like icons and images.
