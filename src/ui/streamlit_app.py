"""Streamlit web interface for Email Unsubscribe Automation"""
import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.config import Config
from src.utils.logger import setup_logging
from src.database.models import Database
from src.core.orchestrator import EmailUnsubscribeOrchestrator


# Page configuration
st.set_page_config(
    page_title="Email Unsubscribe Automation",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if "config" not in st.session_state:
        st.session_state.config = Config()
    
    if "db" not in st.session_state:
        st.session_state.db = None
    
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None
    
    if "credentials_verified" not in st.session_state:
        st.session_state.credentials_verified = False
    
    if "scan_results" not in st.session_state:
        st.session_state.scan_results = None


def sidebar_navigation():
    """Render sidebar navigation"""
    st.sidebar.title("📧 Email Unsubscribe")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Email Scanner", "Unsubscribe Manager", "Whitelist/Blacklist", 
         "Settings", "Statistics", "Operation History"]
    )
    
    st.sidebar.markdown("---")
    
    # Connection status
    if st.session_state.credentials_verified:
        st.sidebar.success("✅ Connected")
    else:
        st.sidebar.warning("⚠️ Not Connected")
    
    return page


def settings_page():
    """Settings and configuration page"""
    st.markdown('<p class="main-header">⚙️ Settings</p>', unsafe_allow_html=True)
    
    st.markdown("### Email Configuration")
    
    with st.form("credentials_form"):
        email = st.text_input(
            "Email Address",
            value=st.session_state.config.email_address or "",
            help="Your Gmail address"
        )
        
        password = st.text_input(
            "App-Specific Password",
            type="password",
            help="Your Gmail app-specific password (not your regular password)"
        )
        
        imap_server = st.text_input(
            "IMAP Server",
            value=st.session_state.config.imap_server,
            help="IMAP server address (default: imap.gmail.com)"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submitted = st.form_submit_button("Save & Test Connection")
        
        if submitted:
            if email and password:
                # Update configuration
                st.session_state.config.set_credentials(email, password)
                os.environ["IMAP_SERVER"] = imap_server
                
                # Test connection
                try:
                    from src.core.email_manager import EmailManager
                    
                    with st.spinner("Testing connection..."):
                        manager = EmailManager(email, password, imap_server)
                        if manager.connect():
                            st.session_state.credentials_verified = True
                            
                            # Initialize database and orchestrator
                            st.session_state.db = Database(st.session_state.config.database_path)
                            st.session_state.orchestrator = EmailUnsubscribeOrchestrator(
                                st.session_state.config,
                                st.session_state.db
                            )
                            
                            manager.disconnect()
                            st.success("✅ Connection successful! Credentials saved.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Connection failed. Please check your credentials.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("Please provide both email and password")
    
    st.markdown("---")
    st.markdown("### Application Settings")
    
    with st.form("app_settings_form"):
        max_emails = st.number_input(
            "Max Emails per Scan",
            min_value=10,
            max_value=1000,
            value=st.session_state.config.max_emails_per_scan,
            help="Maximum number of emails to scan in one operation"
        )
        
        link_delay = st.slider(
            "Delay Between Link Clicks (seconds)",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.config.link_click_delay,
            step=0.5,
            help="Delay between clicking unsubscribe links"
        )
        
        if st.form_submit_button("Save Settings"):
            os.environ["MAX_EMAILS_PER_SCAN"] = str(max_emails)
            os.environ["LINK_CLICK_DELAY"] = str(link_delay)
            st.success("Settings saved!")
    
    st.markdown("---")
    st.markdown("### Security Information")
    st.info("""
    **Important Security Notes:**
    - Use an App-Specific Password, not your regular Gmail password
    - Enable 2-Factor Authentication on your Google Account
    - Never share your credentials
    - Credentials are stored only in memory during the session
    
    **To create an App-Specific Password:**
    1. Go to your Google Account settings
    2. Navigate to Security → 2-Step Verification
    3. Scroll to "App passwords"
    4. Generate a new password for "Mail"
    5. Use that password here
    """)


def dashboard_page():
    """Main dashboard page"""
    st.markdown('<p class="main-header">📊 Dashboard</p>', unsafe_allow_html=True)
    
    if not st.session_state.credentials_verified:
        st.warning("⚠️ Please configure your credentials in the Settings page first.")
        return
    
    # Get statistics
    stats = st.session_state.orchestrator.get_statistics()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Emails Processed", stats.get("total_processed", 0))
    
    with col2:
        st.metric("Emails with Links", stats.get("emails_with_links", 0))
    
    with col3:
        st.metric("Links Clicked", stats.get("links_clicked", 0))
    
    with col4:
        st.metric("Successful Clicks", stats.get("successful_clicks", 0))
    
    # Success rate
    if stats.get("links_clicked", 0) > 0:
        success_rate = (stats.get("successful_clicks", 0) / stats["links_clicked"]) * 100
        st.progress(success_rate / 100)
        st.write(f"Success Rate: {success_rate:.1f}%")
    
    st.markdown("---")
    
    # Category breakdown
    st.markdown("### 📂 Email Categories")
    category_breakdown = stats.get("category_breakdown", {})
    
    if category_breakdown:
        df = pd.DataFrame([
            {"Category": cat, "Count": count}
            for cat, count in category_breakdown.items()
        ])
        st.bar_chart(df.set_index("Category"))
    else:
        st.info("No emails categorized yet. Run a scan to see category breakdown.")
    
    st.markdown("---")
    
    # Recent operations
    st.markdown("### 📜 Recent Operations")
    recent_ops = st.session_state.orchestrator.get_recent_operations(10)
    
    if recent_ops:
        df = pd.DataFrame(recent_ops)
        df = df[["timestamp", "operation_type", "status", "details"]]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No operations yet")


def email_scanner_page():
    """Email scanner page"""
    st.markdown('<p class="main-header">🔍 Email Scanner</p>', unsafe_allow_html=True)
    
    if not st.session_state.credentials_verified:
        st.warning("⚠️ Please configure your credentials in the Settings page first.")
        return
    
    st.markdown("### Scan Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        max_emails = st.slider(
            "Number of emails to scan",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        scan_button = st.button("🔍 Start Scan", type="primary", use_container_width=True)
    
    if scan_button:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(current, total):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Processing email {current} of {total}...")
        
        with st.spinner("Scanning emails..."):
            results = st.session_state.orchestrator.scan_emails(
                max_emails=max_emails,
                progress_callback=progress_callback
            )
            st.session_state.scan_results = results
        
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        st.success("✅ Scan complete!")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Scanned", results["total_scanned"])
        with col2:
            st.metric("With Unsubscribe Links", results["emails_with_links"])
        with col3:
            st.metric("Total Links Found", results["total_links_found"])
        with col4:
            st.metric("Errors", results["errors"])
        
        # Show processed emails
        if results["emails_processed"]:
            st.markdown("### 📧 Processed Emails")
            df = pd.DataFrame(results["emails_processed"])
            st.dataframe(df, use_container_width=True)


def unsubscribe_manager_page():
    """Unsubscribe management page"""
    st.markdown('<p class="main-header">✉️ Unsubscribe Manager</p>', unsafe_allow_html=True)
    
    if not st.session_state.credentials_verified:
        st.warning("⚠️ Please configure your credentials in the Settings page first.")
        return
    
    # Get unclicked links
    conn = st.session_state.db.connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ul.id, ul.link, e.sender, e.subject, e.category, ul.created_at
        FROM unsubscribe_links ul
        JOIN emails e ON ul.email_id = e.id
        WHERE ul.clicked = 0
        ORDER BY ul.created_at DESC
    """)
    
    unclicked_links = [dict(zip([col[0] for col in cursor.description], row)) 
                       for row in cursor.fetchall()]
    
    if not unclicked_links:
        st.info("📭 No pending unsubscribe links. Run a scan to find more!")
        return
    
    st.markdown(f"### Found {len(unclicked_links)} pending unsubscribe links")
    
    # Display as DataFrame with selection
    df = pd.DataFrame(unclicked_links)
    df['select'] = False
    
    # Display table
    st.markdown("#### Select Links to Unsubscribe")
    
    # Category filter
    categories = df['category'].unique().tolist()
    selected_categories = st.multiselect(
        "Filter by category",
        categories,
        default=categories
    )
    
    filtered_df = df[df['category'].isin(selected_categories)]
    
    # Display emails with checkboxes
    if len(filtered_df) > 0:
        for idx, row in filtered_df.iterrows():
            col1, col2 = st.columns([1, 10])
            with col1:
                selected = st.checkbox(f"Select {idx}", key=f"link_{row['id']}", label_visibility="collapsed")
            with col2:
                st.markdown(f"""
                **{row['sender']}** - {row['subject']}  
                Category: `{row['category']}` | Link: {row['link'][:60]}...
                """)
            
            if selected:
                if 'selected_links' not in st.session_state:
                    st.session_state.selected_links = []
                if row['id'] not in st.session_state.selected_links:
                    st.session_state.selected_links.append(row['id'])
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("✅ Unsubscribe Selected", type="primary"):
                if 'selected_links' in st.session_state and st.session_state.selected_links:
                    with st.spinner("Unsubscribing..."):
                        results = st.session_state.orchestrator.unsubscribe_from_links(
                            st.session_state.selected_links
                        )
                    
                    st.success(f"✅ Attempted: {results['total_attempted']}, Success: {results['successful']}, Failed: {results['failed']}")
                    st.session_state.selected_links = []
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning("Please select at least one link")
        
        with col2:
            if st.button("🔄 Unsubscribe All", type="secondary"):
                if st.checkbox("I confirm I want to unsubscribe from all links"):
                    with st.spinner("Unsubscribing from all links..."):
                        link_ids = filtered_df['id'].tolist()
                        results = st.session_state.orchestrator.unsubscribe_from_links(link_ids)
                    
                    st.success(f"✅ Attempted: {results['total_attempted']}, Success: {results['successful']}, Failed: {results['failed']}")
                    time.sleep(2)
                    st.rerun()
    else:
        st.info("No links match the selected filters")


def whitelist_blacklist_page():
    """Whitelist and blacklist management page"""
    st.markdown('<p class="main-header">🛡️ Whitelist & Blacklist</p>', unsafe_allow_html=True)
    
    if not st.session_state.credentials_verified:
        st.warning("⚠️ Please configure your credentials in the Settings page first.")
        return
    
    tab1, tab2 = st.tabs(["✅ Whitelist", "🚫 Blacklist"])
    
    with tab1:
        st.markdown("### Whitelist")
        st.info("Emails matching these patterns will be IGNORED during scanning")
        
        # Add to whitelist
        with st.form("add_whitelist"):
            col1, col2 = st.columns([3, 1])
            with col1:
                pattern = st.text_input("Email pattern (e.g., *@example.com, important@*)")
                notes = st.text_input("Notes (optional)")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Add", use_container_width=True):
                    if pattern:
                        if st.session_state.db.add_to_whitelist(pattern, notes):
                            st.success("Added to whitelist")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Pattern already exists")
        
        # Display whitelist
        whitelist = st.session_state.db.get_whitelist()
        if whitelist:
            for item in whitelist:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{item['email_pattern']}**")
                    if item['notes']:
                        st.caption(item['notes'])
                with col2:
                    if st.button("Remove", key=f"wl_{item['id']}"):
                        st.session_state.db.remove_from_whitelist(item['id'])
                        st.rerun()
        else:
            st.info("No whitelist entries")
    
    with tab2:
        st.markdown("### Blacklist")
        st.info("Emails matching these patterns will be PRIORITIZED for unsubscribing")
        
        # Add to blacklist
        with st.form("add_blacklist"):
            col1, col2 = st.columns([3, 1])
            with col1:
                pattern = st.text_input("Email pattern (e.g., *@spam.com, newsletter@*)")
                notes = st.text_input("Notes (optional)")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Add", use_container_width=True):
                    if pattern:
                        if st.session_state.db.add_to_blacklist(pattern, notes):
                            st.success("Added to blacklist")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Pattern already exists")
        
        # Display blacklist
        blacklist = st.session_state.db.get_blacklist()
        if blacklist:
            for item in blacklist:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{item['email_pattern']}**")
                    if item['notes']:
                        st.caption(item['notes'])
                with col2:
                    if st.button("Remove", key=f"bl_{item['id']}"):
                        st.session_state.db.remove_from_blacklist(item['id'])
                        st.rerun()
        else:
            st.info("No blacklist entries")


def statistics_page():
    """Statistics and analytics page"""
    st.markdown('<p class="main-header">📈 Statistics & Analytics</p>', unsafe_allow_html=True)
    
    if not st.session_state.credentials_verified:
        st.warning("⚠️ Please configure your credentials in the Settings page first.")
        return
    
    stats = st.session_state.orchestrator.get_statistics()
    
    # Overall stats
    st.markdown("### 📊 Overall Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Emails Processed", stats.get("total_processed", 0))
        st.metric("Emails with Links", stats.get("emails_with_links", 0))
    
    with col2:
        st.metric("Total Links Clicked", stats.get("links_clicked", 0))
        st.metric("Successful Clicks", stats.get("successful_clicks", 0))
    
    with col3:
        if stats.get("links_clicked", 0) > 0:
            success_rate = (stats.get("successful_clicks", 0) / stats["links_clicked"]) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Success Rate", "N/A")
    
    st.markdown("---")
    
    # Category breakdown
    st.markdown("### 📂 Email Categories")
    category_breakdown = stats.get("category_breakdown", {})
    
    if category_breakdown:
        df = pd.DataFrame([
            {"Category": cat, "Count": count}
            for cat, count in category_breakdown.items()
        ])
        st.bar_chart(df.set_index("Category"))
    else:
        st.info("No data available yet")
    
    st.markdown("---")
    
    # Export functionality
    st.markdown("### 💾 Export Data")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📥 Export Links"):
            filename = f"unsubscribe_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            if st.session_state.orchestrator.export_links(filename):
                st.success(f"Links exported to {filename}")
            else:
                st.error("Failed to export links")


def operation_history_page():
    """Operation history page"""
    st.markdown('<p class="main-header">📜 Operation History</p>', unsafe_allow_html=True)
    
    if not st.session_state.credentials_verified:
        st.warning("⚠️ Please configure your credentials in the Settings page first.")
        return
    
    limit = st.slider("Number of operations to show", 10, 200, 50)
    
    operations = st.session_state.orchestrator.get_recent_operations(limit)
    
    if operations:
        df = pd.DataFrame(operations)
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            operation_types = df['operation_type'].unique().tolist()
            selected_types = st.multiselect("Filter by operation type", operation_types, default=operation_types)
        
        with col2:
            statuses = df['status'].unique().tolist()
            selected_statuses = st.multiselect("Filter by status", statuses, default=statuses)
        
        # Filter dataframe
        filtered_df = df[
            (df['operation_type'].isin(selected_types)) &
            (df['status'].isin(selected_statuses))
        ]
        
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No operations recorded yet")


def main():
    """Main application"""
    initialize_session_state()
    
    # Sidebar navigation
    page = sidebar_navigation()
    
    # Route to appropriate page
    if page == "Dashboard":
        dashboard_page()
    elif page == "Email Scanner":
        email_scanner_page()
    elif page == "Unsubscribe Manager":
        unsubscribe_manager_page()
    elif page == "Whitelist/Blacklist":
        whitelist_blacklist_page()
    elif page == "Settings":
        settings_page()
    elif page == "Statistics":
        statistics_page()
    elif page == "Operation History":
        operation_history_page()


if __name__ == "__main__":
    # Setup logging
    setup_logging("INFO", "logs/app.log")
    
    # Run app
    main()
