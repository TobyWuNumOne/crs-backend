# Develop the following CRUD backend app with the following specs

```json
Package manager: uv
Database: PostgresDB
Backend: FastAPI
Authentication: jwt tokens

You may write mock frontend code to test your app, but we only review the API docs and its functionailty.

```

Let’s develop a clinic registration system.

1. Users: Doctors, Patients
    1. For each user we record first name, last name, sex, birthdate, role.
2. Clinics:
    1. For each clinic we record: doctor ID, date, time slot(上午下午夜診)
3. Registrations:
    1. For each registration we record: clinic ID, patient, status, registered_at, cancelled_at.

If you feel that you need more columns, feel free to add them.

Please develop at least these APIs:

1. Registration for doctors and patients (Free registration for this project.)
2. A doctor can:

    Add a clinic. Delete a clinic.

    Register a patient for a clinic.

    Check all patients for his/her clinic on a given day.

3. A patient can:

    Register for a clinic.

    Check his/her registered clinic.

    A patient can not register other patients for a clinic.

4. Provide statistics:

    How many doctors and patients?

    How many clinics for a given day?

The app should be functional/usable. It’s OK if you have bugs, but it’s not OK if it doesn’t work.

Please do this on your local machine. I’ll get a remote PostgresDB for you later.
