import streamlit as st

# Baris nama kolom
kolom = ["Kolom 1", "Kolom 2", "Kolom 3", "Kolom 4", "Kolom 5", "Kolom 6", "Kolom 7", "Kolom 8", "Kolom 9"]
st.write(kolom)

# Baris data
for i in range(5):
    kolom1, kolom2, kolom3, kolom4, kolom5, kolom6, kolom7, kolom8, kolom9 = st.columns(9)
    with kolom1:
        st.write("Data 1")
    with kolom2:
        st.write("Data 2")
    with kolom3:
        st.button("Tombol 3", key=f"btn_{i}")
    with kolom4:
        st.write("Data 4")
    with kolom5:
        st.write("Data 5")
    with kolom6:
        st.button("Tombol 6", key=f"btn_{i}")
    with kolom7:
        st.write("Data 7")
    with kolom8:
        st.write("Data 8")
    with kolom9:
        st.button("Tombol 9", key=f"btn_{i}")
