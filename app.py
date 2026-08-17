import streamlit as st
import numpy as np
from scipy.special import ellipk

# 定義物理常數
EPSILON_0 = 8.8541878128e-12  # F/m
MU_0 = 4 * np.pi * 1e-7       # H/m
C = 299792458                 # m/s

# 常見基板材質字典 (Epsilon_r)
SUBSTRATES = {
    "Vacuum / Air": 1.0,
    "Teflon (PTFE)": 2.1,
    "Rogers RO4003C": 3.38,
    "FR4": 4.4,
    "Sapphire": 9.4,
    "Alumina": 9.9,
    "Silicon": 11.8,
    "GaAs": 12.9,
    "Custom": 0.0  # 選擇此項會顯示手動輸入框
}

st.set_page_config(page_title="CPW Calculator", layout="centered")

st.title("Coplanar Waveguide (CPW) Calculator")
st.markdown("計算共平面波導的等效電感 (Ll) 與等效電容 (Cl)")

st.header("1. Substrate Parameters")
col1, col2 = st.columns(2)

with col1:
    material = st.selectbox("Dielectric Material", list(SUBSTRATES.keys()), index=6) # 預設選 Silicon

with col2:
    if material == "Custom":
        epsilon_r = st.number_input("Custom Dielectric Constant (εr)", min_value=1.0, value=10.0, step=0.1)
    else:
        epsilon_r = st.number_input("Dielectric Constant (εr)", value=SUBSTRATES[material], disabled=True)

# 簡化版的有效介電常數估算 (假設基板夠厚)
epsilon_eff_default = (epsilon_r + 1) / 2
epsilon_eff = st.number_input("Effective Dielectric Constant (ε_eff)", value=epsilon_eff_default, help="預設使用無限厚基板近似值，您也可以手動修改")

st.header("2. Geometry Parameters")
col3, col4 = st.columns(2)

with col3:
    w_um = st.number_input("Signal Width (w) [μm]", min_value=0.1, value=10.0, step=1.0)
with col4:
    s_um = st.number_input("Gap to Ground (s) [μm]", min_value=0.1, value=6.0, step=1.0)

# 執行計算
st.header("3. Calculation Results")

if st.button("Calculate Cl & Ll", type="primary"):
    # 將 μm 轉換為 SI 單位 (這裡計算 k0 為比例，單位不影響，但保持良好習慣)
    w = w_um * 1e-6
    s = s_um * 1e-6
    
    # 計算幾何比例
    k0 = w / (w + 2 * s)
    k0_prime = np.sqrt(1 - k0**2)
    
    # 使用 scipy 計算第一類完全橢圓積分
    # 注意：scipy.special.ellipk(m) 的輸入參數 m = k^2
    K_k0 = ellipk(k0**2)
    K_k0_prime = ellipk(k0_prime**2)
    
    # 計算 Ll 與 Cl
    C_l = 4 * EPSILON_0 * epsilon_eff * (K_k0 / K_k0_prime)
    L_l = (MU_0 / 4) * (K_k0_prime / K_k0)
    
    # 計算傳輸線特徵阻抗 (Z0) 與 相位速度 (v) 作為額外參考
    Z0 = np.sqrt(L_l / C_l)
    v = 1 / np.sqrt(L_l * C_l)
    
    st.success("Calculation Successful!")
    
    # 顯示結果
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.metric(label="Equivalent Capacitance (Cl)", value=f"{C_l:.3e} F/m")
        st.metric(label="Equivalent Inductance (Ll)", value=f"{L_l:.3e} H/m")
        
    with res_col2:
        st.metric(label="Characteristic Impedance (Z0)", value=f"{Z0:.2f} Ω")
        st.metric(label="Phase Velocity (v)", value=f"{v/C:.4f} c")
        
    # 顯示中間變數檢查
    with st.expander("Show intermediate variables (K, k0)"):
        st.write(f"- k0 = {k0:.4f}")
        st.write(f"- k'0 = {k0_prime:.4f}")
        st.write(f"- K(k0) = {K_k0:.4f}")
        st.write(f"- K(k'0) = {K_k0_prime:.4f}")