import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd

# Contoh DataFrame
df = pd.DataFrame({
    'Nama': ['Alice', 'Bob', 'Charlie'],
    'Usia': [24, 27, 22]
})

# Membuat GridOptionsBuilder
gb = GridOptionsBuilder.from_dataframe(df)

# Menambahkan kolom tombol tambah
string_to_add_row = """
function(e) { 
    let api = e.api; 
    let rowIndex = e.rowIndex + 1; 
    api.applyTransaction({addIndex: rowIndex, add: [{}]}); 
};
"""
cell_button_add = JsCode('''
    class BtnAddCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
             <span>
                <style>
                .btn_add {
                  background-color: limegreen;
                  border: none;
                  color: white;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 10px;
                  font-weight: bold;
                  height: 2.5em;
                  width: 8em;
                  cursor: pointer;
                }

                .btn_add:hover {
                  background-color: #05d588;
                }
                </style>
                <button id='click-button' 
                    class="btn_add" 
                    >&#x2795; Add</button>
             </span>
          `;
        }

        getGui() {
            return this.eGui;
        }

    };
''')
gb.configure_column('', headerTooltip='Klik untuk menambahkan baris baru', editable=False, filter=False,
                    onCellClicked=JsCode(string_to_add_row), cellRenderer=cell_button_add,
                    autoHeight=True, wrapText=True, lockPosition='left')

# Menambahkan kolom tombol hapus
string_to_delete = """
function(e) { 
    let api = e.api; 
    let sel = api.getSelectedRows(); 
    api.applyTransaction({remove: sel}); 
};
"""
cell_button_delete = JsCode('''
    class BtnCellRenderer {
        init(params) {
            console.log(params.api.getSelectedRows());
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
             <span>
                <style>
                .btn {
                  background-color: #F94721;
                  border: none;
                  color: white;
                  font-size: 10px;
                  font-weight: bold;
                  height: 2.5em;
                  width: 8em;
                  cursor: pointer;
                }

                .btn:hover {
                  background-color: #FB6747;
                }
                </style>
                <button id='click-button'
                    class="btn"
                    >&#128465; Delete</button>
             </span>
          `;
        }

        getGui() {
            return this.eGui;
        }

    };
''')
gb.configure_column('Delete', headerTooltip='Klik untuk menghapus baris', editable=False, filter=False,
                    onCellClicked=JsCode(string_to_delete), cellRenderer=cell_button_delete,
                    autoHeight=True, suppressMovable='true')

# Mengatur grid
grid_options = gb.build()

# Menampilkan grid
AgGrid(df, gridOptions=grid_options, enable_enterprise_modules=True)

st.title("Tabel dengan Tombol Tambah dan Hapus")
