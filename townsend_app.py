import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="EE601 High Voltage Engineering - Townsend Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark Theme CSS Customization
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    div.stButton > button {
        background-color: #00E5FF !important;
        color: #0E1117 !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        width: 100%;
        height: 45px;
    }
    div.stButton > button:hover {
        background-color: #80D8FF !important;
    }
    .main-title {
        color: #00E5FF;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-title {
        color: #B0BEC5;
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 4px;
        margin-bottom: 25px;
    }
    .footer-text {
        color: #8B949E;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 40px;
        padding-top: 15px;
        border-top: 1px solid #2E3646;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- HEADER SECTION: LOGO & COURSE DETAILS ---
header_col1, header_col2 = st.columns([1, 5])

with header_col1:
    # Loads logo directly from your GitHub repository file
    st.image("aec logo.png", width=110)

with header_col2:
    st.markdown(
        '<div class="main-title">EE601: High Voltage Engineering</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-title">Module 1: Breakdown of Gases — Townsend Primary'
        ' vs. Secondary Model</div>',
        unsafe_allow_html=True,
    )

st.divider()

# --- MAIN APP LAYOUT ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Experimental Conditions")
    I0 = st.number_input(
        "Initial Current I₀ (A)",
        value=1e-11,
        format="%.2e",
        min_value=1e-15,
    )
    d_max = st.number_input(
        "Gap Distance d (cm)", value=1.2, min_value=0.01, step=0.1
    )
    p = st.number_input(
        "Gas Pressure p (Torr)", value=10.0, min_value=0.1, step=1.0
    )
    E = st.number_input(
        "Electric Field E (V/cm)", value=2000.0, min_value=1.0, step=100.0
    )

    st.subheader("2. Student Coefficients")
    alpha = st.number_input(
        "Student α (cm⁻¹)", value=5.0, min_value=0.01, step=0.5
    )
    gamma = st.number_input(
        "Student γ", value=0.0025, format="%.4f", min_value=0.0, step=0.0005
    )

    run_button = st.button("🚀 Run Model Comparison")

with col2:
    if run_button or True:
        x = np.linspace(0, d_max, 1000)

        # Primary Model calculation
        I_primary = I0 * np.exp(alpha * x)

        # Secondary Model calculation
        denominator = 1 - gamma * (np.exp(alpha * x) - 1)
        breakdown_mask = denominator <= 0

        I_secondary = np.zeros_like(x)
        if np.any(breakdown_mask):
            idx_breakdown = np.argmax(breakdown_mask)
            x_breakdown = x[idx_breakdown]
            valid_indices = slice(0, idx_breakdown)
            I_secondary[valid_indices] = (
                I0 * np.exp(alpha * x[valid_indices])
            ) / denominator[valid_indices]
            I_secondary[idx_breakdown:] = np.nan
        else:
            x_breakdown = None
            I_secondary = (I0 * np.exp(alpha * x)) / denominator

        breakdown_factor = gamma * (np.exp(alpha * d_max) - 1)
        V_applied = E * d_max

        # Summary Display Box
        st.markdown(
            f"""
            <div style="background-color: #161B22; padding: 15px; border-radius: 8px; border: 1px solid #2E3646;">
                <b style="color: #00E5FF;">📊 EVALUATION SUMMARY</b><br>
                • <b>Applied Voltage V = E × d:</b> {V_applied:.1f} Volts<br>
                • <b>E/p Ratio:</b> {E/p:.2f} V/(cm·Torr)<br>
                • <b>Primary Amplification exp(αd):</b> {np.exp(alpha * d_max):.2e}<br>
                • <b>Secondary Criterion γ(e^(αd)-1):</b> {breakdown_factor:.4f}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if np.isclose(breakdown_factor, 1.0, atol=0.05):
            st.error("💥 CRITICAL BREAKDOWN: γ(e^(αd) - 1) = 1")
        elif breakdown_factor > 1.0:
            st.warning(
                f"💥 OVER-CRITICAL BREAKDOWN: Sparkover occurs at x ="
                f" {x_breakdown:.2f} cm!"
            )
        else:
            st.success(
                "🛡️ SUB-CRITICAL DISCHARGE: Current amplifies, but breakdown"
                " threshold NOT reached."
            )

        # Matplotlib Plot
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(8.5, 4.5))

        fig.patch.set_facecolor("#161B22")
        ax.set_facecolor("#0E1117")

        ax.semilogy(
            x,
            I_primary,
            color="#00E5FF",
            lw=2.5,
            linestyle="--",
            label=r"Primary Model: $I = I_0 e^{\alpha x}$",
        )
        ax.semilogy(
            x,
            I_secondary,
            color="#FF1744",
            lw=3,
            label=(
                r"Secondary Model: $I = \frac{I_0 e^{\alpha x}}{1 - \gamma(e^{\alpha"
                r" x} - 1)}$"
            ),
        )

        if x_breakdown:
            ax.axvline(
                x=x_breakdown,
                color="#FFEA00",
                linestyle=":",
                lw=2,
                label=rf"Sparkover Boundary ($x = {x_breakdown:.2f}\text{{ cm}}$)",
            )

        ax.set_title(
            "Townsend Current Growth Comparison",
            color="#FFFFFF",
            fontsize=13,
            pad=10,
            fontweight="bold",
        )
        ax.set_xlabel("Gap Distance $x$ (cm)", color="#FFFFFF", fontsize=11)
        ax.set_ylabel(
            "Current $I$ (A) [Semi-Log Scale]", color="#FFFFFF", fontsize=11
        )
        ax.grid(
            True, which="both", color="#2E3646", linestyle="-", linewidth=0.5
        )

        ax.legend(
            facecolor="#161B22",
            edgecolor="#2E3646",
            fontsize=10,
            loc="upper left",
            labelcolor="#FFFFFF",
        )

        plt.tight_layout()
        st.pyplot(fig)

# --- FOOTER SECTION ---
st.markdown(
    '<div class="footer-text">Developed by Mr. Mondeep Mazumder, Assistant'
    " Professor, Department of Electrical Engineering</div>",
    unsafe_allow_html=True,
)
