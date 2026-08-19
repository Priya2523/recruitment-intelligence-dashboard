
import os
import tempfile
from pathlib import Path

import gradio as gr
import pandas as pd
import plotly.express as px

SOURCE_FILE = "recruitment_dashboard_with_groq_messages.xlsx"

SAFE_COLUMNS = [
    "candidate_name",
    "position_applied",
    "recommended_action",
    "joining_risk_score",
    "joining_risk_level",
    "followup_priority",
    "groq_ai_recruiter_task",
    "groq_ai_whatsapp_message",
    "groq_ai_followup_step",
    "groq_ai_plan_status",
]

ACTION_ORDER = [
    "Immediate joining commitment follow-up",
    "Reconfirm notice period and joining date",
    "Confirm salary expectations",
    "Collect missing candidate information",
    "No immediate action",
]

CSS = """
.gradio-container {max-width: 1280px !important;}
.hero {
    background: linear-gradient(135deg, #0f172a, #1d4ed8);
    color: white;
    padding: 28px;
    border-radius: 16px;
    margin-bottom: 16px;
}
.hero h1 {margin: 0; font-size: 32px; color: #ffffff !important; font-weight: 700 !important;}
.hero p {margin: 8px 0 0; opacity: .92; color: #dbeafe !important; font-weight: 500;}
.kpis {
    display: grid;
    grid-template-columns: repeat(4, minmax(145px, 1fr));
    gap: 12px;
    margin: 10px 0 18px;
}
.kpis div {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
}
.kpis span {display:block; color:#475569; font-size:13px;}
.kpis strong {display:block; color:#0f172a; font-size:28px; margin-top:5px;}
"""

def demo_data():
    return pd.DataFrame(
        [
            ["Namrata Choudhary", "Compliance Manager",
             "Immediate joining commitment follow-up", 100.0, "HIGH", "HIGH"],
            ["Charmi Jadawala", "Software Engineer II",
             "Immediate joining commitment follow-up", 100.0, "HIGH", "HIGH"],
            ["Anand Rajput", "Compliance Manager",
             "Reconfirm notice period and joining date", 33.3, "MEDIUM", "MEDIUM"],
            ["Priyank Gupta", "Data Analyst",
             "Confirm salary expectations", 22.2, "MEDIUM", "MEDIUM"],
            ["Mayur Patel", "Research Engineer",
             "Collect missing candidate information", 22.2, "LOW", "LOW"],
            ["Abinav S", "Compliance Manager",
             "No immediate action", 11.1, "LOW", "LOW"],
        ],
        columns=[
            "candidate_name", "position_applied", "recommended_action",
            "joining_risk_score", "joining_risk_level", "followup_priority"
        ]
    )

def clean_data(data):
    frame = data.copy()

    for column in SAFE_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA

    frame["candidate_name"] = frame["candidate_name"].fillna("Unnamed candidate").astype(str)
    frame["position_applied"] = frame["position_applied"].fillna("Not specified").astype(str)
    frame["recommended_action"] = (
        frame["recommended_action"]
        .fillna("No immediate action")
        .astype(str)
        .str.strip()
        .replace("", "No immediate action")
    )
    frame["joining_risk_score"] = pd.to_numeric(
        frame["joining_risk_score"], errors="coerce"
    ).fillna(0)
    frame["joining_risk_level"] = (
        frame["joining_risk_level"].fillna("LOW").astype(str).str.upper()
    )
    frame["followup_priority"] = (
        frame["followup_priority"].fillna("LOW").astype(str).str.upper()
    )

    return frame

def dashboard_outputs(frame):
    actionable = frame[frame["recommended_action"].ne("No immediate action")]
    urgent = frame[
        frame["recommended_action"].eq("Immediate joining commitment follow-up")
    ]
    ai_plans = frame[frame["groq_ai_whatsapp_message"].notna()]

    kpis = f"""
    <div class="kpis">
        <div><span>Total candidates</span><strong>{len(frame):,}</strong></div>
        <div><span>Action required</span><strong>{len(actionable):,}</strong></div>
        <div><span>Urgent joining follow-ups</span><strong>{len(urgent):,}</strong></div>
        <div><span>Saved AI outreach plans</span><strong>{len(ai_plans):,}</strong></div>
    </div>
    """

    action_counts = (
        frame["recommended_action"]
        .value_counts()
        .reindex(ACTION_ORDER, fill_value=0)
        .rename_axis("Recommended action")
        .reset_index(name="Candidates")
    )

    action_chart = px.bar(
        action_counts,
        x="Candidates",
        y="Recommended action",
        orientation="h",
        color="Candidates",
        color_continuous_scale="Blues",
        title="Candidate Distribution by Recommended Action",
    )
    action_chart.update_layout(
        coloraxis_showscale=False,
        height=410,
        margin=dict(l=10, r=10, t=55, b=10),
    )
    action_chart.update_yaxes(categoryorder="total ascending")

    risk_counts = (
        actionable["joining_risk_level"]
        .value_counts()
        .rename_axis("Risk level")
        .reset_index(name="Candidates")
    )

    risk_chart = px.pie(
        risk_counts,
        names="Risk level",
        values="Candidates",
        hole=0.58,
        title="Risk Distribution for Actionable Candidates",
        color="Risk level",
        color_discrete_map={
            "HIGH": "#dc2626",
            "MEDIUM": "#f59e0b",
            "LOW": "#16a34a",
        },
    )
    risk_chart.update_layout(
        height=410,
        margin=dict(l=10, r=10, t=55, b=10),
    )

    return kpis, action_chart, risk_chart

def filter_candidates(frame, action, minimum_risk, search_text):
    filtered = frame.copy()

    if action != "All actions":
        filtered = filtered[filtered["recommended_action"].eq(action)]

    filtered = filtered[filtered["joining_risk_score"] >= minimum_risk]

    term = (search_text or "").strip().lower()
    if term:
        filtered = filtered[
            filtered["candidate_name"].str.lower().str.contains(term, na=False)
            | filtered["position_applied"].str.lower().str.contains(term, na=False)
        ]

    filtered = filtered.sort_values(
        ["joining_risk_score", "candidate_name"],
        ascending=[False, True],
    )

    queue_columns = [
        "candidate_name",
        "position_applied",
        "recommended_action",
        "joining_risk_score",
        "joining_risk_level",
        "followup_priority",
        "groq_ai_recruiter_task",
    ]

    return (
        filtered[queue_columns]
        .rename(columns={
            "candidate_name": "Candidate",
            "position_applied": "Position",
            "recommended_action": "Recommended Action",
            "joining_risk_score": "Risk Score",
            "joining_risk_level": "Risk Level",
            "followup_priority": "Priority",
            "groq_ai_recruiter_task": "AI Recruiter Task",
        })
        .reset_index(drop=True)
    )

def load_data(file_path):
    if file_path:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".csv":
            frame = pd.read_csv(file_path)
        else:
            frame = pd.read_excel(file_path)
        status = f"Loaded {len(frame):,} candidate records."
    elif Path(SOURCE_FILE).exists():
        frame = pd.read_excel(SOURCE_FILE)
        status = f"Loaded saved project file: {SOURCE_FILE}"
    else:
        frame = demo_data()
        status = "Showing synthetic demo data. Upload your Excel/CSV file to replace it."

    frame = clean_data(frame)
    kpis, action_chart, risk_chart = dashboard_outputs(frame)

    return frame, kpis, action_chart, risk_chart, status, filter_candidates(
        frame, "All actions", 0, ""
    )

def export_data(frame):
    output = tempfile.NamedTemporaryFile(
        prefix="recruitment_dashboard_export_",
        suffix=".xlsx",
        delete=False,
    )
    output.close()

    # Export only prototype-safe columns; no phone numbers or emails
    frame[SAFE_COLUMNS].to_excel(output.name, index=False)
    return output.name

initial_frame, initial_kpis, initial_action_chart, initial_risk_chart, initial_status, initial_queue = load_data(None)

with gr.Blocks(title="Recruitment Intelligence Dashboard") as app:
    state = gr.State(initial_frame)

    gr.HTML("""
    <div class="hero">
        <h1>Recruitment Intelligence Dashboard</h1>
        <p>AI-supported candidate prioritisation and recruiter outreach planning</p>
    </div>
    """)

    with gr.Row():
        upload = gr.File(
            label="Upload saved recruitment workbook (CSV/XLSX)",
            file_types=[".csv", ".xlsx", ".xls"],
            type="filepath",
        )
        status = gr.Markdown(initial_status)

    with gr.Tab("Overview"):
        kpis = gr.HTML(initial_kpis)

        with gr.Row():
            action_plot = gr.Plot(initial_action_chart)
            risk_plot = gr.Plot(initial_risk_chart)

    with gr.Tab("Candidate Action Queue"):
        with gr.Row():
            action_filter = gr.Dropdown(
                choices=["All actions"] + ACTION_ORDER,
                value="All actions",
                label="Recommended action",
            )
            risk_filter = gr.Slider(
                minimum=0,
                maximum=100,
                value=0,
                step=1,
                label="Minimum joining-risk score",
            )
            search_filter = gr.Textbox(
                label="Search candidate or role",
                placeholder="Example: Abinav or Data Analytics",
            )

        queue = gr.Dataframe(
            value=initial_queue,
            interactive=False,
            label="Prototype-safe candidate queue",
            wrap=True,
        )

    with gr.Tab("Export"):
        gr.Markdown(
            "Download the current dashboard data. "
            "Phone numbers and email addresses are excluded."
        )
        export_button = gr.Button("Prepare Excel export", variant="primary")
        download = gr.File(label="Download export")

    upload.change(
        load_data,
        inputs=upload,
        outputs=[state, kpis, action_plot, risk_plot, status, queue],
    )

    for control in [action_filter, risk_filter, search_filter]:
        control.change(
            filter_candidates,
            inputs=[state, action_filter, risk_filter, search_filter],
            outputs=queue,
        )

    export_button.click(export_data, inputs=state, outputs=download)

if __name__ == "__main__":
    import socket

    def get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("", 0))
            return sock.getsockname()[1]

    is_colab = bool(os.getenv("COLAB_RELEASE_TAG"))
    port = int(os.getenv("PORT", get_free_port()))

    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=is_colab,
        css=CSS,
    )
