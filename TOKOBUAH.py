import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Function to calculate sales metrics including weekly averages
def calculate_metrics(sales_df):
    fruits = sales_df.columns[1:]  # Exclude date column
    metrics = {
        'Buah': [],
        'Total Penjualan (kg)': [],
        'Rata-rata Harian (kg)': [],
        'Rata-rata Mingguan (kg)': [],
        'ROP (kg)': [],
        'EOQ (kg)': [],
        'Status Stok': []
    }
    
    for fruit in fruits:
        daily_avg = sales_df[fruit].mean()
        weekly_avg = daily_avg * 7  # Convert daily to weekly
        total_sales = sales_df[fruit].sum()
        
        # Calculate ROP and EOQ (will be calculated properly in detailed view)
        rop = 2 * daily_avg  # Default 2 days lead time
        eoq = 0  # Will be calculated with user inputs later
        
        metrics['Buah'].append(fruit)
        metrics['Total Penjualan (kg)'].append(total_sales)
        metrics['Rata-rata Harian (kg)'].append(daily_avg)
        metrics['Rata-rata Mingguan (kg)'].append(weekly_avg)
        metrics['ROP (kg)'].append(round(rop, 2))
        metrics['EOQ (kg)'].append("-")  # Placeholder for main table
        
        # Stock status example
        current_stock = total_sales / len(sales_df) * 3  # Example calculation
        metrics['Status Stok'].append("🚨 Perlu Reorder" if current_stock < rop else "🟢 Aman")
    
    return pd.DataFrame(metrics)

# Page configuration
st.set_page_config(layout="wide", page_title="Analisis Penjualan Buah per kg")

# Custom CSS styling
st.markdown("""
<style>
.header {
    padding: 20px;
    background-color: #4B0082;
    border-radius: 10px;
    color: white;
    margin-bottom: 20px;
}
.metric-card {
    padding: 15px;
    border-radius: 10px;
    background-color: #F0F0F0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
.fruit-selector {
    background-color: #E6E6FA;
    padding: 10px;
    border-radius: 5px;
}
.graph-container {
    padding: 15px;
    background-color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<div class="header"><h1>📊 Analisis Penjualan Buah (per kg)</h1></div>', unsafe_allow_html=True)

# Initialize or load sales data
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(columns=['Tanggal', 'Apel', 'Pisang', 'Anggur', 'Stroberi', 'Mangga', 'Jeruk'])

# Create tabs for input and analysis
tab1, tab2 = st.tabs(["📝 Input Data Penjualan", "📈 Analisis & Persediaan"])

# Sales input tab
with tab1:
    st.markdown("### Input Data Penjualan Harian (kg)")
    
    # Input date
    sale_date = st.date_input("Tanggal Penjualan", datetime.today(), key='sale_date')
    
    # Input sales by fruit - using kg units
    st.markdown("**Jumlah Terjual** (kg)")
    cols = st.columns(3)
    
    with cols[0]:
        apel = st.number_input("Apel", min_value=0.0, step=0.1, format="%.2f", key='apel')
        pisang = st.number_input("Pisang", min_value=0.0, step=0.1, format="%.2f", key='pisang')
    with cols[1]:
        anggur = st.number_input("Anggur", min_value=0.0, step=0.1, format="%.2f", key='anggur')
        stroberi = st.number_input("Stroberi", min_value=0.0, step=0.1, format="%.2f", key='stroberi')
    with cols[2]:
        mangga = st.number_input("Mangga", min_value=0.0, step=0.1, format="%.2f", key='mangga')
        jeruk = st.number_input("Jeruk", min_value=0.0, step=0.1, format="%.2f", key='jeruk')
    
    # Save button
    if st.button("Simpan Data Penjualan", type='primary', key='save_sales'):
        new_row = {
            'Tanggal': sale_date,
            'Apel': apel,
            'Pisang': pisang,
            'Anggur': anggur,
            'Stroberi': stroberi,
            'Mangga': mangga, 
            'Jeruk': jeruk
        }
        
        st.session_state.sales_data = pd.concat([
            st.session_state.sales_data,
            pd.DataFrame([new_row])
        ], ignore_index=True)
        
        st.success("Data penjualan berhasil disimpan!")
    
    # Show sales history
    st.markdown("### Riwayat Penjualan")
    if not st.session_state.sales_data.empty:
        st.dataframe(st.session_state.sales_data.sort_values('Tanggal', ascending=False))
    else:
        st.info("Belum ada data penjualan yang diinput.")

# Analysis tab
with tab2:
    if not st.session_state.sales_data.empty:
        # Calculate metrics
        metrics_df = calculate_metrics(st.session_state.sales_data)
        metrics_df = metrics_df.sort_values('Total Penjualan (kg)', ascending=False)
        
        # Top selling fruit
        st.markdown("### 🏆 Buah Terlaris (dalam kg)")
        top_fruit = metrics_df.iloc[0]
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color:#F1FAEE;">🥇 {top_fruit['Buah']}</h3>
                <p>Total Penjualan: <b>{round(top_fruit['Total Penjualan (kg)'], 1)} kg</b></p>
                <p>Rata-rata Harian: <b>{round(top_fruit['Rata-rata Harian (kg)'], 1)} kg/hari</b></p>
                <p>Rata-rata Mingguan: <b>{round(top_fruit['Rata-rata Mingguan (kg)'], 1)} kg/minggu</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Sales comparison chart
        st.markdown("### 📊 Perbandingan Penjualan (kg)")
        fig, ax = plt.subplots(figsize=(10, 5))
        metrics_df.sort_values('Total Penjualan (kg)', ascending=True).plot(
            x='Buah', y='Total Penjualan (kg)', kind='barh', ax=ax, color='#9370DB')
        ax.set_title('Total Penjualan per Jenis Buah (kg)')
        ax.set_xlabel('Jumlah Terjual (kg)')
        st.pyplot(fig, use_container_width=True)
        
        # Inventory analysis table
        st.markdown("### 📊 Analisis Persediaan")
        st.dataframe(metrics_df[['Buah', 'Rata-rata Harian (kg)', 'Rata-rata Mingguan (kg)', 
                         'ROP (kg)', 'Status Stok']])
        
        # Advanced EOQ calculator
        st.markdown("""
        <div class="fruit-selector">
            <h3>🧮 Kalkulator EOQ (per minggu)</h3>
            <p>Hitung jumlah pesanan ekonomis mingguan berdasarkan data penjualan aktual</p>
        </div>
        """, unsafe_allow_html=True)
        
        selected_fruit = st.selectbox("Pilih Buah:", metrics_df['Buah'].values)
        
        if selected_fruit:
            fruit_data = metrics_df[metrics_df['Buah'] == selected_fruit].iloc[0]
            
            with st.expander("Parameter Perhitungan", expanded=True):
                cols = st.columns(2)
                with cols[0]:
                    lead_time = st.number_input("Lead Time (hari)", min_value=1, value=2, 
                                              key=f'lead_{selected_fruit}')
                    ordering_cost = st.number_input("Biaya Pemesanan (Rp)", min_value=1000, 
                                                  value=10000, step=1000)
                    st.markdown(f"**Permintaan Mingguan:** {round(fruit_data['Rata-rata Mingguan (kg)'], 1)} kg")
                with cols[1]:
                    holding_cost = st.number_input("Biaya Penyimpanan (Rp/kg/minggu)", 
                                                 min_value=100, value=3500, step=100)
                    st.markdown(f"**ROP Saat Ini:** {round(fruit_data['ROP (kg)'], 1)} kg")
                
                # Calculate weekly EOQ
                weekly_demand = fruit_data['Rata-rata Mingguan (kg)']
                eoq = np.sqrt((2 * weekly_demand * ordering_cost) / holding_cost)
                eoq_rounded = round(eoq, 1)
                
                # Calculate new ROP based on daily usage and lead time
                daily_demand = fruit_data['Rata-rata Harian (kg)']
                new_rop = daily_demand * lead_time
                
                st.markdown("### Hasil Perhitungan")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Economic Order Quantity (EOQ)", f"{eoq_rounded} kg/minggu")
                with col2:
                    st.metric("Reorder Point (ROP)", f"{round(new_rop, 1)} kg")
                
                # Stock level visualization
                st.markdown("### 📊 Proyeksi Level Stok")
                days = np.arange(0, 21)  # 3 weeks
                stock_levels = np.maximum(0, eoq - daily_demand * days)
                
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(days, stock_levels, label='Level Stok', color='#4B0082')
                ax.axhline(new_rop, color='red', linestyle='--', label='ROP')
                ax.fill_between(days, 0, new_rop, color='red', alpha=0.1, label='Zona Reorder')
                ax.set_title(f'Proyeksi Stok {selected_fruit}')
                ax.set_xlabel('Hari')
                ax.set_ylabel('Jumlah Stok (kg)')
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig, use_container_width=True)
    else:
        st.warning("Silakan input data penjualan terlebih dahulu di tab Input Data Penjualan")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center; color:#666;'> TUGAS UAS MATEMATIKA PEMINATAN - by aufa iqbal rizally</div>", 
            unsafe_allow_html=True)
