# 🚀 Fly.io Deployment Guide (Client Account)

Follow these simple steps to deploy the PDF Manager and its persistent PostgreSQL database onto a new Fly.io account.

## Prerequisites
1.  **Fly.io Account**: Ensure the client has an account.
2.  **Flyctl Installed**: Install the Fly CLI on your machine.
3.  **Login**: Run `fly auth login` to authenticate with the client's account.

---

## Part 1: Deploy the Database (PostgreSQL)

We use a custom PostgreSQL setup to ensure data persistence and control.

1.  **Enter the database directory**:
    ```bash
    cd postgres_db
    ```

2.  **Create the Database App**:
    *(Replace `my-unique-db-name` with a unique name)*
    ```bash
    fly apps create my-unique-db-name --machines --org personal
    ```

3.  **Update the app name in `fly.toml`**:
    Open `postgres_db/fly.toml` and change `app = "..."` to your new unique name.

4.  **Create Persistent Storage**:
    ```bash
    fly volumes create pg_data --region bom --size 1 --app my-unique-db-name --yes
    ```

5.  **Set Database Password**:
    ```bash
    fly secrets set POSTGRES_PASSWORD=your_secure_password --app my-unique-db-name
    ```

6.  **Deploy the Database**:
    ```bash
    fly deploy --image postgres:alpine --yes --remote-only
    ```

---

## Part 2: Deploy the Application

1.  **Go back to the root directory**:
    ```bash
    cd ..
    ```

2.  **Create the Main App**:
    *(Replace `my-pdf-manager-name` with a unique name)*
    ```bash
    fly apps create my-pdf-manager-name --machines --org personal
    ```

3.  **Update the app name in `fly.toml`**:
    Open the root `fly.toml` and change `app = "..."` to your new unique name.

4.  **Connect to the Database**:
    Construct your `DATABASE_URL` using the database app name and password from Part 1:
    `postgresql://rachit:your_secure_password@my-unique-db-name.flycast:5432/pdf_manager`

    ```bash
    fly secrets set DATABASE_URL=postgresql://rachit:your_secure_password@my-unique-db-name.flycast:5432/pdf_manager
    ```

5.  **Set Security Keys**:
    ```bash
    fly secrets set SECRET_KEY=generate_a_random_string JWT_SECRET_KEY=generate_another_random_string
    ```

6.  **Deploy the Application**:
    ```bash
    fly deploy --remote-only
    ```

---

## Part 3: Access & Verification

1.  **Open the app**:
    ```bash
    fly apps open
    ```

2.  **Initial Login**:
    *   **User**: `rachitbishnoi16@gmail.com`
    *   **Password**: `tircha@12345`

3.  **Persistence Test**:
    Upload a document, then run `fly apps restart`. The document will **still be there** because it is now stored in PostgreSQL.

---

### ⚠️ Important Note
Always ensure both the **Database App** and the **Main App** are in the **same region** (e.g., `bom` for Mumbai) for the fastest performance and reliable internal networking.
