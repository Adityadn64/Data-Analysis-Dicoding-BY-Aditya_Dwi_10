import os
import rembg
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

# Atur Streamlit dengan Always Rerun dan Run On Save
st.set_page_config(layout="wide", 
                   initial_sidebar_state="expanded",  # Sidebar selalu terbuka
                   page_title="Bike Sharing Analysis", 
                   page_icon=":bike:")

st.set_option('deprecation.showPyplotGlobalUse', False)

st.title('Bike Sharing Analysis')

# Load dataset
df_day = pd.read_csv('Dataset_Cleaned/day_cleaned.csv')

# Sidebar untuk input filter tanggal
img_path = 'Asset/Bike_Sharing.png'

def remove_bg(img_path):
    # Check if the processed image already exists
    processed_img_path = 'Asset/Bike_Sharing_Removed.png'
    if not os.path.exists(processed_img_path):
        # Load image as bytes
        with open(img_path, "rb") as f:
            img_bytes = f.read()

        # Remove background
        img_bytes = rembg.remove(img_bytes)

        # Save processed image
        with open(processed_img_path, 'wb') as f:
            f.write(img_bytes)

    return processed_img_path

with st.sidebar:
    st.image(image=remove_bg(img_path), caption='Bike Sharing Analysis', use_column_width=True, channels='RGBA', width=1/100)

    st.header('Filter Tanggal')
        
    # Input date range
    start_date, end_date = st.date_input('Pilih rentang tanggal',
                                                value=(pd.to_datetime('2011-01-01'), pd.to_datetime('2012-12-31')),
                                                min_value=pd.to_datetime('2011-01-01'),
                                                max_value=pd.to_datetime('2012-12-31'))

    # Tambahkan tombol reset
    if st.button('Reset Tanggal'):
        start_date = pd.to_datetime('2011-01-01')
        end_date = pd.to_datetime('2012-12-31')

    # Filter data berdasarkan input tanggal
    df_day['dateday'] = pd.to_datetime(df_day['dateday'])
    filtered_df = df_day[(df_day['dateday'] >= pd.Timestamp(start_date)) & (df_day['dateday'] <= pd.Timestamp(end_date))]

    # Tampilkan data yang difilter di sidebar
    st.dataframe(filtered_df.head(), use_container_width=True)

    def st_download_button(datasets):
        for label, data, file_name in datasets:
            if st.download_button(label=label, data=data.to_csv(index=False).encode('utf-8'), file_name=file_name):
                st.info(f"Nama File: {file_name}")
                st.success("Berhasil Download")

    st_download_button([
        ('Download Semua Dataset', df_day, 'Bike_Sharing_Day_Cleaned_By_All_Dataset.csv'),
        ('Download Dataset Berdasarkan Tanggal', filtered_df, 'Bike_Sharing_Day_Cleaned_By_Date_Dataset.csv')
    ])

# Cek apakah ada data yang tersedia setelah filter
if filtered_df.empty:
    st.error("Tidak ada data yang tersedia untuk rentang tanggal yang dipilih.")
else:
    st.markdown('### Total (Sharing Biker, Registered, Casual)')

    # Total peminjaman sepeda
    total_sharing = filtered_df['count'].sum()
    total_registered = filtered_df['registered'].sum()
    total_casual = filtered_df['casual'].sum()

    # Menyimpan data total sharing dalam bentuk dataframe
    total_df = pd.DataFrame({
        'Category': ['Total Sharing Biker', 'Total Registered', 'Total Casual'],
        'Count': [total_sharing, total_registered, total_casual]
    })

    # Display total sharing as dataframe
    st.write("Total Sharing Summary:")
    st.dataframe(total_df, use_container_width=True, hide_index=True)

    # Persebaran peminjaman sepeda berdasarkan musim
    st.markdown('### Persebaran Peminjaman Sepeda berdasarkan Musim')

    # Visualisasi menggunakan seaborn
    plt.figure(figsize=(10, 6))
    sns.barplot(x='season', y='count', data=filtered_df, palette='viridis')
    plt.title('Persebaran Peminjaman Sepeda berdasarkan Musim')
    plt.xlabel('Musim')
    plt.ylabel('Jumlah Peminjaman')
    plt.xticks(rotation=45)
    st.pyplot()

    # Deskripsi statistik berdasarkan musim
    st.write("\nDeskripsi statistik berdasarkan musim:")
    st.dataframe(filtered_df.groupby('season')['count'].describe(), use_container_width=True)

    # Kesimpulan berdasarkan persebaran musim
    st.markdown("""
    ### Kesimpulan:

    Secara keseluruhan, musim gugur (Fall) memiliki jumlah peminjaman sepeda tertinggi, diikuti oleh musim panas (Summer) dan musim dingin (Winter). Musim semi (Spring) memiliki jumlah peminjaman sepeda terendah. Variabilitas jumlah peminjaman juga cukup tinggi di semua musim, dengan beberapa pencilan yang menunjukkan hari-hari dengan jumlah peminjaman yang sangat rendah atau sangat tinggi.
    """)

    # Korelasi Suhu dan Kelembaban dengan Jumlah Peminjaman Sepeda
    st.markdown('### Korelasi Suhu dan Kelembaban dengan Jumlah Peminjaman Sepeda')

    # Visualisasi menggunakan scatter plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='temp', y='count', data=filtered_df, hue='humidity', palette='coolwarm', size='humidity', sizes=(20, 200))
    plt.title('Korelasi Suhu dan Kelembaban dengan Jumlah Peminjaman Sepeda')
    plt.xlabel('Suhu (Celsius)')
    plt.ylabel('Jumlah Peminjaman')
    plt.legend(title='Kelembaban', loc='upper left')
    st.pyplot()

    # Deskripsi statistik korelasi suhu dan kelembaban
    st.write("\nDeskripsi statistik korelasi antara suhu dan kelembaban dengan jumlah peminjaman sepeda:")
    st.dataframe(filtered_df.groupby('humidity')['count'].describe(), use_container_width=True)

    # Kesimpulan korelasi
    st.markdown("""
    ### Kesimpulan:

    Dilihat dari scatter plot ini menunjukkan bahwa suhu memiliki korelasi positif yang signifikan dengan jumlah peminjaman sepeda, dan kelembaban juga tampaknya memiliki pengaruh tetapi mungkin tidak sekuat suhu.
    """)

    # Define bins for temperature
    st.markdown('### Clustering Analysis:')

    bins = [0, 1, 2, 3, 4]
    labels = ['Fail', 'Spring', 'Summer', 'Winter']

    # Create a new column 'temp_category' based on temperature bins
    filtered_df['temp_category'] = pd.cut(filtered_df['temp'], bins=bins, labels=labels)

    # Group by 'temp_category' and calculate mean count
    clustered_data = filtered_df.groupby('temp_category')['count'].mean().reset_index()

    # Visualize clusters
    plt.figure(figsize=(10, 6))
    plt.bar(clustered_data['temp_category'], clustered_data['count'], color='skyblue')
    plt.xlabel('Temperature Category')
    plt.ylabel('Average Number of Rentals')
    plt.title('Average Number of Rentals by Temperature Category')
    plt.xticks(rotation=45)
    plt.show()
    st.pyplot()

    # Calculate Recency (R)
    st.markdown("### RFM Analysis:")

    max_date = df_day['dateday'].max()
    df_day['Recency'] = (max_date - df_day['dateday']).dt.days

    # Calculate Frequency (F) and Monetary (M)
    rfm_data = df_day.groupby('dateday').agg({
        'count': sum,                    # Monetary (M)
        'Recency': min,                # Recency (R)
        'dateday': 'count'            # Frequency (F)
    }).rename(columns={
        'count': 'Monetary',
        'dateday': 'Frequency'
    }).reset_index()

    # Visualize RFM Analysis
    plt.figure(figsize=(12, 6))

    # Plot Recency
    plt.subplot(1, 3, 1)
    plt.hist(rfm_data['Recency'], bins=20, color='skyblue')
    plt.title('Recency')
    plt.xlabel('Days since last rental')
    plt.ylabel('Count')

    # Plot Frequency
    plt.subplot(1, 3, 2)
    plt.hist(rfm_data['Frequency'], bins=20, color='salmon')
    plt.title('Frequency')
    plt.xlabel('Number of rentals per day')
    plt.ylabel('Count')

    # Plot Monetary
    plt.subplot(1, 3, 3)
    plt.hist(rfm_data['Monetary'], bins=20, color='lightgreen')
    plt.title('Monetary')
    plt.xlabel('Total rentals per day')
    plt.ylabel('Count')

    plt.tight_layout()
    plt.show()
    st.pyplot()

# Footer
st.markdown("---")
st.markdown("© 2024 Aditya Dwi Nugraha. All Rights Reserved.")

st.markdown('My Profile:')

with st.empty():
    col1, col2 = st.columns([1,1])

    with col1:
        st.link_button(label="Github", url='https://github.com/Adityadn64/')

    with col2:
        st.link_button(label="Dicoding", url='https://www.dicoding.com/users/aditya_dwi_10/academies')
