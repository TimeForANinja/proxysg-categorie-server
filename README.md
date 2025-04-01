# Local Database Management for Broadcom Edge Secure Gateway (SGW)

This application is designed to manage "Local Databases" for **Broadcom Edge SGW**, as described in the official documentation: [About the Local Database](https://techdocs.broadcom.com/us/en/symantec-security-software/web-and-network-security/edge-swg/7-3/about-the-local-database.html).

The system provides a comprehensive solution utilizing a React-based frontend, a Python Flask backend, and a simple SQLite API.

---

## Project Structure

The application consists of the following main components:

1. **Frontend (React)**  
   Located in the `./frontend` directory, it provides a user-friendly interface for interacting with the local database.

2. **Backend (Flask API)**  
   Located in the `./backend` directory, it acts as the API server and manages critical logic for interacting with the database. It also includes an integrated SQLite-based API by default.

3. **SQLite Database**  
   By default, the backend uses SQLite for a lightweight, integrated database solution.

---

## Running the Application

### **Production Mode**
To run the application in production, you can choose between the two options:

1. **Using the Official Docker Image**  
   The production environment is preconfigured in the official Docker setup. Run the containerized app to deploy seamlessly.

   Example Code for this can be found in `./docker-compose.yml`

2. **Manual Build**  
   - Build the React-based frontend.  
   - Move the built files to the `./dist` folder located inside the backend directory.  
   - The backend serves the static frontend files along with the API.

---

### **Development Mode**
For development purposes, we recommend using the React proxy feature configured for this project.

- Run the **backend** Python Flask server on `localhost:8080`.
- Start the **frontend** React development server. The React server will proxy API requests to the backend.

This setup ensures a smooth development experience without manual rebuilding between changes to the frontend or backend.

---

## API Documentation

The API is **auto-generated** using **Swagger** and provides a detailed description of the available endpoints. The Swagger docs are hosted at:

```
/docs
```

You can explore the API directly in the browser using this URL.

---

## Additional Resources

For more detailed information about individual components, refer to the respective README files:

- **Backend Documentation**: `./backend/README.md`
- **Frontend Documentation**: `./frontend/README.md`

---

This app provides an efficient solution for managing Broadcom Edge SGW local databases and is tailored for both developers and production environments. Leverage the provided tools for easy setup and administration!
