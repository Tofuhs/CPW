import streamlit as st
import numpy as np
from scipy.special import ellipk

# ==========================================
# 輔助函數：工程單位自動轉換 (自動切換 p, n, u, m 等)
# ==========================================
def format_eng(value, unit):
    if value == 0:
        return f"0.0000 {unit}"
    abs_val = abs(value)
    if abs_val >= 1:
        return f"{value:.4f} {unit}"
    elif abs_val >= 1e-3:
        return f"{value*1e3:.4f} m{unit}"
    elif abs_val >= 1e-6:
        return f"{value*1e6:.4f} μ{unit}"
    elif abs_val >= 1e-9:
        return f"{value*1e9:.4f} n{unit}"
    elif abs_val >= 1e-12:
        return f"{value*1e12:.4f} p{unit}"
    elif abs_val >= 1e-15:
        return f"{value*1e15:.4f} f{unit}"
    else:
        return f"{value*1e18:.4f} a{unit}"

# ==========================================
# 物理常數與材質資料庫
# ==========================================
EPSILON_0 = 8.8541878128e-12  # F/m
MU_0 = 4 * np.pi * 1e-7       # H/m
C_SPEED = 299792458.0         # m/s

SUBSTRATES = {
    "Vacuum / Air": 1.0,
    "Teflon (PTFE)": 2.1,
    "Rogers RO4003C": 3.38,
    "FR4": 4.4,
    "Sapphire": 9.4,
    "Alumina": 9.9,
    "Silicon": 11.8,
    "GaAs": 12.9,
    "Custom": 0.0
}

st.set_page_config(page_title="CPW Calculator", layout="wide")

st.title("CPW Resonator Calculator")
st.markdown("計算共平面波導的傳輸線參數 ($C_l, L_l$) 以及對應的 **DC 結果** 與 **AC 等效結果 (n=1)**")

# ==========================================
# 1. 參數輸入區 
# ==========================================
st.header("1. Parameters Input")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Substrate (基板)")
    material = st.selectbox("Dielectric Material", list(SUBSTRATES.keys()), index=6) 
    if material == "Custom":
        er = st.number_input("εr (Relative Permittivity)", min_value=1.0, value=11.8, step=0.1)
    else:
        er = st.number_input("εr (Relative Permittivity)", value=SUBSTRATES[material], disabled=True)
    # 依照您的要求，預設基板厚度改為 500 um
    h_um = st.number_input("Substrate Thickness (h) [μm]", min_value=1.0, value=500.0, step=10.0)

with col2:
    st.subheader("Cross-Section (截面幾何)")
    w_um = st.number_input("Signal Width (w) [μm]", min_value=0.1, value=10.0, step=1.0)
    s_um = st.number_input("Gap (s) [μm]", min_value=0.1, value=6.0, step=1.0)
    t_nm = st.number_input("Metal Thickness (t) [nm]", min_value=1.0, value=100.0, step=10.0)

with col3:
    st.subheader("Transmission Line (傳輸線)")
    # 預設為簡報中的 lambda/2 長度 (19.935 mm / 2 = 9.9675 mm) 方便您驗證
    l_mm = st.number_input("CPW Length (l) [mm]", min_value=0.01, value=9.9675, step=0.1, format="%.4f")

# ==========================================
# 2. 動態視覺化 CPW 結構 (SVG)
# ==========================================
st.header("2. CPW Cross-Section (動態示意圖)")

# 動態調整 SVG 繪圖比例
w_disp = max(w_um, 2) * 10
s_disp = max(s_um, 2) * 10
center_x = 400
signal_x = center_x - w_disp/2
gnd_left_x = signal_x - s_disp - 200
gnd_right_x = signal_x + w_disp + s_disp

svg_code = f"""
<svg viewBox="0 0 800 250" width="100%" xmlns="http://www.w3.org/2000/svg">
  <!-- Substrate -->
  <rect x="50" y="140" width="700" height="90" fill="#e0e0e0" stroke="#333" stroke-width="2"></rect>
  <text x="400" y="195" font-size="18" text-anchor="middle" font-family="sans-serif" fill="#333">Dielectric Substrate (εr={er}), h = {h_um} μm</text>

  <!-- Ground Left -->
  <rect x="50" y="110" width="{gnd_left_x + 200 - 50}" height="30" fill="#ffd700" stroke="#b8860b" stroke-width="2"></rect>
  <text x="100" y="132" font-size="16" text-anchor="middle" font-family="sans-serif" font-weight="bold">GND</text>

  <!-- Signal Trace -->
  <rect x="{signal_x}" y="110" width="{w_disp}" height="30" fill="#ffd700" stroke="#b8860b" stroke-width="2"></rect>
  <text x="{center_x}" y="132" font-size="16" text-anchor="middle" font-family="sans-serif" font-weight="bold">w={w_um}</text>

  <!-- Ground Right -->
  <rect x="{gnd_right_x}" y="110" width="{750 - gnd_right_x}" height="30" fill="#ffd700" stroke="#b8860b" stroke-width="2"></rect>
  <text x="700" y="132" font-size="16" text-anchor="middle" font-family="sans-serif" font-weight="bold">GND</text>

  <!-- Dimensions -->
  <line x1="{signal_x - s_disp}" y1="100" x2="{signal_x}" y2="100" stroke="red" stroke-width="2"></line>
  <text x="{signal_x - s_disp/2}" y="90" font-size="14" fill="red" text-anchor="middle" font-family="sans-serif">s={s_um}</text>
  <line x1="{signal_x + w_disp}" y1="100" x2="{gnd_right_x}" y2="100" stroke="red" stroke-width="2"></line>
  <text x="{signal_x + w_disp + s_disp/2}" y="90" font-size="14" fill="red" text-anchor="middle" font-family="sans-serif">s={s_um}</text>
  <line x1="770" y1="110" x2="770" y2="140" stroke="blue" stroke-width="2"></line>
  <text x="775" y="130" font-size="14" fill="blue" font-family="sans-serif">t={t_nm}nm</text>
</svg>
"""
st.write(svg_code, unsafe_allow_html=True)

# ==========================================
# 3. 顯示計算公式
# ==========================================
st.header("3. Formulas (n=1)")
with st.expander("點擊展開查看公式 (依照簡報定義)", expanded=True):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("**【 單位長度參數 (Basic) 】**")
        st.latex(r"C_l = 4 \varepsilon_0 \varepsilon_{eff} \frac{K(k_0)}{K(k'_0)}")
        st.latex(r"L_l = \frac{\mu_0}{4} \frac{K(k'_0)}{K(k_0)}")
        
        st.markdown("**【 DC 結果 】**")
        st.latex(r"L = \color{red}{L_l l}")
        st.latex(r"C = \color{red}{C_l l}")
        
    with col_f2:
        st.markdown("**【 AC 結果 (等效集總參數 Lumped Element) 】**")
        st.latex(r"L_n = \frac{2}{n^2\pi^2} L_l l \xrightarrow{n=1} \frac{2}{\pi^2} L_{DC}")
        st.latex(r"C = \frac{C_l l}{2} = \frac{C_{DC}}{2}")
        st.latex(r"f_{res} = \frac{1}{2\pi \sqrt{L_n C}}")

# ==========================================
# 4. 執行計算與顯示結果
# ==========================================
st.header("4. Calculation Results")

if st.button("Calculate", type="primary"):
    # 單位轉換為公尺
    w = w_um * 1e-6
    s = s_um * 1e-6
    h = h_um * 1e-6
    l = l_mm * 1e-3
    
    # 計算橢圓積分比例
    k0 = w / (w + 2 * s)
    k0_prime = np.sqrt(1 - k0**2)
    
    K_k0 = ellipk(k0**2)
    K_k0_prime = ellipk(k0_prime**2)
    
    # 有效介電常數 (使用最純粹的共平面近似法 Eeff = (Er+1)/2，以對齊簡報結果)
    eeff = (er + 1.0) / 2.0
    
    # 單位長度結果 (Basic / TL)
    C_l = 4 * EPSILON_0 * eeff * (K_k0 / K_k0_prime)
    L_l = (MU_0 / 4) * (K_k0_prime / K_k0)
    
    # 阻抗與波速
    Z0 = np.sqrt(L_l / C_l)
    v_phase = 1 / np.sqrt(L_l * C_l)
    v_ratio = v_phase / C_SPEED
    
    # DC 結果 (純粹乘上總長度 l)
    C_dc = C_l * l
    L_dc = L_l * l

    # AC 等效集總參數 (Lumped Element, n=1)
    C_eq = C_dc / 2.0
    L_eq = (2.0 / (np.pi**2)) * L_dc
    
    # 共振頻率
    f_res = 1 / (2 * np.pi * np.sqrt(L_eq * C_eq))
    
    # === 畫面佈局 (使用自訂函數 format_eng 自動調整單位) ===
    res_unit, res_dc, res_ac = st.columns(3)
    
    with res_unit:
        st.info("### Basic (單位長度)")
        st.metric(label="ε_eff", value=f"{eeff:.4f}")
        st.metric(label="C_l", value=format_eng(C_l, "F/m"))
        st.metric(label="L_l", value=format_eng(L_l, "H/m"))
        st.metric(label="Z0", value=f"{Z0:.2f} Ω")
        st.metric(label="v (波速)", value=f"{v_ratio:.4f} c")
        
    with res_dc:
        st.warning("### DC (總參數)")
        st.metric(label="C = C_l * l", value=format_eng(C_dc, "F"))
        st.metric(label="L = L_l * l", value=format_eng(L_dc, "H"))
        
    with res_ac:
        st.success("### AC (Lumped, n=1)")
        st.metric(label="C_n = C_DC / 2", value=format_eng(C_eq, "F"))
        st.metric(label="L_n = (2/π²) * L_DC", value=format_eng(L_eq, "H"))
        st.metric(label="Resonance Freq (f_res)", value=format_eng(f_res, "Hz"))