import streamlit as st
import numpy as np
from scipy.special import ellipk

# ==========================================
# 輔助函數：工程單位自動轉換
# ==========================================
def format_eng(value, unit_type):
    if value == 0:
        return f"0.0000 {unit_type}"
    
    abs_v = abs(value)
    
    # 處理電容 (F)
    if "F" in unit_type: 
        if abs_v >= 1e-6: return f"{value*1e6:.4f} μ{unit_type}"
        elif abs_v >= 1e-9: return f"{value*1e9:.4f} n{unit_type}"
        elif abs_v >= 1e-12: return f"{value*1e12:.4f} p{unit_type}"
        elif abs_v >= 1e-15: return f"{value*1e15:.4f} f{unit_type}"
        else: return f"{value*1e18:.4f} a{unit_type}"
        
    # 處理電感 (H)
    elif "H" in unit_type:
        if abs_v >= 1e-3: return f"{value*1e3:.4f} m{unit_type}"
        elif abs_v >= 1e-6: return f"{value*1e6:.4f} μ{unit_type}"
        elif abs_v >= 1e-9: return f"{value*1e9:.4f} n{unit_type}"
        elif abs_v >= 1e-12: return f"{value*1e12:.4f} p{unit_type}"
        else: return f"{value*1e15:.4f} f{unit_type}"
        
    # 處理頻率 (Hz)
    elif "Hz" in unit_type:
        if abs_v >= 1e9: return f"{value*1e-9:.4f} GHz"
        elif abs_v >= 1e6: return f"{value*1e-6:.4f} MHz"
        elif abs_v >= 1e3: return f"{value*1e-3:.4f} kHz"
        else: return f"{value:.4f} Hz"
        
    return f"{value:.4f} {unit_type}"

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
st.markdown("精確計算共平面波導參數，並依據 **λ/2** 或 **λ/4** 類型自動推導 DC 與 AC (n=1) 等效集總參數。")

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
    # 預設厚度 500um
    h_um = st.number_input("Substrate Thickness (h) [μm]", min_value=1.0, value=500.0, step=10.0)

with col2:
    st.subheader("Cross-Section (截面幾何)")
    w_um = st.number_input("Signal Width (w) [μm]", min_value=0.1, value=10.0, step=1.0)
    s_um = st.number_input("Gap (s) [μm]", min_value=0.1, value=6.0, step=1.0)
    t_nm = st.number_input("Metal Thickness (t) [nm]", min_value=1.0, value=100.0, step=10.0)

with col3:
    st.subheader("Resonator (共振腔設定)")
    res_type = st.selectbox("Resonator Type", ["λ/2 Resonator (Open/Open or Short/Short)", "λ/4 Resonator (Open/Short)"])
    l_mm = st.number_input("CPW Length (l) [mm]", min_value=0.01, value=9.9675, step=0.1, format="%.4f")

# ==========================================
# 2. 動態視覺化 CPW 結構 (SVG)
# ==========================================
st.header("2. CPW Cross-Section (動態示意圖)")

w_disp = max(w_um, 2) * 10
s_disp = max(s_um, 2) * 10
center_x = 400
signal_x = center_x - w_disp/2
gnd_left_x = signal_x - s_disp - 200
gnd_right_x = signal_x + w_disp + s_disp

svg_code = f"""
<svg viewBox="0 0 800 250" width="100%" xmlns="http://www.w3.org/2000/svg">
  <rect x="50" y="140" width="700" height="90" fill="#e0e0e0" stroke="#333" stroke-width="2"></rect>
  <text x="400" y="195" font-size="18" text-anchor="middle" font-family="sans-serif" fill="#333">Dielectric Substrate (εr={er}), h = {h_um} μm</text>

  <rect x="50" y="110" width="{gnd_left_x + 200 - 50}" height="30" fill="#ffd700" stroke="#b8860b" stroke-width="2"></rect>
  <text x="100" y="132" font-size="16" text-anchor="middle" font-family="sans-serif" font-weight="bold">GND</text>

  <rect x="{signal_x}" y="110" width="{w_disp}" height="30" fill="#ffd700" stroke="#b8860b" stroke-width="2"></rect>
  <text x="{center_x}" y="132" font-size="16" text-anchor="middle" font-family="sans-serif" font-weight="bold">w={w_um}</text>

  <rect x="{gnd_right_x}" y="110" width="{750 - gnd_right_x}" height="30" fill="#ffd700" stroke="#b8860b" stroke-width="2"></rect>
  <text x="700" y="132" font-size="16" text-anchor="middle" font-family="sans-serif" font-weight="bold">GND</text>

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

is_lambda_2 = "λ/2" in res_type
l_coeff_str = r"\frac{2}{\pi^2}" if is_lambda_2 else r"\frac{8}{\pi^2}"

with st.expander(f"點擊展開查看 {res_type.split()[0]} 公式", expanded=True):
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
        st.latex(rf"L_n = {l_coeff_str} L_{{DC}}")
        st.latex(r"C_n = \frac{C_{DC}}{2}")
        st.latex(r"f_{res} = \frac{1}{2\pi \sqrt{L_n C_n}}")

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
    
    # 有效介電常數 (Eeff = (Er+1)/2)
    eeff = (er + 1.0) / 2.0
    
    # 單位長度結果
    C_l = 4 * EPSILON_0 * eeff * (K_k0 / K_k0_prime)
    L_l = (MU_0 / 4) * (K_k0_prime / K_k0)
    
    Z0 = np.sqrt(L_l / C_l)
    v_phase = 1 / np.sqrt(L_l * C_l)
    v_ratio = v_phase / C_SPEED
    
    # DC 結果 (總長度)
    C_dc = C_l * l
    L_dc = L_l * l

    # AC 等效集總參數
    C_eq = C_dc / 2.0
    
    if is_lambda_2:
        L_eq = (2.0 / (np.pi**2)) * L_dc
    else:
        L_eq = (8.0 / (np.pi**2)) * L_dc
        
    # 共振頻率
    f_res = 1 / (2 * np.pi * np.sqrt(L_eq * C_eq))
    
    # 畫面佈局
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
        st.success(f"### AC (Lumped, {res_type.split()[0]})")
        st.metric(label="C_n = C_DC / 2", value=format_eng(C_eq, "F"))
        
        # 顯示對應的 L_n 公式標籤
        l_label = "L_n = (2/π²) * L_DC" if is_lambda_2 else "L_n = (8/π²) * L_DC"
        st.metric(label=l_label, value=format_eng(L_eq, "H"))
        
        st.metric(label="Resonance Freq (f_res)", value=format_eng(f_res, "Hz"))