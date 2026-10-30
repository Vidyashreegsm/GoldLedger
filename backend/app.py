import uuid
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import IntegrityError

from db import get_db_connection

app = Flask(__name__)
CORS(app)


# --------------------------------------------------
# COMMON HELPERS
# --------------------------------------------------

def get_connection():
    connection = get_db_connection()
    if connection is None:
        return None
    return connection


def error_response(message, status=400):
    return jsonify({"success": False, "error": message}), status


def valid_weight(value):
    try:
        number = Decimal(str(value))
        return number.is_finite() and number > 0
    except (InvalidOperation, TypeError, ValueError):
        return False


def valid_amount(value):
    try:
        number = Decimal(str(value))
        return number.is_finite() and number > 0
    except (InvalidOperation, TypeError, ValueError):
        return False


def valid_date(value):
    try:
        date.fromisoformat(str(value))
        return True
    except (TypeError, ValueError):
        return False


def fetch_all(query, values=()):
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, values)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# HOME AND HEALTH
# --------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to GoldLedger API!",
        "status": "running"
    })


@app.route("/api/health")
def health():
    connection = get_connection()

    if connection is None:
        return jsonify({
            "status": "error",
            "database": "disconnected"
        }), 500

    connection.close()

    return jsonify({
        "status": "success",
        "database": "connected",
        "app": "GoldLedger"
    })


# --------------------------------------------------
# KARIGARS
# --------------------------------------------------

@app.route("/api/karigars", methods=["GET"])
def get_karigars():
    rows = fetch_all(
        "SELECT * FROM karigars ORDER BY karigar_id DESC"
    )

    if rows is None:
        return error_response("Database connection failed", 500)

    return jsonify({
        "success": True,
        "count": len(rows),
        "karigars": rows
    })


@app.route("/api/karigars", methods=["POST"])
def add_karigar():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    joining_date = data.get("joining_date")

    if not name or not phone or not joining_date:
        return error_response(
            "Name, phone and joining date are required"
        )

    if not valid_date(joining_date):
        return error_response("Invalid joining date")

    connection = get_connection()
    if connection is None:
        return error_response("Database connection failed", 500)

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO karigars
            (name, phone, address, specialization, joining_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                name,
                phone,
                data.get("address"),
                data.get("specialization"),
                joining_date
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Karigar registered successfully",
            "karigar_id": cursor.lastrowid
        }), 201

    except IntegrityError:
        connection.rollback()
        return error_response(
            "This phone number is already registered", 409
        )
    except Exception:
        connection.rollback()
        app.logger.exception("Could not register karigar")
        return error_response("Could not register karigar", 500)
    finally:
        cursor.close()
        connection.close()


@app.route("/api/karigars/<int:karigar_id>", methods=["GET"])
def get_karigar(karigar_id):
    rows = fetch_all(
        "SELECT * FROM karigars WHERE karigar_id = %s",
        (karigar_id,)
    )

    if rows is None:
        return error_response("Database connection failed", 500)

    if not rows:
        return error_response("Karigar not found", 404)

    return jsonify({"success": True, "karigar": rows[0]})


@app.route("/api/karigars/<int:karigar_id>", methods=["PUT"])
def update_karigar(karigar_id):
    data = request.get_json(silent=True) or {}

    allowed = [
        "name", "phone", "address",
        "specialization", "joining_date", "status"
    ]

    updates = {key: data[key] for key in allowed if key in data}

    if not updates:
        return error_response("No valid fields provided")

    if "status" in updates and updates["status"] not in [
        "Active", "Inactive"
    ]:
        return error_response("Invalid status")

    if "name" in updates and not str(updates["name"]).strip():
        return error_response("Name cannot be empty")

    if "phone" in updates and not str(updates["phone"]).strip():
        return error_response("Phone cannot be empty")

    if "joining_date" in updates and not valid_date(
        updates["joining_date"]
    ):
        return error_response("Invalid joining date")

    connection = get_connection()
    if connection is None:
        return error_response("Database connection failed", 500)

    cursor = connection.cursor()

    try:
        fields = ", ".join(f"{key} = %s" for key in updates)
        values = list(updates.values()) + [karigar_id]

        cursor.execute(
            f"UPDATE karigars SET {fields} WHERE karigar_id = %s",
            tuple(values)
        )

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT karigar_id FROM karigars WHERE karigar_id = %s",
                (karigar_id,)
            )
            if cursor.fetchone() is None:
                return error_response("Karigar not found", 404)

        connection.commit()
        return jsonify({
            "success": True,
            "message": "Karigar updated successfully"
        })

    except IntegrityError:
        connection.rollback()
        return error_response(
            "This phone number is already registered", 409
        )
    except Exception:
        connection.rollback()
        app.logger.exception("Could not update karigar")
        return error_response("Could not update karigar", 500)
    finally:
        cursor.close()
        connection.close()


@app.route("/api/karigars/<int:karigar_id>", methods=["DELETE"])
def deactivate_karigar(karigar_id):
    connection = get_connection()
    if connection is None:
        return error_response("Database connection failed", 500)

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE karigars SET status = 'Inactive'
            WHERE karigar_id = %s
            """,
            (karigar_id,)
        )

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT karigar_id FROM karigars WHERE karigar_id = %s",
                (karigar_id,)
            )
            if cursor.fetchone() is None:
                return error_response("Karigar not found", 404)

        connection.commit()
        return jsonify({
            "success": True,
            "message": "Karigar deactivated successfully"
        })
    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# JOB ORDERS
# --------------------------------------------------

@app.route("/api/job-orders", methods=["GET"])
def get_job_orders():
    rows = fetch_all(
        """
        SELECT
            j.*,
            k.name AS karigar_name,
            k.phone AS karigar_phone,
            COALESCE(
                (SELECT SUM(g.gold_weight)
                 FROM gold_transactions g
                 WHERE g.job_order_id = j.job_order_id
                   AND g.transaction_type = 'ISSUED'), 0
            ) AS gold_issued,
            COALESCE(
                (SELECT SUM(g.gold_weight)
                 FROM gold_transactions g
                 WHERE g.job_order_id = j.job_order_id
                   AND g.transaction_type = 'RETURNED'), 0
            ) AS gold_returned,
            COALESCE(
                (SELECT SUM(g.gold_weight)
                 FROM gold_transactions g
                 WHERE g.job_order_id = j.job_order_id
                   AND g.transaction_type = 'WASTAGE'), 0
            ) AS wastage
        FROM job_orders j
        JOIN karigars k ON k.karigar_id = j.karigar_id
        ORDER BY j.job_order_id DESC
        """
    )

    if rows is None:
        return error_response("Database connection failed", 500)

    return jsonify({
        "success": True,
        "count": len(rows),
        "job_orders": rows
    })


@app.route("/api/job-orders", methods=["POST"])
def create_job_order():
    data = request.get_json(silent=True) or {}

    required = [
        "karigar_id", "jewellery_type",
        "gold_weight", "due_date"
    ]

    if any(data.get(key) in (None, "") for key in required):
        return error_response("Please fill all required job order fields")

    if not valid_weight(data["gold_weight"]):
        return error_response("Gold weight must be greater than zero")

    if not valid_date(data["due_date"]):
        return error_response("Invalid due date")

    try:
        karigar_id = int(data["karigar_id"])
    except (ValueError, TypeError):
        return error_response("Invalid karigar ID")

    connection = get_connection()
    if connection is None:
        return error_response("Database connection failed", 500)

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT karigar_id FROM karigars
            WHERE karigar_id = %s AND status = 'Active'
            """,
            (karigar_id,)
        )

        if cursor.fetchone() is None:
            return error_response("Active karigar not found", 404)

        cursor.execute(
            """
            INSERT INTO job_orders
            (order_number, karigar_id, jewellery_type,
             description, gold_weight, due_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                karigar_id,
                str(data["jewellery_type"]).strip(),
                data.get("description"),
                Decimal(str(data["gold_weight"])),
                data["due_date"]
            )
        )

        job_id = cursor.lastrowid
        order_number = f"GL-{date.today().year}-{job_id:04d}"

        cursor.execute(
            """
            UPDATE job_orders
            SET order_number = %s
            WHERE job_order_id = %s
            """,
            (order_number, job_id)
        )

        # Automatically record the gold issued for this job.
        cursor.execute(
            """
            INSERT INTO gold_transactions
            (job_order_id, karigar_id, transaction_type,
             gold_weight, notes, transaction_date)
            VALUES (%s, %s, 'ISSUED', %s, %s, %s)
            """,
            (
                job_id,
                karigar_id,
                Decimal(str(data["gold_weight"])),
                "Gold issued when job order was created",
                date.today()
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Job order created and gold issue recorded",
            "job_order_id": job_id,
            "order_number": order_number
        }), 201

    except Exception:
        connection.rollback()
        app.logger.exception("Could not create job order")
        return error_response("Could not create job order", 500)
    finally:
        cursor.close()
        connection.close()


@app.route("/api/job-orders/<int:job_id>", methods=["PUT"])
def update_job_order(job_id):
    data = request.get_json(silent=True) or {}

    allowed = ["jewellery_type", "description", "due_date", "status"]
    updates = {key: data[key] for key in allowed if key in data}

    if not updates:
        return error_response("No valid fields provided")

    if "due_date" in updates and not valid_date(updates["due_date"]):
        return error_response("Invalid due date")

    valid_statuses = [
        "Pending", "In Progress", "Completed",
        "Overdue", "Cancelled"
    ]

    if "status" in updates and updates["status"] not in valid_statuses:
        return error_response("Invalid job order status")

    connection = get_connection()
    if connection is None:
        return error_response("Database connection failed", 500)

    cursor = connection.cursor()

    try:
        fields = ", ".join(f"{key} = %s" for key in updates)
        values = list(updates.values()) + [job_id]

        cursor.execute(
            f"UPDATE job_orders SET {fields} WHERE job_order_id = %s",
            tuple(values)
        )

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT job_order_id FROM job_orders WHERE job_order_id = %s",
                (job_id,)
            )
            if cursor.fetchone() is None:
                return error_response("Job order not found", 404)

        connection.commit()
        return jsonify({
            "success": True,
            "message": "Job order updated successfully"
        })
    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# GOLD LEDGER
# --------------------------------------------------

@app.route("/api/gold-transactions", methods=["GET"])
def get_gold_transactions():
    rows = fetch_all(
        """
        SELECT
            g.*,
            j.order_number,
            j.jewellery_type,
            k.name AS karigar_name
        FROM gold_transactions g
        JOIN job_orders j ON j.job_order_id = g.job_order_id
        JOIN karigars k ON k.karigar_id = g.karigar_id
        ORDER BY g.transaction_id DESC
        """
    )

    if rows is None:
        return error_response("Database connection failed", 500)

    return jsonify({
        "success": True,
        "count": len(rows),
        "transactions": rows
    })


@app.route("/api/gold-transactions", methods=["POST"])
def add_gold_transaction():
    data = request.get_json(silent=True) or {}

    job_id = data.get("job_order_id")
    transaction_type = data.get("transaction_type")
    weight = data.get("gold_weight")

    if not job_id or not transaction_type or weight is None:
        return error_response("Job order, type and weight are required")

    if transaction_type not in ["RETURNED", "WASTAGE"]:
        return error_response(
            "Only RETURNED and WASTAGE entries can be added here"
        )

    if not valid_weight(weight):
        return error_response("Gold weight must be greater than zero")

    if transaction_type == "WASTAGE":
        return error_response(
            "Record wastage only after verifying the physical gold balance. "
            "This endpoint records a wastage entry; it does not replace "
            "a physical reconciliation."
        )

    connection = get_connection()
    if connection is None:
        return error_response("Database connection failed", 500)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                j.karigar_id,
                COALESCE(
                    (SELECT SUM(gold_weight) FROM gold_transactions
                     WHERE job_order_id = j.job_order_id
                       AND transaction_type = 'ISSUED'), 0
                ) AS issued,
                COALESCE(
                    (SELECT SUM(gold_weight) FROM gold_transactions
                     WHERE job_order_id = j.job_order_id
                       AND transaction_type = 'RETURNED'), 0
                ) AS returned,
                COALESCE(
                    (SELECT SUM(gold_weight) FROM gold_transactions
                     WHERE job_order_id = j.job_order_id
                       AND transaction_type = 'WASTAGE'), 0
                ) AS wastage
            FROM job_orders j
            WHERE j.job_order_id = %s
            """,
            (job_id,)
        )

        job = cursor.fetchone()

        if not job:
            return error_response("Job order not found", 404)

        remaining = (
            Decimal(str(job["issued"]))
            - Decimal(str(job["returned"]))
            - Decimal(str(job["wastage"]))
        )

        if Decimal(str(weight)) > remaining:
            return error_response(
                f"Return exceeds remaining gold balance ({remaining} g)"
            )

        cursor.execute(
            """
            INSERT INTO gold_transactions
            (job_order_id, karigar_id, transaction_type,
             gold_weight, notes, transaction_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                job_id,
                job["karigar_id"],
                transaction_type,
                Decimal(str(weight)),
                data.get("notes"),
                data.get("transaction_date") or date.today()
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Gold return recorded successfully",
            "transaction_id": cursor.lastrowid
        }), 201

    except Exception:
        connection.rollback()
        app.logger.exception("Could not record gold transaction")
        return error_response("Could not record gold transaction", 500)
    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# PAYMENTS
# --------------------------------------------------

@app.route("/api/payments", methods=["GET"])
def get_payments():
    rows = fetch_all(
        """
        SELECT
            p.*,
            j.order_number,
            j.jewellery_type,
            k.name AS karigar_name
        FROM payments p
        JOIN job_orders j ON j.job_order_id = p.job_order_id
        JOIN karigars k ON k.karigar_id = p.karigar_id
        ORDER BY p.payment_id DESC
        """
    )

    if rows is None:
        return error_response("Database connection failed", 500)

    return jsonify({
        "success": True,
        "count": len(rows),
        "payments": rows
    })


@app.route("/api/payments", methods=["POST"])
def add_payment():
    data = request.get_json(silent=True) or {}

    job_id = data.get("job_order_id")
    amount = data.get("amount")
    payment_date = data.get("payment_date")
    method = data.get("payment_method", "Cash")

    if not job_id or amount is None or not payment_date:
        return error_response("Job order, amount and date are required")

    if not valid_amount(amount):
        return error_response("Payment amount must be greater than zero")

    if not valid_date(payment_date):
        return error_response("Invalid payment date")

    methods = ["Cash", "UPI", "Bank Transfer", "Cheque", "Other"]
    if method not in methods:
        return error_response("Invalid payment method")

    connection = get_connection()
    if connection is None:
        return error_response("Database connection failed", 500)

    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT karigar_id FROM job_orders WHERE job_order_id = %s",
            (job_id,)
        )

        job = cursor.fetchone()

        if not job:
            return error_response("Job order not found", 404)

        cursor.execute(
            """
            INSERT INTO payments
            (job_order_id, karigar_id, amount, payment_method,
             payment_date, reference_number, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                job_id,
                job[0],
                Decimal(str(amount)),
                method,
                payment_date,
                data.get("reference_number"),
                data.get("notes")
            )
        )

        payment_id = cursor.lastrowid
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Payment recorded successfully",
            "payment_id": payment_id
        }), 201

    except Exception:
        connection.rollback()
        app.logger.exception("Could not record payment")
        return error_response("Could not record payment", 500)
    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/api/dashboard")
def dashboard():
    connection = get_connection()
    if connection is None:
        return error_response("Database connection failed", 500)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM karigars
                 WHERE status = 'Active') AS active_karigars,

                (SELECT COUNT(*) FROM job_orders
                 WHERE status IN ('Pending', 'In Progress')) AS pending_jobs,

                (SELECT COUNT(*) FROM job_orders
                 WHERE status != 'Completed'
                   AND status != 'Cancelled'
                   AND due_date < CURDATE()) AS overdue_jobs,

                (SELECT COALESCE(SUM(gold_weight), 0)
                 FROM gold_transactions
                 WHERE transaction_type = 'ISSUED') AS total_issued,

                (SELECT COALESCE(SUM(gold_weight), 0)
                 FROM gold_transactions
                 WHERE transaction_type = 'RETURNED') AS total_returned,

                (SELECT COALESCE(SUM(gold_weight), 0)
                 FROM gold_transactions
                 WHERE transaction_type = 'WASTAGE') AS total_wastage,

                (SELECT COALESCE(SUM(amount), 0)
                 FROM payments) AS total_payments
            """
        )

        stats = cursor.fetchone()

        issued = Decimal(str(stats["total_issued"]))
        returned = Decimal(str(stats["total_returned"]))
        wastage = Decimal(str(stats["total_wastage"]))

        stats["gold_with_karigars"] = issued - returned - wastage

        cursor.execute(
            """
            SELECT j.job_order_id, j.order_number,
                   j.jewellery_type, j.gold_weight,
                   j.due_date, j.status,
                   k.name AS karigar_name
            FROM job_orders j
            JOIN karigars k ON k.karigar_id = j.karigar_id
            ORDER BY j.job_order_id DESC
            LIMIT 5
            """
        )
        stats["recent_jobs"] = cursor.fetchall()

        cursor.execute(
            """
            SELECT g.transaction_type, g.gold_weight,
                   g.transaction_date, k.name AS karigar_name,
                   j.order_number
            FROM gold_transactions g
            JOIN karigars k ON k.karigar_id = g.karigar_id
            JOIN job_orders j ON j.job_order_id = g.job_order_id
            ORDER BY g.transaction_id DESC
            LIMIT 5
            """
        )
        stats["recent_gold_transactions"] = cursor.fetchall()

        return jsonify({"success": True, "dashboard": stats})

    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# REPORTS
# --------------------------------------------------

@app.route("/api/reports")
def reports():
    connection = get_connection()
    if connection is None:
        return error_response("Database connection failed", 500)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                k.karigar_id,
                k.name AS karigar_name,
                k.phone,
                COALESCE(SUM(
                    CASE WHEN g.transaction_type = 'ISSUED'
                         THEN g.gold_weight ELSE 0 END
                ), 0) AS gold_issued,
                COALESCE(SUM(
                    CASE WHEN g.transaction_type = 'RETURNED'
                         THEN g.gold_weight ELSE 0 END
                ), 0) AS gold_returned,
                COALESCE(SUM(
                    CASE WHEN g.transaction_type = 'WASTAGE'
                         THEN g.gold_weight ELSE 0 END
                ), 0) AS wastage
            FROM karigars k
            LEFT JOIN gold_transactions g
                ON g.karigar_id = k.karigar_id
            GROUP BY k.karigar_id, k.name, k.phone
            ORDER BY k.name
            """
        )

        karigar_report = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_payments,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM payments
            """
        )
        payment_summary = cursor.fetchone()

        return jsonify({
            "success": True,
            "karigar_report": karigar_report,
            "payment_summary": payment_summary
        })

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
