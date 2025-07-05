from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="12012005",  
        database="genai"
    )

@app.route("/")
def home():
    return render_template("index.html") 

@app.route("/add_patient", methods=["POST"])
def add_patient():
    try:
        conn = get_connection()
        cur = conn.cursor()

        Name = request.form["Name"]
        Age = request.form["Age"]
        Gender = request.form["Gender"]
        Department = request.form["Department"]
        AdmissionDate = request.form["AdmissionDate"]
        Diagnosis = request.form["Diagnosis"]

        cur.execute("""
            INSERT INTO modified_hospital_data 
            (Name, Age, Gender, Department, AdmissionDate, Diagnosis)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (Name, Age, Gender, Department, AdmissionDate , Diagnosis))

        conn.commit()
    except Exception as e:
        print("Error in add_patient:", e)
    finally:
        cur.close()
        conn.close()
    return redirect("/")

@app.route("/delete_patient", methods=["POST"])
def delete_patient():
    try:
        conn = get_connection()
        cur = conn.cursor()

        PatientID = request.form["PatientID"]

        # Step 1: Check if patient exists
        cur.execute("""
            SELECT Name, AdmissionDate, Diagnosis
            FROM modified_hospital_data
            WHERE PatientID = %s
        """, (PatientID,))
        patient = cur.fetchone()

        if patient:
            Name, AdmissionDate, Diagnosis = patient

            # Step 2: Insert into discharged_patients
            cur.execute("""
                INSERT INTO discharged_patients (Name, AdmissionDate, Diagnosis)
                VALUES (%s, %s, %s)
            """, (Name, AdmissionDate, Diagnosis))

            # Step 3: Delete from modified_hospital_data
            cur.execute("""
                DELETE FROM modified_hospital_data
                WHERE PatientID = %s
            """, (PatientID,))

            conn.commit()
        else:
            return render_template("patient_not_found.html"), 404

    except Exception as e:
        print("Error in delete_patient:", e)
        return "Internal Server Error", 500

    finally:
        cur.close()
        conn.close()

    return redirect("/")





@app.route("/update_patient", methods=["POST"])
def update_patient():
    try:
        conn = get_connection()
        cur = conn.cursor()

        PatientID = request.form["PatientID"]
        Name = request.form.get("Name")
        Age = request.form.get("Age")
        Gender = request.form.get("Gender")
        Department = request.form.get("Department")
        Diagnosis = request.form.get("Diagnosis")

        # Step 1: Check if patient exists
        cur.execute("SELECT COUNT(*) FROM modified_hospital_data WHERE PatientID = %s", (PatientID,))
        exists = cur.fetchone()[0]

        if not exists:
            return render_template("patient_not_found.html"), 404

        # Step 2: Prepare fields to update
        update_fields = []
        values = []

        if Name:
            update_fields.append("Name = %s")
            values.append(Name)
        if Age:
            update_fields.append("Age = %s")
            values.append(Age)
        if Gender:
            update_fields.append("Gender = %s")
            values.append(Gender)
        if Department:
            update_fields.append("Department = %s")
            values.append(Department)
        if Diagnosis:
            update_fields.append("Diagnosis = %s")
            values.append(Diagnosis)

        # Step 3: Run update if fields present
        if update_fields:
            query = f"""
                UPDATE modified_hospital_data
                SET {', '.join(update_fields)}
                WHERE PatientID = %s
            """
            values.append(PatientID)
            cur.execute(query, tuple(values))
            conn.commit()

    except Exception as e:
        print("Error in update_patient:", e)
        return "Internal Server Error", 500
    finally:
        cur.close()
        conn.close()

    return redirect("/")

@app.route("/view_patients")
def view_patients():
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Fetch all patient records
        cur.execute("SELECT * FROM modified_hospital_data")
        patients = cur.fetchall()

    except Exception as e:
        print("Error fetching patients:", e)
        patients = []

    finally:
        cur.close()
        conn.close()

    return render_template("view_patients.html", patients=patients)

@app.route("/view_discharged")
def view_discharged():
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Fetch discharged patient records
        cur.execute("SELECT * FROM discharged_patients")
        discharged = cur.fetchall()

    except Exception as e:
        print("Error fetching discharged patients:", e)
        discharged = []

    finally:
        cur.close()
        conn.close()

    return render_template("view_discharged.html", discharged=discharged)



if __name__ == "__main__":
    app.run(debug=True, port=5001)
