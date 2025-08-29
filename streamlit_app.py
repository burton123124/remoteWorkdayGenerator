import streamlit as st
import calendar
import datetime
import pandas as pd

def is_working_day(date, selected_weekdays):
    """Check if this weekday is selected by the user"""
    weekday = date.weekday()  # Monday = 0, Sunday = 6
    if weekday < 5:  # Only check Monday-Friday
        return weekday in selected_weekdays
    return False  # Weekend days are never working days

def generate_working_days(selected_years, selected_months, selected_weekdays):
    """Generate working days based on selections"""
    working_days = []
    
    for year in sorted(selected_years):
        for month in sorted(selected_months):
            # Get all days in the month
            days_in_month = calendar.monthrange(year, month)[1]
            
            for day in range(1, days_in_month + 1):
                date = datetime.date(year, month, day)
                if is_working_day(date, selected_weekdays):
                    working_days.append(date.strftime("%d-%m-%Y"))
    
    return working_days

def main():
    # Page config
    st.set_page_config(
        page_title="Generator Dni Roboczych",
        page_icon="📅",
        layout="centered"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 400;
        color: #333333;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 500;
        color: #666666;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .stTextArea textarea {
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 10px;
        background-color: #ffffff;
        border: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.markdown('<h1 class="main-header">Generator Dni Roboczych</h1>', unsafe_allow_html=True)
    
    # Get current date and calculate next 2 months for defaults
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month
    
    # Calculate next 2 months
    next_months = []
    for i in range(1, 3):
        month = current_month + i
        year = current_year
        if month > 12:
            month -= 12
            year += 1
        next_months.append((year, month))
    
    # Get unique years from the next 2 months
    available_years = sorted(list(set([year for year, month in next_months])))
    default_years = available_years
    
    # Year selection
    st.markdown('<p class="section-header">Wybierz lata:</p>', unsafe_allow_html=True)
    selected_years = st.multiselect(
        "",
        options=list(range(current_year, current_year + 3)),
        default=default_years,
        key="years"
    )
    
    # Weekday selection
    st.markdown('<p class="section-header">Wybierz dni tygodnia:</p>', unsafe_allow_html=True)
    weekday_options = {
        0: 'Poniedziałek',
        1: 'Wtorek', 
        2: 'Środa',
        3: 'Czwartek',
        4: 'Piątek'
    }
    
    # Create columns for weekday checkboxes
    cols = st.columns(5)
    selected_weekdays = []
    
    for i, (weekday_num, weekday_name) in enumerate(weekday_options.items()):
        with cols[i]:
            if st.checkbox(weekday_name, value=(weekday_num == 0), key=f"weekday_{weekday_num}"):
                selected_weekdays.append(weekday_num)
    
    # Month selection
    st.markdown('<p class="section-header">Wybierz miesiące:</p>', unsafe_allow_html=True)
    
    # Select all / deselect all buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        select_all = st.button("Zaznacz wszystkie")
    with col2:
        deselect_all = st.button("Odznacz wszystkie")
    
    month_options = {
        1: 'Styczeń', 2: 'Luty', 3: 'Marzec', 4: 'Kwiecień',
        5: 'Maj', 6: 'Czerwiec', 7: 'Lipiec', 8: 'Sierpień',
        9: 'Wrzesień', 10: 'Październik', 11: 'Listopad', 12: 'Grudzień'
    }
    
    # Default selected months (next 2 months)
    next_month_numbers = [month for year, month in next_months]
    default_months = [month_options[month] for month in next_month_numbers if month in month_options]
    
    # Handle select/deselect all
    if select_all:
        default_selection = list(month_options.values())
    elif deselect_all:
        default_selection = []
    else:
        default_selection = default_months
    
    selected_month_names = st.multiselect(
        "",
        options=list(month_options.values()),
        default=default_selection,
        key="months"
    )
    
    # Convert selected month names back to numbers
    selected_months = [num for num, name in month_options.items() if name in selected_month_names]
    
    # Generate and display results
    if selected_years and selected_months and selected_weekdays:
        working_days = generate_working_days(selected_years, selected_months, selected_weekdays)
        
        st.markdown('<p class="section-header">Wygenerowane dni robocze:</p>', unsafe_allow_html=True)
        
        if working_days:
            # Display in text area
            output_text = "\n".join(working_days)
            st.text_area(
                "",
                value=output_text,
                height=300,
                key="output"
            )
            
            # Copy to clipboard button (shows the text to copy)
            st.markdown(f"**Liczba dni:** {len(working_days)}")
            
            # Download button
            st.download_button(
                label="💾 Pobierz jako plik tekstowy",
                data=output_text,
                file_name=f"dni_robocze_{datetime.date.today().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
            # Optional: Show as table
            if st.checkbox("Pokaż jako tabelę"):
                df_data = []
                for day_str in working_days:
                    date_obj = datetime.datetime.strptime(day_str, "%d-%m-%Y").date()
                    df_data.append({
                        "Data": day_str,
                        "Dzień tygodnia": weekday_options.get(date_obj.weekday(), "Weekend"),
                        "Miesiąc": month_options[date_obj.month],
                        "Rok": date_obj.year
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, hide_index=True)
        else:
            st.info("Brak dni roboczych dla wybranych kryteriów.")
    else:
        st.info("Wybierz lata, miesiące i dni tygodnia, aby wygenerować dni robocze.")

if __name__ == "__main__":
    main()
