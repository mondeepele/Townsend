import matplotlib.pyplot as plt
import numpy as np
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
    '<div class="main-title">EE601: High Voltage Engineering</div>',
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

# --- SIDEBAR: PROBLEM STATEMENT & GIVEN DATA ---
st.sidebar.header("📌 Given Operating Conditions")
st.sidebar.write(r"**System Voltage ($V_{max}$):** 145.0 kV (rms L-L)")
st.sidebar.write(r"**Overvoltage Factor ($k_p$):** 4.2 p.u.")
st.sidebar.write(r"**Safety Factor ($SF$):** 1.25")
st.sidebar.write("**Environment:** Coastal Industrial (Salt spray)")
st.sidebar.write(
    r"**Pollution Factor ($k_{env}$):** 0.35 | Air Density ($\delta$): 1.0"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Candidate Materials Data")
for name, spec in MATERIALS.items():
    st.sidebar.markdown(f"**{name}**")
    st.sidebar.caption(
        f"E_int: {spec['E_int']} kV/mm | \u03b5_r: {spec['er']} | Creepage Ratio: {spec['cr_ratio']} mm/kV"
    )

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

# --- GROUND TRUTH CALCULATIONS ---
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

        if not puncture_risk and not flashover_risk and v_err <= 5.0:
            st.success(
                f"✅ **DESIGN APPROVED!** Your parameters safely withstand the "
                f"{true_V_impulse:.1f} kV impulse."
            )
            st.info(
                f"📊 **Material Volumetric Cost Index:** {true_cost_index:.2e} | "
                f"Material: {selected_mat}"
            )
            st.balloons()
        else:
            st.error("❌ **DESIGN FAILURE DETECTED!**")
            if puncture_risk:
                st.write(
                    f"💥 **INTERNAL DIELECTRIC PUNCTURE:** Applied stress ({applied_stress:.2f} kV/mm) "
                    f"exceeds breakdown strength ({mat_spec['E_int']} kV/mm). "
                    "**Result:** Irreversible solid insulation puncture & treeing."
                )
            if flashover_risk:
                st.write(
                    f"⚡ **SURFACE FLASHOVER:** Designed Creepage ({student_Lc} mm) "
                    f"is less than required ({true_Lc} mm). "
                    "**Result:** Pollution tracking leading to external arc-over."
                )
            if v_err > 5.0:
                st.write(
                    f"⚠️ **WRONG SURGE VOLTAGE:** Your impulse calculation ({student_Vimp} kV) "
                    f"deviates from expected ({true_V_impulse:.1f} kV)."
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
    v_peak = student_Vimp if student_Vimp > 0 else true_V_impulse
    v_t = v_peak * 1.037 * (np.exp(-0.014 * t) - np.exp(-2.47 * t))

    ax1.plot(t, v_t, color="#00E5FF", lw=2.5, label="Transient Impulse Wave")
    ax1.axvline(1.2, color="#FFEA00", linestyle="--", alpha=0.7, label=r"Front Time $t_1$ = 1.2 $\mu$s")
    ax1.axvline(50.0, color="#FF1744", linestyle="--", alpha=0.7, label=r"Tail Time $t_2$ = 50 $\mu$s")

    ax1.set_title(f"Standard Lightning Impulse Waveform 1.2/50 $\mu$s (Peak = {v_peak:.1f} kV)", color="#FFFFFF")
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

    ax2.plot(d_arr, v_withstand, color="#00E5FF", lw=2.5, label=f"Puncture Threshold ({selected_mat})")
    ax2.axhline(true_V_impulse, color="#FFEA00", linestyle=":", lw=2, label=f"Design Impulse Level ({true_V_impulse:.1f} kV)")

    if student_d > 0 and student_Vimp > 0:
        p_color = "#FF1744" if (student_Vimp / student_d) > mat_spec["E_int"] else "#00E5FF"
        ax2.scatter([student_d], [student_Vimp], color=p_color, s=120, zorder=5, label="Student Operating Point")

    ax2.set_title("Solid Insulation Puncture Boundary", color="#FFFFFF")
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
    stress_ratio = (true_Lc / student_Lc) if student_Lc > 0 else 2.5
    tracking_severity = (np.exp(x_surface / 25 * stress_ratio) - 1) / 10.0

    ax3.plot(x_surface, tracking_severity, color="#FF1744" if stress_ratio > 1.0 else "#00E5FF", lw=2.5, label="Surface Degradation Rate")
    ax3.set_title(f"Surface Tracking Severity along Creepage Path (Stress Multiplier: {stress_ratio:.2f}x)", color="#FFFFFF")
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

    r_inner = 15.0
    r_outer = r_inner + (student_d if student_d > 0 else true_d)
    r_space = np.linspace(r_inner, r_outer + 30.0, 500)

    v_applied = student_Vimp if student_Vimp > 0 else true_V_impulse
    geom_factor = np.log(r_outer / r_inner)
    E_r = v_applied / (r_space * geom_factor)

    ax4.plot(r_space, E_r, color="#00E5FF", lw=2.5, label=r"Field Distribution $E(r)$")
    ax4.axvline(r_outer, color="#FFEA00", linestyle="--", label="Solid/Air Interface Boundary")
    ax4.axhline(mat_spec["E_int"], color="#FF1744", linestyle=":", label=f"Solid Limit ({mat_spec['E_int']} kV/mm)")

    ax4.set_title("2D Radial Electric Field Distribution Space Curve", color="#FFFFFF")
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
