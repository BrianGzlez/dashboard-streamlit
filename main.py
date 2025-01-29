import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data using st.cache_data
@st.cache_data
def load_data():
    df = pd.read_excel('data.xlsx')
    return df


# Button for navigation
page = st.radio("Go to", ["Dashboard", "Instructions"], horizontal=True)

# Load the dataset
df = load_data()

# Convert 'Created At' column to datetime and remove timezone information
df['Created At'] = pd.to_datetime(df['Created At'], errors='coerce').dt.tz_localize(None)

# Apply filters based on user selection
if page == "Dashboard":
    # Filters for the general section in the sidebar
    st.sidebar.header("Filters")

    case_status_filter = st.sidebar.multiselect(
        "Select Case Status", 
        df['Case Status'].unique(), 
        default=df['Case Status'].unique()
    )

    assignee_filter = st.sidebar.multiselect(
        "Select Assignees", 
        df['Assignee Name'].dropna().unique(), 
        default=[df['Assignee Name'].dropna().unique()[0]]  # Default to first assignee
    )

    check_type_filter = st.sidebar.multiselect(
        "Select Check Type", 
        df['Check Type'].unique(), 
        default=df['Check Type'].unique()
    )

    # Date range filters in the sidebar
    start_date = st.sidebar.date_input("Start Date", df['Created At'].min())
    end_date = st.sidebar.date_input("End Date", df['Created At'].max())

    # Ensure that the date filters are of datetime type
    start_date = pd.to_datetime(start_date).normalize()
    end_date = pd.to_datetime(end_date).normalize()

    # Filter the data based on the selected filters
    df_filtered = df[
        df['Case Status'].isin(case_status_filter) & 
        df['Assignee Name'].isin(assignee_filter) & 
        df['Check Type'].isin(check_type_filter) & 
        (df['Created At'] >= start_date) & 
        (df['Created At'] <= end_date)
    ]

    # Group data by month (using year and month)
    df_filtered['Month'] = df_filtered['Created At'].dt.to_period('M')  # Create a period column for month
    df_monthly = df_filtered.groupby(['Month', 'Assignee Name']).size().reset_index(name='Case Count')

    # KPI Calculations for Case Status (counts based on filtered data)
    case_status_count = df_filtered['Case Status'].value_counts()

    # Display KPIs for case status (Open, Approved, Rejected, Total)
   
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        open_cases = case_status_count.get('open', 0)  # Count Open cases
        st.markdown(f"<h3 style='text-align: center; color: #FFC107;'>Open Cases</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #FFC107;'>{open_cases}</h2>", unsafe_allow_html=True)
        
    with col2:
        approved_cases = case_status_count.get('approved', 0)  # Count Approved cases
        st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>Approved Cases</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #4CAF50;'>{approved_cases}</h2>", unsafe_allow_html=True)
        
    with col3:
        rejected_cases = case_status_count.get('rejected', 0)  # Count Rejected cases
        st.markdown(f"<h3 style='text-align: center; color: #F44336;'>Rejected Cases</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #F44336;'>{rejected_cases}</h2>", unsafe_allow_html=True)
    with col4:
        total_cases = df_filtered.shape[0]
        st.markdown(f"<h3 style='text-align: center; color: #000000;'>Total Cases</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #000000;'>{total_cases}</h2>", unsafe_allow_html=True)
  

    # Bar chart for cases by month
    fig, ax = plt.subplots(figsize=(10, 6))

    # Pivot data for plotting
    df_pivot = df_monthly.pivot(index='Month', columns='Assignee Name', values='Case Count').fillna(0)

    # Plot the bar chart
    df_pivot.plot(kind='bar', stacked=False, ax=ax, figsize=(10, 6))

    # Add labels on the bars
    for p in ax.patches:
        ax.annotate(str(int(p.get_height())), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    fontsize=10, color='black', xytext=(0, 5), textcoords='offset points')

    plt.xticks(rotation=45)
    plt.xlabel('Month')
    plt.ylabel('Number of Cases')
    plt.title('Monthly Case Distribution by Assignee')

    st.pyplot(fig)

    # Case Breakdown by Assignee Name and Case Status
    st.subheader("Case Breakdown by Assignee Name and Case Status")
    
    # Grouping by Assignee Name and Case Status for breakdown
    df_case_status = df_filtered.groupby(['Assignee Name', 'Case Status']).size().unstack(fill_value=0)

    # Add Grand Total row
    df_case_status['Grand Total'] = df_case_status.sum(axis=1)
    df_case_status.loc['Grand Total'] = df_case_status.sum()

    # Display the grouped table
    st.write(df_case_status)


elif page == "Instructions":
    st.header("Instructions")
    st.write("""
    ### How to Use the Dashboard

    This dashboard allows you to analyze case data over time, segmented by different factors such as **Case Status**, **Assignees**, and **Check Types**.

    #### 1. **Filters Section** (Sidebar):
    - **'Case Status'**: Select one or more case statuses to filter the cases for analysis.
    - **'Assignees'**: Choose one or more assignees to analyze their individual cases. You can select up to three assignees.
    - **'Check Type'**: Filter by the type of checks. You can select multiple check types to view.
    - **'Date Range'**: Use the start and end date filters to specify the period of time you want to analyze. The dashboard will update automatically based on these filters.

    #### 2. **Data Visualization** (Main Dashboard):
    - **Monthly Case Breakdown**: A bar chart is displayed showing the number of cases for each month. Each bar represents a different assignee (if selected), and the height of the bar indicates the total number of cases for that month.
    - **Interactive Features**: Hover over the bars in the graph to view the exact count of cases for each assignee in a specific month. The table below also provides a detailed breakdown of cases by Case Status.

    #### 3. **Data Summary**:
    - The table below the graph aggregates the data by case status, providing a clear overview of the distribution of cases across different categories.

    Use this dashboard to gain valuable insights into case performance over time.
    """)
