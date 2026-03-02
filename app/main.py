from fastapi import FastAPI
from sqlalchemy import text
from app.database import SessionLocal
from pydantic import BaseModel

app = FastAPI()


class StartEvent(BaseModel):
    user_id: str
    funnel_name: str
    step_name: str
    channel: str

class FunnelCreate(BaseModel):
    funnel_name: str
    description: str | None = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-test")
def db_test():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {"db_status": "connected", "result": result}
    finally:
        db.close()


@app.post("/events/start")
def create_start_event(event: StartEvent):
    db = SessionLocal()
    try:
        insert_query = text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'start', :channel)
            RETURNING id;
        """)

        new_id = db.execute(insert_query, {
            "user_id": event.user_id,
            "funnel_name": event.funnel_name,
            "step_name": event.step_name,
            "channel": event.channel
        }).scalar()

        db.commit()

        return {"message": "event saved", "event_id": new_id}
    finally:
        db.close()

@app.post("/events/step")
def create_step_event(event: StartEvent):
    db = SessionLocal()
    try:
        insert_query = text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'step', :channel)
            RETURNING id;
        """)

        new_id = db.execute(insert_query, {
            "user_id": event.user_id,
            "funnel_name": event.funnel_name,
            "step_name": event.step_name,
            "channel": event.channel
        }).scalar()

        db.commit()

        return {"message": "step event saved", "event_id": new_id}
    finally:
        db.close()

@app.post("/events/complete")
def create_complete_event(event: StartEvent):
    db = SessionLocal()
    try:
        insert_query = text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'complete', :channel)
            RETURNING id;
        """)

        new_id = db.execute(insert_query, {
            "user_id": event.user_id,
            "funnel_name": event.funnel_name,
            "step_name": event.step_name,
            "channel": event.channel
        }).scalar()

        db.commit()

        return {"message": "complete event saved", "event_id": new_id}
    finally:
        db.close()

@app.post("/events/abandon")
def create_abandon_event(event: StartEvent):
    db = SessionLocal()
    try:
        insert_query = text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'abandon', :channel)
            RETURNING id;
        """)

        new_id = db.execute(insert_query, {
            "user_id": event.user_id,
            "funnel_name": event.funnel_name,
            "step_name": event.step_name,
            "channel": event.channel
        }).scalar()

        db.commit()

        return {"message": "abandon event saved", "event_id": new_id}
    finally:
        db.close()


@app.post("/funnels")
def create_funnel(funnel: FunnelCreate):
    db = SessionLocal()
    try:
        insert_query = text("""
            INSERT INTO funnels (funnel_name, description)
            VALUES (:funnel_name, :description)
            RETURNING id, funnel_name, description, created_at;
        """)

        result = db.execute(insert_query, {
            "funnel_name": funnel.funnel_name,
            "description": funnel.description
        }).mappings().first()

        db.commit()

        return dict(result)
    finally:
        db.close()


@app.get("/funnels")
def get_funnels():
    db = SessionLocal()
    try:
        query = text("""
            SELECT id, funnel_name, description, created_at
            FROM funnels
            ORDER BY id DESC;
        """)
        result = db.execute(query).mappings().all()
        return {"funnels": [dict(row) for row in result]}
    finally:
        db.close()


@app.get("/funnels/{funnel_id}")
def get_funnel_by_id(funnel_id: int):
    db = SessionLocal()
    try:
        funnel_query = text("""
            SELECT id, funnel_name, description, created_at
            FROM funnels
            WHERE id = :funnel_id;
        """)
        funnel = db.execute(funnel_query, {"funnel_id": funnel_id}).mappings().first()

        if not funnel:
            return {"error": "Funnel not found"}

        steps_query = text("""
            SELECT id, step_name, step_order, created_at
            FROM funnel_steps
            WHERE funnel_id = :funnel_id
            ORDER BY step_order;
        """)
        steps = db.execute(steps_query, {"funnel_id": funnel_id}).mappings().all()

        return {
            "funnel": dict(funnel),
            "steps": [dict(s) for s in steps]
        }
    finally:
        db.close()

@app.get("/analytics/funnel/{funnel_id}/steps")
def funnel_step_report(funnel_id: int):
    db = SessionLocal()
    try:
        # 1) Get funnel name from funnel_id
        funnel_query = text("""
            SELECT funnel_name
            FROM funnels
            WHERE id = :funnel_id;
        """)
        funnel = db.execute(funnel_query, {"funnel_id": funnel_id}).mappings().first()

        if not funnel:
            return {"error": "Funnel not found"}

        funnel_name = funnel["funnel_name"]

        # 2) Step analytics using funnel_steps as the source of truth
        report_query = text("""
            WITH step_users AS (
                SELECT
                    fs.step_order,
                    fs.step_name,
                    COUNT(DISTINCT e.user_id) AS users_at_step
                FROM funnel_steps fs
                LEFT JOIN events e
                    ON e.funnel_name = (SELECT funnel_name FROM funnels WHERE id = :funnel_id)
                   AND e.step_name = fs.step_name
                WHERE fs.funnel_id = :funnel_id
                GROUP BY fs.step_order, fs.step_name
            )
            SELECT
                step_order,
                step_name,
                users_at_step,
                LAG(users_at_step) OVER (ORDER BY step_order) AS users_previous_step,

                CASE
                    WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                    ELSE (LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step)
                END AS drop_off_users,

                CASE
                    WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                    WHEN LAG(users_at_step) OVER (ORDER BY step_order) = 0 THEN NULL
                    ELSE ROUND(
                        ((LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step)::numeric
                        / LAG(users_at_step) OVER (ORDER BY step_order)) * 100,
                        2
                    )
                END AS drop_off_percentage,

                CASE
                    WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                    WHEN LAG(users_at_step) OVER (ORDER BY step_order) = 0 THEN NULL
                    ELSE ROUND((users_at_step::numeric / LAG(users_at_step) OVER (ORDER BY step_order)) * 100, 2)
                END AS conversion_rate_percentage

            FROM step_users
            ORDER BY step_order;
        """)


        rows = db.execute(report_query, {"funnel_id": funnel_id}).mappings().all()

        return {
            "funnel_id": funnel_id,
            "funnel_name": funnel_name,
            "steps": [dict(r) for r in rows]
        }

    finally:
        db.close()

@app.get("/analytics/funnel/{funnel_id}/summary")
def funnel_summary(funnel_id: int):
    db = SessionLocal()
    try:
        # Get funnel name
        funnel_query = text("""
            SELECT funnel_name
            FROM funnels
            WHERE id = :funnel_id;
        """)
        funnel = db.execute(funnel_query, {"funnel_id": funnel_id}).mappings().first()

        if not funnel:
            return {"error": "Funnel not found"}

        funnel_name = funnel["funnel_name"]

        # Total started
        started_query = text("""
            SELECT COUNT(DISTINCT user_id) AS total_started
            FROM events
            WHERE funnel_name = :funnel_name
              AND event_type = 'start';
        """)
        total_started = db.execute(started_query, {"funnel_name": funnel_name}).scalar() or 0

        # Total completed
        completed_query = text("""
            SELECT COUNT(DISTINCT user_id) AS total_completed
            FROM events
            WHERE funnel_name = :funnel_name
              AND event_type = 'complete';
        """)
        total_completed = db.execute(completed_query, {"funnel_name": funnel_name}).scalar() or 0

        # Overall conversion rate
        overall_conversion = None
        if total_started > 0:
            overall_conversion = round((total_completed / total_started) * 100, 2)

        # Biggest drop-off step (using step analytics)
        biggest_drop_query = text("""
            WITH step_users AS (
                SELECT
                    fs.step_order,
                    fs.step_name,
                    COUNT(DISTINCT e.user_id) AS users_at_step
                FROM funnel_steps fs
                LEFT JOIN events e
                    ON e.funnel_name = :funnel_name
                   AND e.step_name = fs.step_name
                WHERE fs.funnel_id = :funnel_id
                GROUP BY fs.step_order, fs.step_name
            ),
            step_metrics AS (
                SELECT
                    step_order,
                    step_name,
                    users_at_step,
                    LAG(users_at_step) OVER (ORDER BY step_order) AS users_previous_step,
                    CASE
                        WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                        ELSE (LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step)
                    END AS drop_off_users,
                    CASE
                        WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                        WHEN LAG(users_at_step) OVER (ORDER BY step_order) = 0 THEN NULL
                        ELSE ROUND(
                            ((LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step)::numeric
                            / LAG(users_at_step) OVER (ORDER BY step_order)) * 100,
                            2
                        )
                    END AS drop_off_percentage
                FROM step_users
            )
            SELECT step_order, step_name, drop_off_users, drop_off_percentage
            FROM step_metrics
            WHERE drop_off_percentage IS NOT NULL
            ORDER BY drop_off_percentage DESC
            LIMIT 1;
        """)

        biggest_drop = db.execute(biggest_drop_query, {
            "funnel_id": funnel_id,
            "funnel_name": funnel_name
        }).mappings().first()

        return {
            "funnel_id": funnel_id,
            "funnel_name": funnel_name,
            "total_started": total_started,
            "total_completed": total_completed,
            "overall_conversion_percentage": overall_conversion,
            "biggest_drop_off_step": dict(biggest_drop) if biggest_drop else None
        }

    finally:
        db.close()
@app.get("/analytics/funnel/{funnel_id}/time")
def funnel_time_analysis(funnel_id: int):
    db = SessionLocal()
    try:
        # Get funnel name
        funnel_query = text("""
            SELECT funnel_name
            FROM funnels
            WHERE id = :funnel_id;
        """)
        funnel = db.execute(funnel_query, {"funnel_id": funnel_id}).mappings().first()

        if not funnel:
            return {"error": "Funnel not found"}

        funnel_name = funnel["funnel_name"]

        # Time between steps (based on first time user hit each step)
        time_query = text("""
            WITH ordered_steps AS (
                SELECT
                    step_order,
                    step_name,
                    LEAD(step_name) OVER (ORDER BY step_order) AS next_step_name,
                    LEAD(step_order) OVER (ORDER BY step_order) AS next_step_order
                FROM funnel_steps
                WHERE funnel_id = :funnel_id
                ORDER BY step_order
            ),
            first_step_time AS (
                SELECT
                    e.user_id,
                    e.step_name,
                    MIN(e.created_at) AS first_time
                FROM events e
                WHERE e.funnel_name = :funnel_name
                GROUP BY e.user_id, e.step_name
            ),
            step_pairs AS (
                SELECT
                    os.step_order,
                    os.step_name,
                    os.next_step_order,
                    os.next_step_name,
                    fst1.user_id,
                    fst1.first_time AS step_time,
                    fst2.first_time AS next_step_time
                FROM ordered_steps os
                JOIN first_step_time fst1
                    ON fst1.step_name = os.step_name
                JOIN first_step_time fst2
                    ON fst2.step_name = os.next_step_name
                   AND fst2.user_id = fst1.user_id
                WHERE os.next_step_name IS NOT NULL
            )
            SELECT
                step_order,
                step_name,
                next_step_order,
                next_step_name,
                COUNT(*) AS users_with_both_steps,
                ROUND(AVG(EXTRACT(EPOCH FROM (next_step_time - step_time)) / 60), 2) AS avg_minutes_to_next_step,
                ROUND(MIN(EXTRACT(EPOCH FROM (next_step_time - step_time)) / 60), 2) AS min_minutes_to_next_step,
                ROUND(MAX(EXTRACT(EPOCH FROM (next_step_time - step_time)) / 60), 2) AS max_minutes_to_next_step
            FROM step_pairs
            WHERE next_step_time >= step_time
            GROUP BY step_order, step_name, next_step_order, next_step_name
            ORDER BY step_order;
        """)

        rows = db.execute(time_query, {
            "funnel_id": funnel_id,
            "funnel_name": funnel_name
        }).mappings().all()

        time_analysis = [dict(r) for r in rows]

        slowest_transition = None
        if time_analysis:
            slowest_transition = max(
                time_analysis,
                key=lambda x: x["avg_minutes_to_next_step"] if x["avg_minutes_to_next_step"] is not None else -1
            )

        return {
            "funnel_id": funnel_id,
            "funnel_name": funnel_name,
            "slowest_transition": slowest_transition,
            "time_analysis": time_analysis
        }

    finally:
        db.close()
