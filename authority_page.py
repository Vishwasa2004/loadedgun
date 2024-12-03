import streamlit as st
import pandas as pd
import datetime
from utils import load_issue_tickets, save_issue_ticket

def authority_interface():
    st.title("Authority Page")
    st.header("Manage Issue Tickets")

    # Load tickets
    issue_tickets = load_issue_tickets()

    if issue_tickets:
        df_tickets = pd.DataFrame(issue_tickets)

        # Display open tickets
        open_tickets = [ticket for ticket in issue_tickets if ticket["status"] == "Open"]
        st.subheader("Open Tickets")
        if open_tickets:
            st.dataframe(pd.DataFrame(open_tickets))
        else:
            st.info("No open tickets to display.")

        # Filter overdue tickets
        overdue_tickets = []
        for ticket in open_tickets:
            try:
                ticket_date = datetime.datetime.fromisoformat(ticket["date"])
                days_since_report = (datetime.datetime.now() - ticket_date).days

                if days_since_report > 7:  # Add overdue condition
                    overdue_tickets.append(ticket)
            except ValueError:
                st.error(f"Invalid date format in ticket: {ticket}")

        if overdue_tickets:
            st.subheader("Overdue Tickets")
            st.warning(f"There are {len(overdue_tickets)} overdue tickets!")
            st.dataframe(pd.DataFrame(overdue_tickets))

        # Manage a selected ticket
        if open_tickets:
            ticket_index = st.selectbox("Select a Ticket to Manage", range(len(open_tickets)), format_func=lambda x: open_tickets[x]["title"])
            selected_ticket = open_tickets[ticket_index]

            st.subheader("Ticket Details")
            st.json(selected_ticket)

            # Resolve or take action
            if st.button("Mark as Resolved"):
                issue_tickets[ticket_index]["status"] = "Resolved"
                save_issue_ticket(issue_tickets)
                st.success("Ticket marked as resolved!")

                # Simulate rerun by setting a query parameter
                st.experimental_set_query_params(rerun="true")
        else:
            st.warning("No tickets available for management.")
    else:
        st.info("No tickets to display.")

    # Check and handle rerun
    params = st.experimental_get_query_params()
    if "rerun" in params:
        st.experimental_set_query_params()  # Clear query params
        st.experimental_rerun()

try:
    st.experimental_rerun()
except AttributeError:
    st.stop()  # Alternative to rerun the script
