# Event Management API

This is a complete backend solution for an Event Management system built with **FastAPI** and **SQLModel**, successfully implementing all core and bonus requirements of the Python Backend Developer Assessment.

## Architectural Overview
* **Database**: SQLite (managed by SQLModel)
* **Core Logic**: Implemented using **SQLModel** for concise and type-safe database interaction.
* **Access Control**: **JWT** for authentication and **RBAC** (Role-Based Access Control) enforced via Dependencies.
* **Caching/Limiting**: **Redis** is used as the backend for the Rate Limiting feature.

## Implemented Features

| Feature | Status | Details |
| :--- | :--- | :--- |
| **User Auth & Roles** | ✅ Complete | JWT signup/login. First user registered is automatically assigned **Admin** role. |
| **Event Management CRUD** | ✅ Complete | Create, Read (Search/Filter/Paginate), Update, Delete events. |
| **Role-Based Access Control** | ✅ Complete | Users manage only their own events. Admin can view **all** events and update **any** event's status. |
| **Search & Filtering** | ✅ Complete | Events can be filtered by `title`, `status`, and `start_date`/`end_date`. |
| **Pagination** | ✅ Complete | Event listings are paginated (`page` and `limit` parameters). |
| **Task Management** | ✅ Bonus | Full CRUD for tasks, with strict ownership logic enforced based on the parent event owner. |
| **Rate Limiting** | ✅ Bonus | Configured for 100 requests/hour using `fastapi-limiter`. |

## Setup and Running the Project

### Prerequisites
* Python 3.10+
* **Redis Server**: Required to run the Rate Limiting feature. You must have a Redis instance running locally (default: `redis://localhost:6379`).

### Installation

1.  **Clone the Repository (If applicable):**
    ```bash
    git clone [https://github.com/elbewhy/](https://github.com/elbewhy/)<your-repo-name>.git
    cd <your-repo-name>
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate  # Linux/macOS
    ```

3.  **Install Dependencies:**
    ```bash
    pip install fastapi uvicorn[standard] sqlmodel python-jose[cryptography] passlib[bcrypt] pydantic-settings fastapi-limiter redis pytest
    ```

### Run the Server
Ensure your local Redis server is running before executing:

```bash
uvicorn app.main:app --reload