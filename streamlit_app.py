import streamlit as st
import calendar
import datetime
import pyperclip

def easter_date(year):
    """Calculate Easter date for a given year using the algorithm"""
    # Algorithm for Easter calculation
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    n = (h + l - 7 * m + 114) // 31
    p = (h + l - 7 * m + 114) % 31
    return datetime.date(year, n, p + 1)

def get_polish_holidays(year):
    """Get all Polish public holidays for a given year"""
    holidays = {}
    
    # Fixed holidays
    holidays[datetime.date(year, 1, 1)] = "Nowy Rok"
    holidays[datetime.date(year, 1, 6)] = "Święto Trzech Króli"
    holidays[datetime.date(year, 5, 1)] = "Święto Pracy"
    holidays[datetime.date(year, 5, 3)] = "Święto Konstytucji 3 Maja"
    holidays[datetime.date(year, 8, 15)] = "Wniebowzięcie NMP"
    holidays[datetime.date(year, 11, 1)] = "Wszystkich Świętych"
    holidays[datetime.date(year, 11, 11)] = "Święto Niepodległości"
    holidays[datetime.date(year, 12, 24)] = "Wigilia"  # NEW in 2025
    holidays[datetime.date(year, 12, 25)] = "Boże Narodzenie"
    holidays[datetime.date(year, 12, 26)] = "Drugi dzień Bożego Narodzenia"
    
    # Easter-based holidays
    easter = easter_date(year)
    holidays[easter] = "Wielkanoc"
    holidays[easter + datetime.timedelta(days=1)] = "Poniedziałek Wielkanocny"
    holidays[easter + datetime.timedelta(days=49)] = "Zielone Świątki"
    holidays[easter + datetime.timedelta(days=60)] = "Boże Ciało"
    
    return holidays

def is_working_day(date, selected_weekdays):
    """Check if this weekday is selected by the user"""
    weekday = date.weekday()  # Monday = 0, Sunday = 6
    if weekday < 5:  # Only check Monday-Friday
        return weekday in selected_weekdays
    return False  # Weekend days are never working days

def generate_working_days(selected_years, selected_months, selected_weekdays):
    """Generate working days based on selections"""
    if not selected_years or not selected_months or not selected_weekdays:
        return [], []
    
    working_days = []
    holiday_days = []
    
    # Get all holidays for selected years
    all_holidays = {}
    for year in selected_years:
        all_holidays.update(get_polish_holidays(year))
    
    for year in sorted(selected_years):
        for month in sorted(selected_months):
            # Get all days in the month
            days_in_month = calendar.monthrange(year, month)[1]
            
            for day in range(1, days_in_month + 1):
                date = datetime.date(year, month, day)
                if is_working_day(date, selected_weekdays):
                    date_str = date.strftime("%d-%m-%Y")
                    
                    # Check if it's a holiday
                    if date in all_holidays:
                        holiday_days.append(f"{date_str} ({all_holidays[date]})")
                    else:
                        working_days.append(date_str)
    
    return working_days, holiday_days

def main():
    # Page config
    st.set_page_config(
        page_title="Generator Dni Roboczych",
        page_icon="📅",
        layout="wide"
    )
    
    # Custom CSS for Apple-like styling
    st.markdown("""
    <style>
    .main > div {
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    .stSelectbox > div > div {
        background-color: #ffffff;
        border-radius: 5px;
    }
    h1 {
        color: #333333;
        font-family: 'Helvetica', sans-serif;
        text-align: center;
        margin-bottom: 2rem;
    }
    h3 {
        color: #555555;
        font-family: 'Helvetica', sans-serif;
        font-weight: normal;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stTextArea > div > div > textarea {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-family: 'Monaco', monospace;
        color: #333333;
        line-height: 1.4;
    }
    .stCheckbox > label {
        color: #333333;
        font-family: 'Helvetica', sans-serif;
    }
    /* Fix checkbox layout */
    div[data-testid="column"] {
        padding: 0.25rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.title("Generator Dni Roboczych")
    
    # Create main layout with three columns
    control_col, result_col, holiday_col = st.columns([1, 2, 1])
    
    with control_col:
        st.subheader("Ustawienia")
        
        # Get current date and calculate defaults
        today = datetime.date.today()
        current_year = today.year
        current_month = today.month
        
        # Calculate next 2 months (current +1 and +2)
        next_months = []
        for i in range(1, 3):
            month = current_month + i
            year = current_year
            if month > 12:
                month -= 12
                year += 1
            next_months.append((year, month))
        
        default_months = [month for year, month in next_months]
        
        # Year selection - show current year + next 2 years as checkboxes
        available_years = [current_year, current_year + 1, current_year + 2]
        
        st.write("**Wybierz lata:**")
        # Create 3 columns for year checkboxes
        year_cols = st.columns(3)
        selected_years = []
        
        for i, year in enumerate(available_years):
            with year_cols[i]:
                # Default to current year only
                checked = st.checkbox(str(year), value=(i == 0), key=f"year_{year}")
                if checked:
                    selected_years.append(year)
        
        # Weekday selection
        st.write("**Wybierz dni tygodnia:**")
        weekdays = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']
        selected_weekdays = []
        
        for i, weekday in enumerate(weekdays):
            # Default Monday (i==0) to True
            checked = st.checkbox(weekday, value=(i == 0), key=f"weekday_{i}")
            if checked:
                selected_weekdays.append(i)
        
        # Month selection
        st.write("**Wybierz miesiące:**")
        months = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                  'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
        
        # Create month checkboxes in a more compact layout
        selected_months = []
        for i in range(0, 12, 3):
            month_cols = st.columns(3)
            for j in range(3):
                if i + j < 12:
                    idx = i + j
                    with month_cols[j]:
                        # Default to next 2 months
                        is_default = (idx + 1) in default_months
                        checked = st.checkbox(months[idx], value=is_default, key=f"month_{idx}")
                        if checked:
                            selected_months.append(idx + 1)
        
        # Holiday toggle
        st.write("**Opcje:**")
        hide_holidays = st.checkbox("Ukryj dni wolne od pracy", value=True, key="hide_holidays")
        st.caption("✓ Ukryj = dni wolne tylko po prawej stronie")
        st.caption("✗ Pokaż = dni wolne w głównym oknie (czerwone)")
    
    with result_col:
        st.subheader("Wygenerowane dni robocze")
        
        # Generate working days
        working_days, holiday_days = generate_working_days(selected_years, selected_months, selected_weekdays)
        
        if working_days or holiday_days:
            # Get all holidays for display
            all_holidays_for_output = []
            if selected_years and selected_months:
                all_holidays = {}
                for year in selected_years:
                    all_holidays.update(get_polish_holidays(year))
                
                # Filter holidays by selected months
                for holiday_date, holiday_name in sorted(all_holidays.items()):
                    if holiday_date.month in selected_months:
                        date_str = holiday_date.strftime("%d-%m-%Y")
                        all_holidays_for_output.append(f"{date_str} ({holiday_name})")
            
            # Prepare output text
            if hide_holidays:
                # Only working days
                output_text = "\n".join(working_days) + "\n\n"
            else:
                # Include holidays in main output with red formatting
                output_text = "\n".join(working_days)
                if all_holidays_for_output:
                    output_text += "\n\n--- DNI WOLNE OD PRACY ---\n"
                    for holiday in all_holidays_for_output:
                        output_text += f"🔴 {holiday}\n"
                output_text += "\n"
            
            # Calculate dynamic height
            total_lines = len(working_days) + (len(all_holidays_for_output) if not hide_holidays else 0)
            text_height = max(250, min(600, total_lines * 25 + 100))
            
            st.text_area(
                "Dni robocze:",
                value=output_text,
                height=text_height,
                label_visibility="collapsed"
            )
            
            # Create two columns for buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # Copy to clipboard button
                if st.button("📋 Skopiuj do schowka", use_container_width=True):
                    copy_text = output_text.strip()
                    # JavaScript code to copy to clipboard
                    st.markdown(f"""
                    <script>
                    navigator.clipboard.writeText(`{copy_text}`).then(function() {{
                        console.log('Text copied to clipboard');
                    }});
                    </script>
                    """, unsafe_allow_html=True)
                    st.success("Skopiowane do schowka!")
            
            with col2:
                # Download button
                st.download_button(
                    label="💾 Pobierz jako TXT",
                    data=output_text.strip(),
                    file_name=f"dni_robocze_{today.strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            working_count = len(working_days)
            holiday_count = len(all_holidays_for_output)
            total_info = f"Wygenerowano {working_count} dni roboczych"
            if not hide_holidays and holiday_count > 0:
                total_info += f" i {holiday_count} dni wolnych"
            st.info(total_info + ".")
            
        else:
            st.warning("Wybierz lata, miesiące i dni tygodnia aby wygenerować dni robocze.")
    
    with holiday_col:
        st.subheader("Dni wolne od pracy")
        
        # Only show holidays in right column when toggle is ON (hiding them from main output)
        if hide_holidays:
            # Generate all holidays for selected years and months
            all_holidays_display = []
            if selected_years and selected_months:
                all_holidays = {}
                for year in selected_years:
                    all_holidays.update(get_polish_holidays(year))
                
                # Filter holidays by selected months and format for display
                for holiday_date, holiday_name in sorted(all_holidays.items()):
                    if holiday_date.month in selected_months:
                        date_str = holiday_date.strftime("%d-%m-%Y")
                        all_holidays_display.append(f"{date_str} ({holiday_name})")
            
            if all_holidays_display:
                # Calculate height for holidays column
                holiday_height = max(250, min(600, len(all_holidays_display) * 25 + 100))
                
                # Display all holidays in red
                holiday_text = ""
                for holiday in all_holidays_display:
                    holiday_text += f"🔴 {holiday}\n"
                holiday_text += "\n"
                
                st.text_area(
                    "Dni wolne:",
                    value=holiday_text,
                    height=holiday_height,
                    label_visibility="collapsed"
                )
            else:
                st.write("Brak dni wolnych w wybranych miesiącach.")
        else:
            # When toggle is OFF, right column is empty (holidays moved to main output)
            st.write("*(Dni wolne przeniesione do głównego okna)*")
            st.text_area(
                "Puste:",
                value="",
                height=250,
                label_visibility="collapsed",
                disabled=True
            )

if __name__ == "__main__":
    main()
