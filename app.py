import streamlit as st

# Function to determine button color based on status (optional for clarity)
def get_button_color(status):
    if status == "Baik":
        return "green"
    elif status == "Rusak":
        return "red"
    else:
        return "gray"  # Default color

# Main function
def main():
    # Define CSS classes for button styles (optional, but recommended for visual reference)
    st.write('<style>')
    st.write('.btn-default { background-color: #ddd; color: black; padding: 10px 20px; border: none; border-radius: 5px; }')
    st.write('.btn-green { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }')
    st.write('.btn-red { background-color: red; color: white; padding: 10px 20px; border: none; border-radius: 5px; }')
    st.write('</style>')

    # ... (your initial app logic here) ...

    # Button creation with clear and concise variable names
    current_status = "Baik"  # Replace with your initial status logic
    button_text = f"Ubah ke {('Rusak' if current_status == 'Baik' else 'Baik')}"
    button_color = get_button_color(current_status)  # Or directly assign a color string

    button = st.button(button_text, key=f"ubah_status_{i}", css_class=button_color)  # Using css_class for styling

    # ... (your button handling logic here, including updating status) ...

if __name__ == "__main__":
    main()
