`Introduction`    

This project is a comprehensive full-stack web application template designed to streamline the development process for modern web applications. It combines a robust backend built with Python and FastAPI, and a dynamic frontend powered by Next.js and React. This template is structured to support multiple environments (local, development, UAT, staging, and production) and includes a suite of tools for efficient development, testing, and deployment.

`Core Technologies`

`Backend`
- Python
- FastAPI
- PostgreSQL
- Alembic (for database migrations)
- SQLAlchemy (ORM)
- Dynaconf (for configuration management)

`Frontend`
- Next.js 14+
- TypeScript
- Tailwind CSS
- Shadcn/ui (for UI components)
- Framer Motion (for animations)
- React Query (TanStack Query for data fetching)
- React Context API (for state management)

`Project Structure`
The project is organized into two main sections: backend and frontend.

`Backend Structure`             | `Explanation`
  - app/                        | Contains the main application code
    - models/                   | Defines database table structures
    - routers/                  | Specifies API endpoints and their handlers
    - schemas/                  | Defines data models for request/response validation
    - services/                 | Implements core business logic and data processing
    - utils/                    | Houses helper functions and common utilities
  - alembic/                    | Manages database schema changes over time
  - config/                     | Stores environment-specific settings
  - tests/                      | Contains unit and integration tests for backend

`Frontend Structure`            | `Explanation`
  - frontend/                   | Root directory for frontend application
    - public/                   | Stores publicly accessible static files
    - src/                      | Source code directory
      - app/                    | Implements Next.js 14+ app router and pages
      - components/             | Houses modular and reusable UI components
      - hooks/                  | Contains custom hooks for shared logic
      - lib/                    | Provides utility functions and API integration
      - styles/                 | Manages global styles and Tailwind CSS setup
      - types/                  | Defines TypeScript types and interfaces
      - context/                | Implements state management using Context API


`Key Features`

1. Multi-Environment Support: 
    - Configured for local, development, UAT, staging, and production environments.

2. Automated Setup Scripts: 
   - `lcl_prep_env.py`: Prepares the local environment
   - `lcl_provision_env.py`: Provisions the local environment

3. Dependency Management:
   - Scripts for installing, updating, and uninstalling dependencies
   - Automatic updating of `requirements.txt` and `package.json`

4. Database Management:
   - Scripts for creating, connecting, and dropping databases
   - Alembic integration for database migrations

5. Backup System:
   - Automated and manual backup creation
   - Backup restoration, deletion, and viewing capabilities

6. Update Scripts:
   - Updating API specifications, database schema, project tree, and tech stack

7. Development Tools:
   - Scripts for starting backend and frontend servers
   - CRUD operation testing

8. Documentation:
   - Automated generation of API specs, database schema, and project tree

*Getting Started*

`Automated Setup`
    Run the following commands to set up the project:
    `python scripts/devops/lcl_prep_env.py`
    `python scripts/devops/lcl_provision_env.py`

`Manual Setup`
    If automated setup fails, follow the instructions in `workspace/instructions/setup_local_instructions.md`.

`Starting the Application`
    - Backend: `python scripts/start/start_backend.py`
    - Frontend: `python scripts/start/start_frontend.py`

`Development Workflow`
- Use provided scripts for database management, backups, and updates
- Regularly update the tech stack and project documentation

`Best Practices`
    1. **Version Control**: Commit changes regularly and use meaningful commit messages.
    2. **Testing**: Write and run tests for both backend and frontend code.
    3. **Documentation**: Keep the API specs and project documentation up-to-date.
    4. **Backups**: Regularly create backups, especially before major changes.
    5. **Code Style**: Follow PEP 8 for Python and use ESLint/Prettier for JavaScript/TypeScript.

`Conclusion`
This template provides a solid foundation for building scalable and maintainable web applications. It combines best practices in full-stack development with a suite of tools to enhance productivity and code quality. Whether you're building a small project or a large-scale application, this template offers the flexibility and robustness to meet your development needs.

*Setup Notes*

**Note:** Ensure to run the following setups (MinIO, Redis, and Ngrok) before starting the backend application.


`MinIO DB Setup`
  1. Install MinIO by running the following command:
     ```bash
     wget https://dl.min.io/server/minio/release/linux-amd64/minio
     chmod +x minio
     sudo mv minio /usr/local/bin/
     ```
  2. Create a directory for MinIO data:
     ```bash
     mkdir ~/minio-data
     ```
  3. Start MinIO server with the following command:
     ```bash
     minio server ~/minio-data --console-address ":9001"
     ```
  4. Access MinIO at `http://localhost:9000` using the following credentials:
     - **Access Key**: `minioadmin`
     - **Secret Key**: `minioadmin`
  5. Ensure that MinIO is running on `localhost:9000` (default).

`Redis Setup on Ubuntu`
  1. Update your package list:
     ```bash
     sudo apt update
     ```
  2. Install Redis server:
     ```bash
     sudo apt install redis-server
     ```
  3. After installation, configure Redis to start on boot:
     ```bash
     sudo systemctl enable redis-server
     ```
  4. Start the Redis service:
     ```bash
     sudo systemctl start redis-server
     ```
  5. If prompted, restart your computer to ensure Redis starts correctly.
  6. Verify that Redis is running:
     ```bash
     redis-cli ping
     ```
     You should receive a response of `PONG`.

`Ngrok Setup`
  1. In a separate terminal, run Ngrok to expose your local server:
     ```bash
     ngrok http 9000
     ```
  2. Copy the generated Ngrok URL.
  3. Update the URL in your Google Cloud email bot project's subscription settings to point to the Ngrok URL.