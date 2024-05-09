import streamlit as st
import sys
import os

# Menambahkan path folder login agar Python bisa menemukan login.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'login'))

# Import login.py sebagai modul
import login

# Jalankan aplikasi login
login.main()
