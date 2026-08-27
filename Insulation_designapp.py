import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Configure Page
st.set_page_config(
    page_title="High Voltage Bushing Design Lab",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div.stButton > button {
        background-color: #00E5FF !important;
        color: #0E1117 !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        width: 100%;
        height: 45px;
    }
    div.stButton > button:hover { background-color: #80D8FF !important; }
    .main-title { color: #00E5FF; font-size: 2.2rem; font-weight: 700; margin-bottom: 0px; }
    .sub-title { color: #B0BEC5; font-size: 1.2rem; font-weight: 500; margin-top: 4px; margin-bottom: 20px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">EE18PE: High Voltage Engineering</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Modules 1–3: Coastal Substation Bushing Insulation Design Lab</div>',
    unsafe_allow_html=True,
)
st.divider()

# --- MATERIAL DATABASE ---
MATERIALS = {
    "Material 1: Epoxy Resin": {
        "E_int": 25.0,
        "er": 3.8,
        "cr_ratio": 31.0,
        "cost_factor": 1.0,
        "tracking_res": "Moderate",
    },
    "Material 2: HDPE": {
        "E_int": 18.0,
        "er": 2.3,
        "cr_ratio": 28.0,
        "cost_factor": 0.8,
        "tracking_res": "Poor",
    },
    "Material 3: Silicone Rubber (HTV)": {
        "E_int": 20.0,
        "er": 2.9,
        "cr_ratio": 45.0,
        "cost_factor": 1.4,
        "tracking_res": "Excellent (Hydrophobic)",
    },
    "Material 4: Electrical Porcelain": {
        "E_int": 12.0,
        "er": 6.0,
        "cr_ratio": 31.0,
        "cost_factor": 0.6,
        "tracking_res": "Good",
    },
}

# --- SIDEBAR: PROBLEM STATEMENT & GIVEN DATA TABLES ---
st.sidebar.header("📌 Operating Conditions")

op_data = {
    "Parameter": [
        "System Voltage (V_max)",
        "Overvoltage Factor (k_p)",
        "Safety Factor (SF)",
        "Environment",
        "Pollution Factor (k_env)",
        "Air Density (δ)",
    ],
    "Value": [
        "145.0 kV (rms L-L)",
        "4.2 p.u.",
        "1.25",
        "Coastal Industrial",
        "0.35",
        "1.0",
    ],
}
df_op = pd.DataFrame(op_data)
st.sidebar.table(df_op)

st.sidebar.markdown("### 📚 Candidate Materials Data")

mat_table_data = []
for name, spec in MATERIALS.items():
    mat_table_data.append(
        {
            "Material": name.split(":")[1].strip(),
            "E_int (kV/mm)": spec["E_int"],
            "ε_r": spec["er"],
            "Creepage Ratio (mm/kV)": spec["cr_ratio"],
        }
    )
df_mat = pd.DataFrame(mat_table_data)
st.sidebar.table(df_mat)

# --- MAIN DESIGN INPUTS ---
st.subheader("🛠️ Student Design Input Panel")
col_in1, col_in2 = st.columns(2)

with col_in1:
    selected_mat = st.selectbox(
        "1. Select Solid Dielectric Material", list(MATERIALS.keys())
    )
    student_Vimp = st.number_input(
        "2. Calculated Design Impulse Voltage V_impulse (kV peak)",
        value=0.0,
        step=10.0,
        format="%.2f",
    )
    student_d = st.number_input(
        "3. Designed Solid Core Thickness d_solid (mm)",
        value=0.0,
        step=1.0,
        format="%.2f",
    )

with col_in2:
    student_Lc = st.number_input(
        "4. Designed Creepage Distance L_c (mm)",
        value=0.0,
        step=100.0,
        format="%.1f",
    )
    student_E_max = st.number_input(
        "5. Maximum Electric Field in Solid Stress Point (kV/mm)",
        value=0.0,
        step=0.5,
        format="%.2f",
    )
    evaluate_btn = st.button("🚀 Evaluate Bushing Design")

# --- EXACT GROUND TRUTH CALCULATIONS ---
mat_spec = MATERIALS[selected_mat]
true_V_peak_LG = (145.0 * np.sqrt(2)) / np.sqrt(3)  # ~118.39 kV
true_V_surge = 4.2 * true_V_peak_LG                 # ~497.24 kV
true_V_impulse = true_V_surge * 1.25                # ~621.55 kV

true_d = true_V_impulse / mat_spec["E_int"]
true_Lc = mat_spec["cr_ratio"] * 145.0
true_cost_index = (true_d**2) * true_Lc * mat_spec["cost_factor"]

# --- EVALUATION LOGIC ---
st.divider()

if evaluate_btn:
    v_err = abs(student_Vimp - true_V_impulse) / true_V_impulse * 100
    d_err = abs(student_d - true_d) / true_d * 100
    lc_err = abs(student_Lc - true_Lc) / true_Lc * 100

    st.subheader("🔍 Design Verification & Diagnostics")

    if student_d <= 0 or student_Vimp <= 0 or student_Lc <= 0:
        st.error("⚠️ **INCOMPLETE INPUTS:** Please enter your calculated values.")
    else:
        applied_stress = student_Vimp / student_d if student_d > 0 else 999.0
        puncture_risk = applied_stress > mat_spec["E_int"]
        flashover_risk = student_Lc < true_Lc
        voltage_incorrect = v_err > 5.0

        if not puncture_risk and not flashover_risk and not voltage_incorrect:
            st.success("✅ **DESIGN APPROVED!** Your parameters are safe and within acceptable tolerances.")
            st.info(
                f"📊 **Material Volumetric Cost Index:** {true_cost_index:.2e} | "
                f"Material: {selected_mat}"
            )
            st.balloons()
        else:
            st.error("❌ **DESIGN FAILURE DETECTED!** Review your calculations and parameters.")
            if puncture_risk:
                st.write(
                    f"💥 **INTERNAL DIELECTRIC PUNCTURE:** The applied electrical stress "
                    f"({applied_stress:.2f} kV/mm) exceeds the allowable breakdown strength of "
                    f"{selected_mat} ({mat_spec['E_int']} kV/mm)."
                )
            if flashover_risk:
                st.write(
                    "⚡ **SURFACE FLASHOVER:** Your designed Creepage Distance (L_c) is insufficient "
                    "for the specified coastal pollution severity, risking external arc-over."
                )
            if voltage_incorrect:
                st.write(
                    "⚠️ **INCORRECT IMPULSE VOLTAGE:** Your calculated V_impulse value "
                    "does not match the expected impulse withstand voltage for these operating conditions."
                )

# --- VISUALIZATION PLOTS ---
st.subheader("📈 Electrical & Dielectric Simulation Diagnostics")

tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ Lightning Impulse Wave",
    "💥 Dielectric Breakdown Curve",
    "🌿 Treeing & Tracking Severity",
    "🌌 Radial Electric Field in Space",
])

plt.style.use("dark_background")

# 1. LIGHTNING IMPULSE WAVEFORM (1.2 / 50 μs)
with tab1:
    fig1, ax1 = plt.subplots(figsize=(8.5, 3.8))
    fig1.patch.set_facecolor("#161B22")
    ax1.set_facecolor("#0E1117")

    t = np.linspace(0, 100, 1000)
    
    # Ideal Wave
    v_ideal = true_V_impulse * 1.037 * (np.exp(-0.014 * t) - np.exp(-2.47 * t))
    ax1.plot(t, v_ideal, color="#FFEA00", linestyle="--", lw=1.8, label="Target Required Impulse Wave")

    # Student Wave
    if student_Vimp > 0:
        v_student = student_Vimp * 1.037 * (np.exp(-0.014 * t) - np.exp(-2.47 * t))
        ax1.plot(t, v_student, color="#00E5FF", lw=2.5, label=f"Student Calculated Wave (Peak = {student_Vimp:.1f} kV)")

    ax1.axvline(1.2, color="#8B949E", linestyle=":", alpha=0.7, label=r"Front Time $t_1$ = 1.2 $\mu$s")
    ax1.axvline(50.0, color="#8B949E", linestyle=":", alpha=0.7, label=r"Tail Time $t_2$ = 50 $\mu$s")

    ax1.set_title("Standard Lightning Impulse Waveform (1.2/50 $\mu$s) Comparison", color="#FFFFFF")
    ax1.set_xlabel(r"Time ($\mu$s)")
    ax1.set_ylabel("Voltage (kV)")
    ax1.grid(True, color="#2E3646")
    ax1.legend()
    st.pyplot(fig1)

# 2. DIELECTRIC BREAKDOWN CURVE
with tab2:
    fig2, ax2 = plt.subplots(figsize=(8.5, 3.8))
    fig2.patch.set_facecolor("#161B22")
    ax2.set_facecolor("#0E1117")

    d_arr = np.linspace(5, 60, 500)
    v_withstand = d_arr * mat_spec["E_int"]

    ax2.plot(d_arr, v_withstand, color="#00E5FF", lw=2.5, label=f"Puncture Limit ({selected_mat})")

    if student_d > 0 and student_Vimp > 0:
        is_safe = (student_Vimp / student_d) <= mat_spec["E_int"]
        p_color = "#00E5FF" if is_safe else "#FF1744"
        ax2.scatter([student_d], [student_Vimp], color=p_color, s=120, zorder=5, 
                    label=f"Student Design Point ({'Safe' if is_safe else 'Puncture Risk'})")

    ax2.set_title("Solid Insulation Puncture Boundary vs. Operating Point", color="#FFFFFF")
    ax2.set_xlabel("Solid Thickness d (mm)")
    ax2.set_ylabel("Withstand Voltage (kV)")
    ax2.grid(True, color="#2E3646")
    ax2.legend()
    st.pyplot(fig2)

# 3. TREEING & TRACKING SEVERITY PLOT
with tab3:
    fig3, ax3 = plt.subplots(figsize=(8.5, 3.8))
    fig3.patch.set_facecolor("#161B22")
    ax3.set_facecolor("#0E1117")

    x_surface = np.linspace(0, 100, 500)

    # Ideal Curve
    ideal_tracking = (np.exp(x_surface / 25 * 1.0) - 1) / 10.0
    ax3.plot(x_surface, ideal_tracking, color="#FFEA00", linestyle="--", lw=1.8, label="Target Safe Tracking Profile")

    # Student Curve
    if student_Lc > 0:
        stress_ratio = true_Lc / student_Lc
        student_tracking = (np.exp(x_surface / 25 * stress_ratio) - 1) / 10.0
        p_color = "#FF1744" if stress_ratio > 1.0 else "#00E5FF"
        ax3.plot(x_surface, student_tracking, color=p_color, lw=2.5, label="Student Designed Tracking Profile")

    ax3.set_title("Surface Tracking Severity along Creepage Path", color="#FFFFFF")
    ax3.set_xlabel("Creepage Distance Span (%)")
    ax3.set_ylabel("Tracking Degradation (A.U.)")
    ax3.grid(True, color="#2E3646")
    ax3.legend()
    st.pyplot(fig3)

# 4. RADIAL ELECTRIC FIELD IN SPACE
with tab4:
    fig4, ax4 = plt.subplots(figsize=(8.5, 3.8))
    fig4.patch.set_facecolor("#161B22")
    ax4.set_facecolor("#0E1117")

    r_inner = 15.0  # mm

    # Ideal Distribution Curve
    r_outer_ideal = r_inner + true_d
    r_space_ideal = np.linspace(r_inner, r_outer_ideal + 30.0, 500)
    E_r_ideal = true_V_impulse / (r_space_ideal * np.log(r_outer_ideal / r_inner))
    ax4.plot(r_space_ideal, E_r_ideal, color="#FFEA00", linestyle="--", lw=1.8, label=r"Ideal Field Distribution $E(r)$")

    # Student Distribution Curve
    if student_d > 0 and student_Vimp > 0:
        r_outer_stud = r_inner + student_d
        r_space_stud = np.linspace(r_inner, r_outer_stud + 30.0, 500)
        E_r_stud = student_Vimp / (r_space_stud * np.log(r_outer_stud / r_inner))
        ax4.plot(r_space_stud, E_r_stud, color="#00E5FF", lw=2.5, label=r"Student Field Distribution $E(r)$")
        ax4.axvline(r_outer_stud, color="#00E5FF", linestyle=":", label="Student Outer Interface")

    ax4.axhline(mat_spec["E_int"], color="#FF1744", linestyle=":", label=f"Material Breakdown Threshold ({mat_spec['E_int']} kV/mm)")

    ax4.set_title("2D Radial Electric Field Stress Curve Comparison", color="#FFFFFF")
    ax4.set_xlabel("Radial Distance r (mm)")
    ax4.set_ylabel("Electric Field Stress E (kV/mm)")
    ax4.grid(True, color="#2E3646")
    ax4.legend()
    st.pyplot(fig4)

# --- FOOTER ---
st.markdown(
    '<div style="color: #8B949E; font-size: 0.85rem; text-align: center; margin-top: 40px;">'
    "Developed by Mr. Mondeep Mazumder, Assistant Professor, Department of Electrical Engineering"
    "</div>",
    unsafe_allow_html=True,
)
