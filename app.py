"""CAPA Tracker - Corrective and Preventive Action log with a Streamlit dashboard."""
from datetime import date, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

SOURCES = ["Customer complaint", "Internal audit", "Non-conformance",
           "Process deviation", "Supplier issue"]
CAUSES = ["Man", "Machine", "Method", "Material", "Measurement", "Environment"]
STATUSES = ["Open", "In progress", "Closed"]
CHECKS = ["Not checked", "Effective", "Not effective"]
COLUMNS = ["ID", "Raised", "Source", "Problem", "Root cause category",
           "Root cause detail", "Corrective action", "Preventive action",
           "Owner", "Due", "Status", "Closed on", "Effectiveness"]


def sample_data():
    """Made-up CAPA records with dates relative to today."""
    t = date.today()
    d = lambda n: None if n is None else t + timedelta(days=n)
    rows = [
        ("Customer complaint", "Label misprint on finished pallets", "Method",
         "Wrong label template loaded at start-up", "Reprint labels and re-check pallets",
         "Add template check to the start-up checklist", "Line Supervisor", -60, -30, "Closed", -35, "Effective"),
        ("Internal audit", "Calibration sticker overdue on caliper", "Measurement",
         "Calibration schedule not reviewed monthly", "Calibrate the caliper now",
         "Monthly calibration review in the QC plan", "QC Lead", -55, -40, "Closed", -42, "Effective"),
        ("Non-conformance", "Dimension out of tolerance on part batch", "Machine",
         "Tool wear not tracked", "Replace tool and sort the batch",
         "Add tool-life counter and change interval", "Maintenance", -45, -20, "Closed", -18, "Not effective"),
        ("Process deviation", "Wrong mixing time recorded", "Man",
         "Operator not trained on new work instruction", "Retrain operators",
         "Training sign-off before new instructions go live", "Line Supervisor", -35, -10, "Closed", -12, "Effective"),
        ("Supplier issue", "Raw material out of spec on delivery", "Material",
         "No incoming inspection for new supplier lot", "Reject lot and request replacement",
         "Add incoming inspection plan for new suppliers", "Quality Engineer", -30, -5, "In progress", None, "Not checked"),
        ("Non-conformance", "Defect rate spike on night shift", "Method",
         "Set-up sheet not followed", "Re-run set-up verification",
         "Add second-person set-up check", "QC Lead", -25, -3, "In progress", None, "Not checked"),
        ("Customer complaint", "Packaging damaged in transit", "Method",
         "Stacking height not defined", "Update the packing specification",
         "Define max stacking height on the pallet label", "Quality Engineer", -20, 10, "In progress", None, "Not checked"),
        ("Internal audit", "Gauge R&R not done for new gauge", "Measurement",
         "No requirement in new-equipment procedure", "Run a gauge R&R study",
         "Add gauge R&R to the new-equipment checklist", "QC Lead", -15, 15, "Open", None, "Not checked"),
        ("Process deviation", "Temperature drifting above limit", "Environment",
         "Ventilation blocked by stored materials", "Clear the area and restore airflow",
         "Mark a no-storage zone and add a weekly check", "Maintenance", -10, -2, "Open", None, "Not checked"),
        ("Non-conformance", "Inspection records missing signatures", "Method",
         "Shift handover step unclear", "Complete the missing records",
         "Add a signature check to shift handover", "Line Supervisor", -5, 20, "Open", None, "Not checked"),
        ("Supplier issue", "Wrong grade of material delivered", "Material",
         "Purchase order missing grade specification", "Return the material",
         "Add grade to the purchase-order template", "Quality Engineer", -50, -25, "Closed", -28, "Effective"),
        ("Non-conformance", "Machine stops during run", "Machine",
         "Sensor misaligned after cleaning", "Realign the sensor",
         "Add sensor check to the cleaning SOP", "Maintenance", -12, 5, "In progress", None, "Not checked"),
    ]
    records = []
    for i, r in enumerate(rows, start=1):
        src, prob, cat, detail, corr, prev, owner, raised, due, status, closed, eff = r
        records.append([f"CAPA-{i:03d}", d(raised), src, prob, cat, detail, corr,
                        prev, owner, d(due), status, d(closed), eff])
    return pd.DataFrame(records, columns=COLUMNS)


def overdue_mask(df):
    today = pd.Timestamp(date.today())
    return (df["Status"] != "Closed") & (pd.to_datetime(df["Due"]) < today)


def average_days_to_close(df):
    closed = df[df["Status"] == "Closed"].dropna(subset=["Closed on"])
    if closed.empty:
        return None
    days = (pd.to_datetime(closed["Closed on"]) - pd.to_datetime(closed["Raised"])).dt.days
    return round(days.mean(), 1)


def pareto_chart(df):
    counts = df["Root cause category"].value_counts()
    cumulative = counts.cumsum() / counts.sum() * 100
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.bar(counts.index, counts.values, color="tab:blue")
    ax.set_ylabel("Number of CAPAs")
    ax.tick_params(axis="x", rotation=30)
    ax2 = ax.twinx()
    ax2.plot(counts.index, cumulative.values, color="tab:red", marker="o")
    ax2.axhline(80, color="grey", linestyle="--", linewidth=1)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("Cumulative %")
    fig.tight_layout()
    return fig


def next_id(df):
    if df.empty:
        return "CAPA-001"
    return f"CAPA-{max(int(i.split('-')[1]) for i in df['ID']) + 1:03d}"


st.set_page_config(page_title="CAPA Tracker")
st.title("CAPA Tracker")
st.caption(
    "Corrective and Preventive Action log. Records start as made-up sample data. "
    "Do not enter confidential company data: this app is public, and records "
    "last only for your session, so download the CSV to keep them."
)

if "capas" not in st.session_state:
    st.session_state.capas = sample_data()
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

df = st.session_state.capas
tab_dash, tab_log, tab_update, tab_data = st.tabs(
    ["Dashboard", "Log a CAPA", "Update", "Data"]
)

with tab_dash:
    if df.empty:
        st.info("No CAPAs yet. Add one in the 'Log a CAPA' tab, or load the sample data in 'Data'.")
    else:
        overdue = overdue_mask(df)
        avg_days = average_days_to_close(df)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", len(df))
        c2.metric("Not closed", int((df["Status"] != "Closed").sum()))
        c3.metric("Overdue", int(overdue.sum()))
        c4.metric("Avg days to close", "n/a" if avg_days is None else avg_days)

        st.subheader("Root cause Pareto")
        st.pyplot(pareto_chart(df))
        st.caption("Bars show how many CAPAs each cause category has. The red line is the "
                   "cumulative percentage, and the dashed line marks 80%.")

        st.subheader("Overdue actions")
        if overdue.any():
            st.dataframe(df[overdue][["ID", "Problem", "Owner", "Due", "Status"]],
                         hide_index=True)
        else:
            st.success("No overdue CAPAs.")

        st.subheader("All CAPAs")
        st.dataframe(df[["ID", "Raised", "Source", "Problem", "Root cause category",
                         "Owner", "Due", "Status", "Effectiveness"]], hide_index=True)

with tab_log:
    with st.form("log_capa", clear_on_submit=True):
        source = st.selectbox("Source", SOURCES)
        problem = st.text_area("Problem description")
        cause_cat = st.selectbox("Root cause category (6M)", CAUSES)
        cause_detail = st.text_input("Root cause detail")
        corrective = st.text_area("Corrective action (fixes the problem)")
        preventive = st.text_area("Preventive action (stops it coming back)")
        owner = st.text_input("Owner")
        raised = st.date_input("Date raised", value=date.today())
        due = st.date_input("Due date", value=date.today() + timedelta(days=30))
        submitted = st.form_submit_button("Add CAPA")
    if submitted:
        if not problem.strip():
            st.error("Please describe the problem.")
        elif due < raised:
            st.error("The due date cannot be before the date raised.")
        else:
            new_id = next_id(df)
            row = [new_id, raised, source, problem.strip(), cause_cat, cause_detail.strip(),
                   corrective.strip(), preventive.strip(), owner.strip(), due,
                   "Open", None, "Not checked"]
            st.session_state.capas = pd.concat(
                [df, pd.DataFrame([row], columns=COLUMNS)], ignore_index=True)
            st.session_state.flash = f"{new_id} added."
            st.rerun()

with tab_update:
    if df.empty:
        st.info("Nothing to update yet.")
    else:
        capa_id = st.selectbox("Select a CAPA", df["ID"])
        idx = df.index[df["ID"] == capa_id][0]
        st.write(f"**{df.loc[idx, 'Problem']}**")
        st.write(f"Corrective: {df.loc[idx, 'Corrective action']}")
        st.write(f"Preventive: {df.loc[idx, 'Preventive action']}")
        new_status = st.selectbox("Status", STATUSES,
                                  index=STATUSES.index(df.loc[idx, "Status"]))
        new_check = st.selectbox("Effectiveness check", CHECKS,
                                 index=CHECKS.index(df.loc[idx, "Effectiveness"]))
        closed_on = st.date_input("Closed on (used when status is Closed)", value=date.today())
        if st.button("Save update"):
            df.loc[idx, "Status"] = new_status
            df.loc[idx, "Effectiveness"] = new_check
            df.loc[idx, "Closed on"] = closed_on if new_status == "Closed" else None
            st.session_state.capas = df
            st.session_state.flash = f"{capa_id} updated."
            st.rerun()

with tab_data:
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="capa_log.csv", mime="text/csv")
    col_a, col_b = st.columns(2)
    if col_a.button("Load sample data"):
        st.session_state.capas = sample_data()
        st.session_state.flash = "Sample data loaded."
        st.rerun()
    if col_b.button("Start empty"):
        st.session_state.capas = pd.DataFrame(columns=COLUMNS)
        st.session_state.flash = "Started with an empty log."
        st.rerun()
